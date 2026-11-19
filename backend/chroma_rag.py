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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

class ChromaRAGService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
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

    def index_document(self, doc_id: str, file_path: str, category: str, original_filename: str) -> int:
        """
        Extracts, embeds, and registers PDF chunks into ChromaDB.
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

    def generate_exam_strategy(self, exam_name: str, daily_hours: float, prep_level: str) -> str:
        """
        Generates a comprehensive, structured study strategy using Gemini with syllabus breakdown,
        timeline, daily timetable, and revision cycles.
        """
        if not self.is_configured():
            return (
                f"# Strategic Preparation Blueprint: {exam_name}\n\n"
                f"**Target Exam:** {exam_name} | **Daily Commitment:** {daily_hours} hrs/day | **Level:** {prep_level}\n\n"
                f"### Phase 1: Core Foundation & Theoretical Mastery (Weeks 1–6)\n"
                f"- Focus on high-yield syllabus modules, standard university textbooks, and foundational concepts.\n"
                f"- Dedicate {max(1.5, daily_hours * 0.4):.1f} hours daily to technical/specialist topics.\n\n"
                f"### Phase 2: High-Volume Question Bank & Mock Practice (Weeks 7–10)\n"
                f"- Solve minimum 50–70 sectional MCQs per day.\n"
                f"- Analyze previous year question trends and common distractors.\n\n"
                f"### Phase 3: Simulated Exam Mocks & Rapid Formula Revision (Weeks 11–12)\n"
                f"- Take full-length timed mock tests in exact exam slots.\n"
                f"- Consolidate concise handwritten formula sheets and error logs."
            )

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
            return f"# Strategy Blueprint for {exam_name}\n\nFailed to generate online strategy ({e}). Please review standard curriculum guides."

    def answer_rag_query(self, query: str, doc_id: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes hybrid vector retrieval in ChromaDB and generates an answer with source citations.
        Supports single-document focus or category-wide search.
        """
        query_vec = self.get_embedding(query)
        
        # Build ChromaDB where filter
        where_filter = None
        if doc_id:
            where_filter = {"doc_id": doc_id}
        elif category and category != "all":
            where_filter = {"category": category}

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
            return {
                "answer": f"Encountered an issue generating response ({e}). Relevant text: {retrieved_docs[0] if retrieved_docs else 'None'}",
                "sources": sources,
                "model": "error-fallback"
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
            return {"answer": f"Mentor guidance fallback: {e}", "sources": [], "model": "error-fallback"}

# Singleton instance
rag_service = ChromaRAGService()
