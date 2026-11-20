"""
ChromaDB Vector Store & Google Gemini RAG Engine with Exponential Backoff
"""
import os
import re
import time
import math
import random
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
import pypdf
from google import genai
from google.genai import types
from google.genai.errors import APIError

os.environ["ANONYMIZED_TELEMETRY"] = "False"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

class ChromaRAGService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=Settings(anonymized_telemetry=False, is_persistent=True)
        )
        self.collection_name = "gov_exam_rag_docs"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Government Exam Preparation PDF Chunks"}
        )
        
        self.embedding_model = "text-embedding-004"
        self.candidate_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
        self.active_chat_model = self.candidate_models[0]
        self._load_client()

    def _load_client(self):
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key:
            try:
                self.genai_client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[RAG] Warning: genai.Client init failed: {e}")
                self.genai_client = None
        else:
            self.genai_client = None

    def is_configured(self) -> bool:
        return self.genai_client is not None

    def _call_with_retry_and_fallback(self, func, *args, **kwargs):
        """
        Executes a Gemini API call with exponential backoff and automatic model fallback
        for 503 UNAVAILABLE, 429 RATE_LIMIT, or temporary server issues.
        """
        max_retries = 3
        backoff = 1.5

        for model_name in self.candidate_models:
            self.active_chat_model = model_name
            for attempt in range(max_retries):
                try:
                    return func(model_name, *args, **kwargs)
                except Exception as e:
                    err_str = str(e).lower()
                    is_transient = any(x in err_str for x in ["503", "unavailable", "429", "quota", "resource_exhausted", "timeout"])
                    if is_transient and attempt < max_retries - 1:
                        sleep_time = (backoff ** attempt) + random.uniform(0.2, 0.5)
                        print(f"[RAG] Transient error '{e}' on model {model_name}. Retrying in {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                    else:
                        print(f"[RAG] Model {model_name} failed with error: {e}. Attempting next candidate model...")
                        break  # Try next model in candidate_models list

        raise RuntimeError("All Gemini candidate models and retries were exhausted.")

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates 768-dim float embedding using text-embedding-004 with fallback.
        """
        if self.genai_client:
            try:
                res = self.genai_client.models.embed_content(
                    model=self.embedding_model,
                    contents=text[:2000]
                )
                if hasattr(res, 'embedding') and hasattr(res.embedding, 'values'):
                    return list(res.embedding.values)
                elif hasattr(res, 'embeddings') and res.embeddings:
                    return list(res.embeddings[0].values)
            except Exception as e:
                print(f"[RAG] Warning: Remote embedding API call failed ({e}). Using deterministic pseudo-vector.")

        # Deterministic 768-dim pseudo vector for offline / rate-limit resilience
        import hashlib
        vec = [0.0] * 768
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        for w in words:
            h = int(hashlib.md5(w.encode()).hexdigest(), 16)
            idx = h % 768
            vec[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def extract_and_chunk_pdf(self, file_path: str, chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF and splits into chunks preserving page numbers.
        """
        reader = pypdf.PdfReader(file_path)
        chunks = []
        chunk_idx = 0

        for page_num, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            
            cleaned = re.sub(r'\s+', ' ', page_text).strip()
            if not cleaned:
                continue

            # Sliding window chunking
            start = 0
            while start < len(cleaned):
                end = min(start + chunk_size, len(cleaned))
                chunk_str = cleaned[start:end].strip()
                if len(chunk_str) > 60:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "text": chunk_str
                    })
                    chunk_idx += 1
                start += (chunk_size - overlap)

        return chunks

    def index_document(self, doc_id: str, file_path: str, category: str, original_filename: str, user_id: str = "default_user") -> int:
        """
        Extracts, embeds, and registers PDF chunks into ChromaDB with user isolation.
        """
        chunks = self.extract_and_chunk_pdf(file_path)
        if not chunks:
            return 0

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for c in chunks:
            c_id = f"{doc_id}_{c['chunk_index']}"
            vec = self.get_embedding(c['text'])
            ids.append(c_id)
            embeddings.append(vec)
            documents.append(c['text'])
            metadatas.append({
                "doc_id": doc_id,
                "user_id": user_id,
                "page_number": c["page_number"],
                "category": category,
                "filename": original_filename
            })

        # Batch upsert into ChromaDB
        batch_size = 50
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

        return len(chunks)

    def delete_document_vectors(self, doc_id: str):
        """
        Purges all chunks belonging to a document from ChromaDB.
        """
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"[RAG] Warning deleting ChromaDB vectors for {doc_id}: {e}")

    def generate_quick_summary(self, file_path: str, filename: str, category: str) -> str:
        """
        Generates an AI summary of the uploaded document with key topics and syllabus alignment.
        """
        chunks = self.extract_and_chunk_pdf(file_path, chunk_size=1000, overlap=0)
        sample_text = "\n\n".join([f"[Page {c['page_number']}] {c['text']}" for c in chunks[:5]])

        if not sample_text:
            return f"Document '{filename}' uploaded under category '{category}'. Contains technical study material."

        if not self.is_configured():
            return (
                f"**Overview:** Study resource '{filename}' categorised as *{category}*.\n"
                f"- High-yield resource covering key examination concepts.\n"
                f"- Comprehensive reference for self-study and revision."
            )

        prompt = (
            f"You are a senior exam mentor for Indian competitive exams (SEBI, SBI, IBPS, UPSC, SSC).\n"
            f"Analyze the following initial pages of the uploaded document '{filename}' (Category: {category}):\n\n"
            f"{sample_text}\n\n"
            f"Provide a concise, 3-4 bullet point summary in markdown highlighting:\n"
            f"1. Core Subject Matter & Topics Covered\n"
            f"2. Exam Relevance & Target Sections\n"
            f"3. Suggested Study Approach (e.g., theory reading vs. MCQ practice)\n"
            f"Keep it crisp, scholarly, and student-friendly."
        )

        def _do_summary(model_name: str) -> str:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text

        try:
            return self._call_with_retry_and_fallback(_do_summary)
        except Exception as e:
            return f"Overview for {filename}: High-yield technical document for {category}. (Auto-summary fallback: {e})"

    def _build_rich_strategy_blueprint(self, exam_name: str, daily_hours: float, prep_level: str, api_error_note: Optional[str] = None) -> str:
        """
        Comprehensive built-in blueprint generator with exam patterns, subject breakdowns,
        daily hourly schedules, and high-yield topics.
        """
        hours = float(daily_hours)
        tech_hrs = round(hours * 0.55, 1)
        mcq_hrs = round(hours * 0.25, 1)
        rev_hrs = round(max(0.5, hours - tech_hrs - mcq_hrs), 1)

        alert_banner = ""
        if api_error_note:
            alert_banner = (
                f"> 💡 **Exam Mentor Notice:** *{api_error_note}*\n"
                f"> *This blueprint has been synthesized using our comprehensive offline exam pattern & curriculum knowledge base.*\n\n"
            )

        return (
            f"{alert_banner}# 🎯 Strategic Preparation Blueprint: {exam_name}\n\n"
            f"**Aspirant Target:** {exam_name} | **Daily Time Budget:** {daily_hours} hrs/day | **Initial Prep Level:** {prep_level}\n\n"
            f"---\n\n"
            f"### 1. Executive Strategy & Exam Architecture\n"
            f"For competitive examinations like **{exam_name}**, preparation must balance theoretical depth with sectional speed and accuracy under negative marking:\n"
            f"- **Core Screening Filters:** Prelims / Phase 1 focuses heavily on speed-based Aptitude, English, and General Awareness, along with technical screening.\n"
            f"- **Decisive Selection Merit:** The Mains / Phase 2 Specialist Paper (covering DBMS, Networking, OS, DSA, System Design, and Cyber Security) determines your final merit ranking.\n\n"
            f"### 2. Daily Hourly Architecture ({daily_hours} Hours Total)\n"
            f"- **Block A: Specialist Technical Domain ({tech_hrs} hrs)**\n"
            f"  - Deep conceptual textbook reading and architecture diagrams.\n"
            f"  - Handwritten summary of primary formulas, protocols, and standard SQL patterns.\n"
            f"- **Block B: Question Bank & Timed MCQs ({mcq_hrs} hrs)**\n"
            f"  - Active recall: Solve 40–60 topic-wise MCQs daily.\n"
            f"  - Maintain an 'Error Logbook' of incorrect options and distractor traps.\n"
            f"- **Block C: Rapid Recall & Revision ({rev_hrs} hrs)**\n"
            f"  - Spaced repetition of previously studied chapters.\n"
            f"  - Daily review of flashcards, ACID transaction rules, and subnet masks.\n\n"
            f"### 3. Phase-by-Phase Roadmap\n\n"
            f"#### 📅 Phase 1: Core Foundation & Theoretical Mastery (Weeks 1–6)\n"
            f"- **DBMS & Advanced SQL:** ER modeling, Relational Algebra, Functional Dependencies, 1NF to BCNF, Serializability, MVCC, and complex analytical SQL joins.\n"
            f"- **Operating Systems & Systems Engineering:** Process scheduling, Deadlock prevention (Banker's Algorithm), Virtual Memory, and Paging mechanics.\n"
            f"- **Computer Networks:** OSI 7-Layer vs. TCP/IP, CIDR subnetting, TCP 3-way handshake, sliding window protocols, and TLS/HTTPS security.\n\n"
            f"#### 📅 Phase 2: High-Volume Question Bank & Sectional Drilling (Weeks 7–10)\n"
            f"- Work through uploaded Question Bank PDFs in the platform library.\n"
            f"- Drill high-weightage topics: Data Structures (Trees, Graphs, Sorting complexity), Software Engineering (SDLC, Design Patterns), and Cloud / Cyber Security regulations.\n"
            f"- Weekly sectional timed tests to build rapid question elimination technique.\n\n"
            f"#### 📅 Phase 3: Simulated Mocks & Final Revision Cycles (Weeks 11–12)\n"
            f"- Full-length 100-question timed mock tests in identical exam slots.\n"
            f"- Strict target: >75% accuracy with zero unforced negative marks.\n"
            f"- Formula sheets, port numbers, and protocol cheat sheets revision only.\n\n"
            f"### 4. High-Yield Pitfalls to Avoid\n"
            f"1. **Passive Reading Trap:** Do not read PDFs passively. Always test understanding using the quiz module and question bank immediately after reading.\n"
            f"2. **Neglecting Non-Tech Cutoffs:** In banking/regulatory exams, scoring 0.25 below sectional cutoffs in English or Reasoning will invalidate high technical scores.\n"
            f"3. **Ignoring Negative Marking:** Use intelligent elimination; avoid guessing when more than two distractors seem plausible."
        )

    def generate_exam_strategy(self, exam_name: str, daily_hours: float, prep_level: str) -> str:
        """
        Generates a comprehensive, structured study strategy using Gemini with syllabus breakdown,
        timeline, daily timetable, and revision cycles.
        """
        if not self.is_configured():
            return self._build_rich_strategy_blueprint(exam_name, daily_hours, prep_level)

        prompt = (
            f"You are an expert exam strategist and faculty mentor for Indian Government and Banking examinations "
            f"(such as {exam_name}, UPSC CSE, SSC CGL, SEBI Grade A, IBPS SO, SBI SCO).\n\n"
            f"Develop an actionable, high-yield preparation blueprint for an aspirant with:\n"
            f"- **Target Exam:** {exam_name}\n"
            f"- **Daily Study Hours:** {daily_hours} hours\n"
            f"- **Preparation Level:** {prep_level}\n\n"
            f"Structure your response strictly in Markdown with clear typography:\n"
            f"1. **Executive Strategy & Exam Pattern Overview** (Weightage, key filters)\n"
            f"2. **Daily Routine & Time-Block Architecture** (Balancing conceptual reading, revision & MCQ practice)\n"
            f"3. **Phase-by-Phase Roadmap** (Phase 1: Foundation, Phase 2: Question Banks, Phase 3: Final Mocks)\n"
            f"4. **Subject Priorities & Must-Read References**\n"
            f"5. **High-Yield Pitfalls & Accuracy Tips**"
        )

        def _do_strategy(model_name: str) -> str:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text

        try:
            return self._call_with_retry_and_fallback(_do_strategy)
        except Exception as e:
            err_msg = str(e)
            user_note = "Your Google Gemini API Key was reported as leaked/invalid by Google AI Studio. Update with a fresh key to enable live cloud generation." if "leaked" in err_msg.lower() or "403" in err_msg else f"API Notice: {err_msg}"
            return self._build_rich_strategy_blueprint(exam_name, daily_hours, prep_level, api_error_note=user_note)

    def answer_rag_query(self, query: str, doc_id: Optional[str] = None, category: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes hybrid vector retrieval in ChromaDB and generates an answer with source citations.
        Supports single-document focus or user/category-scoped search.
        """
        query_vec = self.get_embedding(query)
        
        # Build ChromaDB where filter with user isolation
        where_filter = None
        if doc_id:
            where_filter = {"doc_id": doc_id}
        elif category and category != "all" and user_id:
            where_filter = {"$and": [{"user_id": user_id}, {"category": category}]}
        elif category and category != "all":
            where_filter = {"category": category}
        elif user_id:
            where_filter = {"user_id": user_id}

        query_args = {
            "query_embeddings": [query_vec],
            "n_results": 5
        }
        if where_filter:
            query_args["where"] = where_filter

        try:
            results = self.collection.query(**query_args)
        except Exception as e:
            print(f"[RAG] ChromaDB query error: {e}")
            results = {"documents": [[]], "metadatas": [[]]}

        retrieved_docs = results.get("documents", [[]])[0]
        retrieved_meta = results.get("metadatas", [[]])[0]

        sources = []
        context_blocks = []
        for doc_text, meta in zip(retrieved_docs, retrieved_meta):
            fn = meta.get("filename", "Document")
            pg = meta.get("page_number", 1)
            d_id = meta.get("doc_id", "")
            sources.append({
                "filename": fn,
                "page": pg,
                "document_id": d_id
            })
            context_blocks.append(f"Source: {fn} (Page {pg}):\n{doc_text}")

        context_text = "\n\n---\n\n".join(context_blocks)

        if not self.is_configured():
            # Heuristic offline answer
            if not context_blocks:
                return {
                    "answer": f"I could not locate specific matches for '{query}' in the uploaded documents. Please try rephrasing or asking a question related to database normalization, networking, or SQL.",
                    "sources": [],
                    "model": "offline-fallback"
                }
            return {
                "answer": (
                    f"Based on the relevant documents (**{sources[0]['filename']}**, Page {sources[0]['page']}):\n\n"
                    f"{retrieved_docs[0][:400]}...\n\n"
                    f"*(Note: Google Gemini API key is currently running in offline fallback mode. Configure API key for deep generative synthesis).* "
                ),
                "sources": sources,
                "model": "offline-fallback"
            }

        prompt = (
            f"You are an expert AI Tutor and Exam Faculty Mentor for Indian Government and Banking exams.\n"
            f"A student is asking the following question:\n\n"
            f"Student Question: {query}\n\n"
            f"Examine the following extracted PDF excerpts carefully:\n"
            f"{context_text if context_text else 'No specific document excerpts matched.'}\n\n"
            f"Instructions:\n"
            f"- If relevant context is provided above, explain the answer comprehensively, citing specific source documents and page numbers (e.g. '[{sources[0]['filename'] if sources else 'Doc'}, Page X]').\n"
            f"- If the context does not fully answer the question, supplement with accurate, standard technical knowledge for competitive exams, stating clearly what comes from the text and what is standard syllabus doctrine.\n"
            f"- Use clean Markdown, bold headers, and concise bullet points."
        )

        def _do_chat(model_name: str) -> str:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text

        try:
            answer = self._call_with_retry_and_fallback(_do_chat)
            return {
                "answer": answer,
                "sources": sources,
                "model": self.active_chat_model
            }
        except Exception as e:
            fallback_body = (
                f"**Extracted Reference Excerpt ({sources[0]['filename']}, Page {sources[0]['page']}):**\n\n"
                f"{retrieved_docs[0]}\n\n"
                f"> 💡 *Notice: Cloud generation experienced an API issue ({e}). Displaying exact semantic excerpt retrieved from ChromaDB.*"
                if retrieved_docs else
                f"I could not locate specific matches for '{query}' in the indexed documents."
            )
            return {
                "answer": fallback_body,
                "sources": sources,
                "model": "offline-vector-match"
            }

    def answer_general_mentor_query(self, query: str) -> Dict[str, Any]:
        """
        General Mode: Exam mentor answering syllabus, current affairs, doubts, and strategy.
        """
        if not self.is_configured():
            return {
                "answer": (
                    f"**General Exam Mentor:** Addressing '{query}'.\n\n"
                    f"For government and banking exams (SEBI, SBI SCO, IBPS SO, UPSC, SSC), consistency in daily practice and syllabus mapping are paramount. "
                    f"Focus on the official notifications, high-weightage sections, and sectional mock tests."
                ),
                "sources": [],
                "model": "general-offline"
            }

        prompt = (
            f"You are a senior faculty mentor for Indian Government and Competitive Exams (UPSC CSE, SSC CGL, Banking Exams, Railways, State PSCs).\n"
            f"Answer the aspirant's query thoughtfully, clearly, and authoritatively:\n\n"
            f"Query: {query}\n\n"
            f"Provide actionable advice, syllabus clarity, or technical explanations formatted in clean Markdown."
        )

        def _do_mentor(model_name: str) -> str:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text

        try:
            ans = self._call_with_retry_and_fallback(_do_mentor)
            return {"answer": ans, "sources": [], "model": self.active_chat_model}
        except Exception as e:
            return {
                "answer": (
                    f"**Faculty Mentor Insights on '{query}':**\n\n"
                    f"1. **Syllabus & Weightage Alignment:** Prioritize high-scoring modules first (e.g. DBMS, Networking, OS, and Data Structures for IT officer exams; History, Polity, Geography for General exams).\n"
                    f"2. **Daily Routine:** Maintain a 60/40 ratio between theoretical study and active MCQ practice under timed conditions.\n"
                    f"3. **Error Analysis:** Thoroughly analyze every incorrect option in your mock tests to avoid repeating conceptual traps.\n\n"
                    f"> 💡 *Notice: To enable live cloud Gemini mentoring responses, update your API key in Settings or `.env`.*"
                ),
                "sources": [],
                "model": "offline-curriculum-mentor"
            }

# Singleton instance
rag_service = ChromaRAGService()
