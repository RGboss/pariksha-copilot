"""
ChromaDB Vector Store & Google Gemini RAG Engine with Advanced PDF Analysis,
Model Selection, and Token-Optimized Context Retrieval
"""
import os
import re
import time
import math
import json
import random
import hashlib
from typing import List, Dict, Any, Optional, Tuple

import chromadb
from chromadb.config import Settings
import pypdf
from google import genai
from google.genai import types
from google.genai.errors import APIError

os.environ["ANONYMIZED_TELEMETRY"] = "False"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", os.path.join(DATA_DIR, "chroma_db"))
os.makedirs(CHROMA_DIR, exist_ok=True)

def compute_file_hash(file_path: str) -> str:
    """Computes SHA-256 hash of a file for deduplication."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

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
        self.candidate_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        self.active_chat_model = self.candidate_models[0]
        self.embedding_api_available = True
        self._load_client()

    def _load_client(self):
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key:
            try:
                self.genai_client = genai.Client(api_key=api_key)
                self.embedding_api_available = True
            except Exception as e:
                print(f"[RAG] Warning: genai.Client init failed: {e}")
                self.genai_client = None
                self.embedding_api_available = False
        else:
            self.genai_client = None
            self.embedding_api_available = False

    def is_configured(self) -> bool:
        return self.genai_client is not None

    def get_supported_models(self) -> List[Dict[str, Any]]:
        """Returns catalog of supported AI models with token efficiency info."""
        return [
            {
                "id": "gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "tag": "Fast & Recommended",
                "description": "High-velocity inference, optimal token economics, and sharp reasoning for syllabus & chapter inquiries.",
                "token_efficiency": "High (Balanced)",
                "badge": "Recommended"
            },
            {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "tag": "Deep Analytical Reasoning",
                "description": "Comprehensive multi-step thinking for nuanced exam pattern breakdowns and complex problem solving.",
                "token_efficiency": "Standard (Deep Context)",
                "badge": "Deep Thinker"
            },
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "tag": "Ultra-Low Latency",
                "description": "Fastest token generation with minimal context overhead, ideal for quick concept checks.",
                "token_efficiency": "Very High",
                "badge": "Instant"
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "tag": "Large Context Window",
                "description": "High precision across lengthy document sections and extensive revision notes.",
                "token_efficiency": "Standard",
                "badge": "Long-Form"
            },
            {
                "id": "offline-curriculum",
                "name": "Offline Curriculum Engine",
                "tag": "Zero Quota / 100% Free",
                "description": "Local deterministic semantic vector search & standard syllabus doctrines without consuming any cloud API tokens.",
                "token_efficiency": "100% Free (0 Tokens)",
                "badge": "Offline"
            }
        ]

    def _call_with_retry_and_fallback(self, func, requested_model: Optional[str] = None, *args, **kwargs):
        """
        Executes a Gemini API call with exponential backoff and automatic model fallback.
        Prioritizes user's requested model if provided.
        """
        max_retries = 3
        backoff = 1.5

        # Arrange candidate models with requested model at front
        candidates = list(self.candidate_models)
        if requested_model and requested_model in candidates:
            candidates.remove(requested_model)
            candidates.insert(0, requested_model)
        elif requested_model and requested_model not in ["offline-curriculum", "offline-fallback"]:
            candidates.insert(0, requested_model)

        for model_name in candidates:
            self.active_chat_model = model_name
            for attempt in range(max_retries):
                try:
                    return func(model_name, *args, **kwargs)
                except Exception as e:
                    err_str = str(e).lower()
                    is_fatal_auth = any(x in err_str for x in ["api_key_invalid", "invalid_argument", "unauthenticated", "permission_denied", "api key not valid", "400 invalid_argument"])
                    if is_fatal_auth:
                        print(f"[RAG] Permanent API key error on {model_name}: {e}. Halting remote retries.")
                        raise e

                    is_transient = any(x in err_str for x in ["503", "unavailable", "429", "quota", "resource_exhausted", "timeout"])
                    if is_transient and attempt < max_retries - 1:
                        sleep_time = (backoff ** attempt) + random.uniform(0.2, 0.5)
                        print(f"[RAG] Transient error '{e}' on model {model_name}. Retrying in {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                    else:
                        print(f"[RAG] Model {model_name} failed with error: {e}. Attempting next candidate...")
                        break

        raise RuntimeError("All Gemini candidate models and retries were exhausted.")

    def _compute_pseudo_vector(self, text: str) -> List[float]:
        """Deterministic 768-dim pseudo vector for offline / rate-limit resilience."""
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

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates 768-dim float embedding using text-embedding-004 with fallback and circuit breaker.
        """
        if self.genai_client and self.embedding_api_available:
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
                err_str = str(e).lower()
                if "api_key_invalid" in err_str or "invalid_argument" in err_str or "permission" in err_str:
                    print(f"[RAG] Permanent embedding API error ({e}). Circuit breaker activated: using offline vectors.")
                    self.embedding_api_available = False
                else:
                    print(f"[RAG] Warning: Remote embedding API call failed ({e}). Using deterministic pseudo-vector.")

        return self._compute_pseudo_vector(text)

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings in efficient batches with automatic fallback.
        """
        if not texts:
            return []

        if not self.genai_client or not self.embedding_api_available:
            return [self._compute_pseudo_vector(t) for t in texts]

        results = []
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            if not self.embedding_api_available or not self.genai_client:
                for t in batch:
                    results.append(self._compute_pseudo_vector(t))
                continue

            trimmed = [t[:2000] for t in batch]
            try:
                res = self.genai_client.models.embed_content(
                    model=self.embedding_model,
                    contents=trimmed
                )
                if hasattr(res, 'embeddings') and res.embeddings:
                    for emb in res.embeddings:
                        results.append(list(emb.values))
                else:
                    for t in batch:
                        results.append(self._compute_pseudo_vector(t))
            except Exception as e:
                err_str = str(e).lower()
                if "api_key_invalid" in err_str or "invalid_argument" in err_str or "permission" in err_str:
                    print(f"[RAG] Permanent embedding API error in batch ({e}). Disabling remote embeddings.")
                    self.embedding_api_available = False
                else:
                    print(f"[RAG] Batch embedding error ({e}). Falling back to local vectors.")
                for t in batch:
                    results.append(self._compute_pseudo_vector(t))

        return results

    def extract_and_chunk_pdf(self, file_path: str, chunk_size: int = 850, overlap: int = 150) -> Dict[str, Any]:
        """
        High-performance PDF text, outline, and table extraction using PyMuPDF (fitz)
        with automatic fallback to pypdf. Preserves headings and semantic paragraph boundaries.
        """
        chunks = []
        toc = []
        total_chars = 0
        page_count = 0

        # Primary extraction engine: PyMuPDF
        try:
            import pymupdf
            doc = pymupdf.open(file_path)
            page_count = len(doc)
            
            # Extract Table of Contents / Book Outline
            try:
                raw_toc = doc.get_toc() or []
                for item in raw_toc:
                    if len(item) >= 3:
                        toc.append({
                            "level": item[0],
                            "title": str(item[1]).strip(),
                            "page": item[2]
                        })
            except Exception:
                pass

            chunk_idx = 0
            current_section = "General Section"

            for page_num in range(1, page_count + 1):
                page = doc[page_num - 1]
                page_text_blocks = []

                # Table extraction
                try:
                    tables = page.find_tables()
                    if tables and tables.tables:
                        for tab in tables.tables:
                            rows = tab.extract()
                            if rows and len(rows) > 1:
                                tbl_md = "\n".join([" | ".join([str(c or "").strip() for c in r]) for r in rows[:15]])
                                page_text_blocks.append(f"[Table on Page {page_num}]\n{tbl_md}")
                except Exception:
                    pass

                # Structural text blocks
                try:
                    blocks = page.get_text("blocks")
                    for b in blocks:
                        if len(b) >= 5 and b[6] == 0:  # Text block
                            text = b[4].strip()
                            if text:
                                # Header detection heuristics
                                first_line = text.split("\n")[0].strip()
                                if len(first_line) < 80 and (
                                    first_line.isupper() or 
                                    re.match(r'^(chapter|section|part|unit|module|stage|\d+\.|\d+\.\d+)\b', first_line, re.IGNORECASE)
                                ):
                                    current_section = first_line
                                page_text_blocks.append(text)
                except Exception:
                    raw_txt = page.get_text() or ""
                    if raw_txt.strip():
                        page_text_blocks.append(raw_txt.strip())

                page_content = "\n\n".join(page_text_blocks)
                page_content = re.sub(r'[\r\t\f\v]', ' ', page_content)
                page_content = re.sub(r' +', ' ', page_content).strip()
                total_chars += len(page_content)

                if not page_content:
                    continue

                # Semantic paragraph chunking
                paragraphs = [p.strip() for p in page_content.split("\n\n") if len(p.strip()) > 25]
                if not paragraphs:
                    paragraphs = [page_content]

                current_chunk = ""
                for p in paragraphs:
                    if len(current_chunk) + len(p) + 2 < chunk_size:
                        current_chunk = f"{current_chunk}\n\n{p}".strip()
                    else:
                        if len(current_chunk) > 60:
                            chunks.append({
                                "chunk_index": chunk_idx,
                                "page_number": page_num,
                                "section_title": current_section,
                                "text": current_chunk
                            })
                            chunk_idx += 1
                        current_chunk = p

                if len(current_chunk) > 60:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "section_title": current_section,
                        "text": current_chunk
                    })
                    chunk_idx += 1

            if not chunks and page_count > 0:
                # Scanned or image-only PDF fallback: create structural reference chunks
                for p in range(1, min(page_count + 1, 6)):
                    chunks.append({
                        "chunk_index": p - 1,
                        "page_number": p,
                        "section_title": f"Page {p}",
                        "text": f"Study material from '{os.path.basename(file_path)}' (Page {p} of {page_count}). Scanned reference page."
                    })

            doc.close()

        except Exception as e:
            print(f"[RAG] PyMuPDF extraction failed ({e}), falling back to pypdf...")
            try:
                reader = pypdf.PdfReader(file_path)
                page_count = len(reader.pages)
                chunk_idx = 0
                for page_num, page in enumerate(reader.pages, start=1):
                    try:
                        p_txt = page.extract_text() or ""
                    except Exception:
                        p_txt = ""
                    cleaned = re.sub(r'\s+', ' ', p_txt).strip()
                    total_chars += len(cleaned)
                    if not cleaned:
                        continue
                    start = 0
                    while start < len(cleaned):
                        end = min(start + chunk_size, len(cleaned))
                        c_str = cleaned[start:end].strip()
                        if len(c_str) > 60:
                            chunks.append({
                                "chunk_index": chunk_idx,
                                "page_number": page_num,
                                "section_title": f"Page {page_num}",
                                "text": c_str
                            })
                            chunk_idx += 1
                        start += (chunk_size - overlap)
            except Exception as e2:
                print(f"[RAG] pypdf fallback also failed ({e2})")

        return {
            "chunks": chunks,
            "toc": toc,
            "total_chars": total_chars,
            "page_count": page_count
        }

    def index_document(self, doc_id: str, file_path: str, category: str, original_filename: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Extracts, embeds, and registers PDF chunks into ChromaDB with user isolation
        and returns detailed extraction metadata.
        """
        extracted = self.extract_and_chunk_pdf(file_path)
        chunks = extracted["chunks"]
        if not chunks:
            return {
                "chunk_count": 0,
                "toc": extracted["toc"],
                "total_chars": extracted["total_chars"],
                "page_count": extracted["page_count"]
            }

        ids = []
        documents = []
        metadatas = []

        chunk_texts = [c['text'] for c in chunks]
        embeddings = self.get_embeddings_batch(chunk_texts)

        for i, c in enumerate(chunks):
            c_id = f"{doc_id}_{c['chunk_index']}"
            ids.append(c_id)
            documents.append(c['text'])
            metadatas.append({
                "doc_id": doc_id,
                "user_id": user_id,
                "page_number": c["page_number"],
                "section_title": c.get("section_title", "General"),
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

        return {
            "chunk_count": len(chunks),
            "toc": extracted["toc"],
            "total_chars": extracted["total_chars"],
            "page_count": extracted["page_count"]
        }

    def delete_document_vectors(self, doc_id: str):
        """Purges all chunks belonging to a document from ChromaDB."""
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"[RAG] Warning deleting ChromaDB vectors for {doc_id}: {e}")

    def query_relevant_chunks(
        self,
        query_text: str,
        user_id: Optional[str] = None,
        document_id: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant document chunks with metadata for quizzes, flashcards, and citations.
        """
        query_vec = self.get_embedding(query_text)
        filters = []
        if user_id:
            filters.append({"user_id": user_id})
        if document_id:
            filters.append({"doc_id": document_id})
        if category and category.lower() != "all":
            filters.append({"category": category})

        where_filter = None
        if len(filters) == 1:
            where_filter = filters[0]
        elif len(filters) > 1:
            where_filter = {"$and": filters}

        query_args = {
            "query_embeddings": [query_vec],
            "n_results": top_k
        }
        if where_filter:
            query_args["where"] = where_filter

        try:
            results = self.collection.query(**query_args)
        except Exception as e:
            print(f"[RAG] ChromaDB query error in query_relevant_chunks: {e}")
            return []

        retrieved_docs = results.get("documents", [[]])[0] if results.get("documents") else []
        retrieved_meta = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

        chunks = []
        for text, meta in zip(retrieved_docs, retrieved_meta):
            chunks.append({
                "text": text,
                "page": meta.get("page_number", 1) if meta else 1,
                "section": meta.get("section_title", "") if meta else "",
                "filename": meta.get("filename", "") if meta else "",
                "doc_id": meta.get("doc_id", "") if meta else ""
            })
        return chunks

    def generate_quick_summary(self, file_path: str, filename: str, category: str, model: Optional[str] = None) -> str:
        """
        Generates an AI summary of the uploaded document with key topics and syllabus alignment.
        """
        extracted = self.extract_and_chunk_pdf(file_path, chunk_size=1000, overlap=0)
        chunks = extracted.get("chunks", [])
        sample_text = "\n\n".join([f"[Page {c['page_number']} | {c.get('section_title', '')}] {c['text']}" for c in chunks[:4]])

        if not sample_text:
            return f"Document '{filename}' uploaded under category '{category}'. Contains technical study material."

        if not self.is_configured() or model == "offline-curriculum":
            toc = extracted.get("toc", [])
            toc_bullets = "\n".join([f"- {item['title']} (Page {item['page']})" for item in toc[:4]])
            return (
                f"**Overview:** Study resource '{filename}' categorised as *{category}*.\n\n"
                f"- High-yield resource covering key examination concepts ({extracted['page_count']} pages, {extracted['total_chars']:,} characters).\n"
                f"- Structured reference for self-study, revision cycles, and high-frequency question patterns.\n"
                + (f"**Key Chapters Detected:**\n{toc_bullets}\n" if toc_bullets else "")
            )

        prompt = (
            f"You are a senior exam mentor for Indian competitive exams (SEBI, SBI, IBPS, UPSC, SSC).\n"
            f"Analyze the following initial pages of the uploaded document '{filename}' (Category: {category}):\n\n"
            f"{sample_text}\n\n"
            f"Provide a concise, 3-4 bullet point summary in markdown highlighting:\n"
            f"1. Core Subject Matter & Topics Covered\n"
            f"2. Exam Relevance & Target Sections\n"
            f"3. Suggested Study Approach (e.g., theory reading vs. MCQ practice)\n"
            f"Keep it crisp, scholarly, token-efficient, and student-friendly."
        )

        def _do_summary(model_name: str) -> str:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text

        try:
            return self._call_with_retry_and_fallback(_do_summary, requested_model=model)
        except Exception as e:
            return f"Overview for {filename}: High-yield technical document for {category}. ({extracted['page_count']} pages, {len(chunks)} indexed segments)."

    def answer_rag_query(
        self,
        query: str,
        doc_id: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Document Mode: Semantic RAG retrieval scoped by user_id and document/category.
        Optimizes prompt token usage by filtering and pruning context chunks.
        """
        query_vec = self.get_embedding(query)

        # Build ChromaDB where filter
        filters = []
        if user_id:
            filters.append({"user_id": user_id})
        if doc_id:
            filters.append({"doc_id": doc_id})
        if category and category.lower() != "all":
            filters.append({"category": category})

        where_filter = None
        if len(filters) == 1:
            where_filter = filters[0]
        elif len(filters) > 1:
            where_filter = {"$and": filters}

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

        # Token Optimization: Filter and Prune Context Chunks
        sources = []
        context_blocks = []
        max_context_chars = 4500  # Cap context at ~1,100 tokens of high-signal text
        accumulated_chars = 0

        for doc_text, meta in zip(retrieved_docs, retrieved_meta):
            if accumulated_chars + len(doc_text) > max_context_chars and len(context_blocks) >= 2:
                break
            fn = meta.get("filename", "Document")
            pg = meta.get("page_number", 1)
            sec = meta.get("section_title", "")
            d_id = meta.get("doc_id", "")
            sources.append({
                "filename": fn,
                "page": pg,
                "section": sec,
                "document_id": d_id
            })
            sec_tag = f" | Section: {sec}" if sec and sec != "General" else ""
            context_blocks.append(f"Source: {fn} (Page {pg}{sec_tag}):\n{doc_text.strip()}")
            accumulated_chars += len(doc_text)

        context_text = "\n\n---\n\n".join(context_blocks)

        # Offline / Zero-Token Mode Handling
        if model == "offline-curriculum" or not self.is_configured():
            if not context_blocks:
                return {
                    "answer": f"I could not locate specific matches for '{query}' in your uploaded documents. Please check your book search or ask a syllabus question.",
                    "sources": [],
                    "model": "offline-curriculum",
                    "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "saved": "100% Offline"}
                }
            return {
                "answer": (
                    f"**Extracted Reference Excerpt ({sources[0]['filename']}, Page {sources[0]['page']}):**\n\n"
                    f"{retrieved_docs[0]}\n\n"
                    f"> ⚡ **Token Saver Mode:** Answered using local semantic vector matching (0 cloud tokens used)."
                ),
                "sources": sources,
                "model": "offline-curriculum",
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "saved": "100% Offline"}
            }

        # Token-Optimized System Prompt
        prompt = (
            f"You are an expert AI Tutor and Senior Faculty Mentor for Indian Government and Competitive Exams.\n"
            f"A student is asking:\n\n"
            f"Student Question: {query}\n\n"
            f"Extracted Study Material Context:\n"
            f"{context_text if context_text else 'No specific document excerpts matched.'}\n\n"
            f"Guidelines for High-Yield Learning & Token Efficiency:\n"
            f"1. Directly address the core doubt using concise, authoritative points and clear headings.\n"
            f"2. Cite the source document name and page number when citing facts (e.g. '[{sources[0]['filename'] if sources else 'Book'}, Page X]').\n"
            f"3. Highlight key exam formulas, concepts, or pitfalls clearly."
        )

        chosen_model = model or self.active_chat_model
        p_tokens_est = max(1, int(len(prompt.split()) * 1.3))

        def _do_chat(model_name: str) -> Tuple[str, Dict[str, Any]]:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            # Extract official usage metadata if provided by Gemini SDK
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', p_tokens_est),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                    "model": model_name
                }
            else:
                c_tokens_est = max(1, int(len(response.text.split()) * 1.3))
                usage = {
                    "prompt_tokens": p_tokens_est,
                    "completion_tokens": c_tokens_est,
                    "total_tokens": p_tokens_est + c_tokens_est,
                    "model": model_name
                }
            return response.text, usage

        try:
            answer, usage_data = self._call_with_retry_and_fallback(_do_chat, requested_model=chosen_model)
            return {
                "answer": answer,
                "sources": sources,
                "model": usage_data.get("model", chosen_model),
                "token_usage": usage_data
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
                "model": "offline-vector-match",
                "token_usage": {"prompt_tokens": p_tokens_est, "completion_tokens": 50, "total_tokens": p_tokens_est + 50}
            }

    def answer_general_mentor_query(self, query: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        General Mode: Exam mentor answering syllabus, current affairs, doubts, and strategy.
        Supports dynamic model selection and token usage tracking.
        """
        if model == "offline-curriculum" or not self.is_configured():
            return {
                "answer": (
                    f"**Faculty Mentor Insights on '{query}':**\n\n"
                    f"1. **Syllabus & Weightage Alignment:** Prioritize high-scoring modules first (e.g. DBMS, Networking, OS, and Data Structures for IT officer exams; History, Polity, Geography for General exams).\n"
                    f"2. **Daily Routine:** Maintain a 60/40 ratio between theoretical study and active MCQ practice under timed conditions.\n"
                    f"3. **Error Analysis:** Thoroughly analyze every incorrect option in your mock tests to avoid repeating conceptual traps.\n\n"
                    f"> ⚡ **Token Saver:** Response generated using local syllabus guidelines (0 cloud tokens used)."
                ),
                "sources": [],
                "model": "offline-curriculum",
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "saved": "100% Offline"}
            }

        prompt = (
            f"You are a senior faculty mentor for Indian Government and Competitive Exams (UPSC CSE, SSC CGL, Banking Exams, Railways, State PSCs).\n"
            f"Answer the aspirant's query thoughtfully, concisely, and authoritatively:\n\n"
            f"Query: {query}\n\n"
            f"Provide actionable advice, syllabus clarity, or high-yield technical explanations in clean Markdown with clear headings."
        )

        chosen_model = model or self.active_chat_model
        p_tokens_est = max(1, int(len(prompt.split()) * 1.3))

        def _do_mentor(model_name: str) -> Tuple[str, Dict[str, Any]]:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', p_tokens_est),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                    "model": model_name
                }
            else:
                c_tokens_est = max(1, int(len(response.text.split()) * 1.3))
                usage = {
                    "prompt_tokens": p_tokens_est,
                    "completion_tokens": c_tokens_est,
                    "total_tokens": p_tokens_est + c_tokens_est,
                    "model": model_name
                }
            return response.text, usage

        try:
            ans, usage_data = self._call_with_retry_and_fallback(_do_mentor, requested_model=chosen_model)
            return {
                "answer": ans,
                "sources": [],
                "model": usage_data.get("model", chosen_model),
                "token_usage": usage_data
            }
        except Exception as e:
            return {
                "answer": (
                    f"**Faculty Mentor Insights on '{query}':**\n\n"
                    f"1. **Syllabus & Weightage Alignment:** Prioritize high-scoring modules first.\n"
                    f"2. **Daily Routine:** Maintain a 60/40 ratio between theoretical study and active MCQ practice under timed conditions.\n"
                    f"3. **Error Analysis:** Thoroughly analyze every incorrect option in your mock tests.\n\n"
                    f"> 💡 *Notice: Cloud generation experienced an issue ({e}). Showing offline curriculum guidelines.*"
                ),
                "sources": [],
                "model": "offline-curriculum-mentor",
                "token_usage": {"prompt_tokens": p_tokens_est, "completion_tokens": 60, "total_tokens": p_tokens_est + 60}
            }

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

        blueprint = f"""{alert_banner}# Comprehensive Master Preparation Strategy: {exam_name}

## 🎯 Candidate Profile & Time Allocation
- **Target Examination:** {exam_name}
- **Current Preparation Stage:** {prep_level}
- **Allocated Daily Study Time:** {hours} Hours / Day
  - 📖 **Core Concept Study & Theory:** {tech_hrs} Hours
  - ✍️ **Active Question Practice & PYQs:** {mcq_hrs} Hours
  - 🔁 **Active Recall & Revision Drill:** {rev_hrs} Hours

---

## 📌 Phase-Wise 16-Week Preparation Roadmap

### Phase 1: Foundational Theory & Syllabus Mapping (Weeks 1 to 5)
- **Objective:** Complete 100% syllabus coverage of foundational concepts.
- **Key Milestones:**
  - Build chapter-wise formula notebooks and concept maps.
  - Complete basic exercises and previous 5 years' preliminary level questions.
  - Dedicate 1.5 hours every Sunday to revision of the entire week's notes.

### Phase 2: In-Depth Subject Mastery & High-Yield Sections (Weeks 6 to 11)
- **Objective:** Focus intensively on subjects carrying maximum weightage.
- **Key Milestones:**
  - Transition from standard textbook theory to timed sectional question sets.
  - Solve high-difficulty multi-concept questions.
  - Maintain a separate **Mistake Log** analyzing reasons for incorrect attempts.

### Phase 3: Full-Length Mocks, Speed Tuning & Final Revision (Weeks 12 to 16)
- **Objective:** Simulate real exam conditions and develop peak exam temperament.
- **Key Milestones:**
  - Take 2 full-length simulated mock tests every week strictly within official exam hours.
  - Zero in on negative marking elimination and sectional time management.
  - Dedicate the final 10 days solely to formula sheets, high-frequency facts, and mistake logs.

---

## ⚡ Daily Study Routine Blueprint ({hours} Hours)
- **Session 1 (Morning - Peak Alertness | {tech_hrs}h):** Deep work on core analytical subjects and tough theoretical chapters.
- **Session 2 (Afternoon/Evening | {mcq_hrs}h):** Timed practice questions, sectional quizzes, and past exam questions.
- **Session 3 (Night - Consolidation | {rev_hrs}h):** Rapid active recall, reviewing today's formulas, and planning tomorrow's syllabus targets.
"""
        return blueprint

    def generate_strategy(self, exam_name: str, daily_hours: float, prep_level: str, model: Optional[str] = None) -> str:
        """
        Generates structured, actionable study strategy using Gemini with fallback.
        """
        if model == "offline-curriculum" or not self.is_configured():
            return self._build_rich_strategy_blueprint(
                exam_name=exam_name,
                daily_hours=daily_hours,
                prep_level=prep_level,
                api_error_note="Using Offline Exam Pattern & Curriculum Knowledge Base (Zero API Quota Used)"
            )

        prompt = (
            f"You are a master study strategist and senior mentor for Indian competitive exams (SEBI, SBI SCO, IBPS SO, UPSC, SSC).\n"
            f"Create a comprehensive, highly actionable preparation strategy for:\n"
            f"- Target Exam: {exam_name}\n"
            f"- Daily Study Hours: {daily_hours}\n"
            f"- Preparation Level: {prep_level}\n\n"
            f"Include:\n"
            f"1. Detailed 16-Week Phase Breakdown (Foundations, Advanced Practice, Mock Cycles)\n"
            f"2. Daily Hourly Schedule matching {daily_hours} hours\n"
            f"3. High-Yield Topic Priorities and Subject Weightage\n"
            f"4. Revision Strategy and Error Analysis Techniques\n"
            f"Format cleanly in Markdown with bold headers and bullet points."
        )

        chosen_model = model or self.active_chat_model

        def _do_strategy(model_name: str) -> str:
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text

        try:
            return self._call_with_retry_and_fallback(_do_strategy, requested_model=chosen_model)
        except Exception as e:
            print(f"[RAG] Strategy generation API call failed ({e}). Using offline curriculum blueprint.")
            return self._build_rich_strategy_blueprint(
                exam_name=exam_name,
                daily_hours=daily_hours,
                prep_level=prep_level,
                api_error_note=f"API temporarily reached quota or experienced a connection issue ({e})."
            )

    generate_exam_strategy = generate_strategy

# Singleton instance
rag_service = ChromaRAGService()
