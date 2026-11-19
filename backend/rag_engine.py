# -*- coding: utf-8 -*-
"""
Google GenAI RAG Engine & Vector Search Service
Supports:
- Google Text Embeddings (text-embedding-004)
- Google Gemini 2.5 Flash / 1.5 Flash generative models
- High-performance SQLite + NumPy vector similarity search
- Hybrid Search (Dense Vector + Keyword BM25 overlap)
- Automated PDF summarization & contextual citation Q&A
- Graceful offline fallback when API key is not yet configured
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from dotenv import load_dotenv

from backend.db import (
    get_all_chunks_for_vector_search,
    get_setting,
    set_setting,
    save_chat_message,
    get_chat_history
)

load_dotenv()

class GoogleRAGService:
    def __init__(self):
        self.embedding_model = "text-embedding-004"
        self.chat_model = "gemini-2.5-flash"
        self._cached_client = None
        self._cached_key = None

    def get_api_key(self, provided_key: Optional[str] = None) -> Optional[str]:
        """
        Resolves API key with hierarchical fallback:
        1. Explicitly provided argument
        2. SQLite app_settings ('gemini_api_key')
        3. Environment variable 'GEMINI_API_KEY'
        4. Environment variable 'GOOGLE_API_KEY'
        """
        if provided_key and provided_key.strip():
            return provided_key.strip()
        
        db_key = get_setting("gemini_api_key")
        if db_key and db_key.strip():
            return db_key.strip()
            
        env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if env_key and env_key.strip():
            return env_key.strip()
            
        return None

    def get_client(self, api_key: Optional[str] = None):
        """
        Initializes and caches google.genai client.
        """
        key = self.get_api_key(api_key)
        if not key:
            return None
        
        if self._cached_client and self._cached_key == key:
            return self._cached_client
            
        try:
            from google import genai
            client = genai.Client(api_key=key)
            self._cached_client = client
            self._cached_key = key
            return client
        except Exception as e:
            print(f"[RAG] Failed to initialize google.genai client: {e}")
            return None

    def is_configured(self, api_key: Optional[str] = None) -> bool:
        """
        Checks whether a valid API key is present.
        """
        key = self.get_api_key(api_key)
        return bool(key and len(key) >= 15)

    def generate_embeddings(self, texts: List[str], api_key: Optional[str] = None) -> List[Optional[np.ndarray]]:
        """
        Generates 768-dimensional float32 vector embeddings for a list of text strings.
        Returns a list of NumPy arrays (or None if client unavailable).
        """
        client = self.get_client(api_key)
        if not client or not texts:
            return [None] * len(texts)

        results = []
        batch_size = 10  # Process in batches to stay well within quotas
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                # google.genai client embed_content
                embed_res = client.models.embed_content(
                    model=self.embedding_model,
                    contents=batch
                )
                
                # Check structure of embeddings returned by SDK
                if hasattr(embed_res, 'embeddings'):
                    for emb in embed_res.embeddings:
                        vec = np.array(emb.values, dtype=np.float32)
                        results.append(vec)
                elif hasattr(embed_res, 'embedding'):
                    vec = np.array(embed_res.embedding.values, dtype=np.float32)
                    results.append(vec)
                else:
                    results.extend([None] * len(batch))
            except Exception as e:
                print(f"[RAG] Error generating embeddings batch {i}-{i+batch_size}: {e}")
                results.extend([None] * len(batch))

        return results

    def generate_single_embedding(self, text: str, api_key: Optional[str] = None) -> Optional[np.ndarray]:
        res = self.generate_embeddings([text], api_key)
        return res[0] if res else None

    def summarize_document(self, text_sample: str, title: str, category: str, api_key: Optional[str] = None) -> str:
        """
        Uses Gemini to generate a high-yield academic summary of the uploaded document.
        """
        client = self.get_client(api_key)
        if not client:
            # Fallback heuristic summary if offline
            preview = text_sample[:500].replace('\n', ' ').strip()
            return f"Document '{title}' ({category}). Sample content preview: {preview}..."

        prompt = f"""You are an expert IT Officer examination academic advisor for SEBI Grade A (IT Stream), SBI SCO (IT), and IBPS SO (IT Officer).

Please analyze the following excerpt from the study document '{title}' (Category: {category}):

---
{text_sample[:10000]}
---

Provide a structured, student-friendly summary formatted in markdown:
1. **Core Subject & Topic Overview**: What IT domain does this cover? (e.g. DBMS, Networking, Java OOPs, System Design, Cybersecurity, etc.)
2. **Relevance to Banking Exams**: How does it map to SEBI, SBI SCO, or IBPS SO syllabus?
3. **Key Concepts & Question Types**: What specific topics or interview/exam questions does this document provide?
Keep it clear, concise (under 250 words), and highly actionable for an exam aspirant.
"""
        try:
            response = client.models.generate_content(
                model=self.chat_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"[RAG] Summarization error: {e}")
            preview = text_sample[:400].replace('\n', ' ').strip()
            return f"Uploaded Document: {title}. Preview: {preview}..."

    def search_similar_chunks(self, query: str, doc_id: Optional[str] = None,
                              top_k: int = 5, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search across stored document chunks in SQLite:
        1. Dense Vector Cosine Similarity (via Google text-embedding-004 + NumPy)
        2. Keyword Lexical Matching bonus for exact technical terminology
        """
        chunks = get_all_chunks_for_vector_search(doc_id)
        if not chunks:
            return []

        q_vec = self.generate_single_embedding(query, api_key)
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        
        scored_chunks = []
        
        for ch in chunks:
            content = ch['content']
            blob = ch['embedding_blob']
            
            vector_score = 0.0
            if q_vec is not None and blob is not None:
                try:
                    c_vec = np.frombuffer(blob, dtype=np.float32)
                    norm_q = np.linalg.norm(q_vec)
                    norm_c = np.linalg.norm(c_vec)
                    if norm_q > 0 and norm_c > 0:
                        vector_score = float(np.dot(q_vec, c_vec) / (norm_q * norm_c))
                except Exception:
                    vector_score = 0.0

            # Lexical term overlap bonus
            content_lower = content.lower()
            term_matches = sum(1 for term in query_terms if term in content_lower)
            lexical_score = (term_matches / len(query_terms)) if query_terms else 0.0
            
            # Hybrid combined score
            if q_vec is not None:
                combined_score = (0.75 * vector_score) + (0.25 * lexical_score)
            else:
                combined_score = lexical_score

            scored_chunks.append({
                "id": ch['id'],
                "document_id": ch['document_id'],
                "filename": ch['original_filename'],
                "category": ch['category'],
                "page": ch['page_number'],
                "content": content,
                "score": round(combined_score, 4),
                "vector_score": round(vector_score, 4),
                "lexical_score": round(lexical_score, 4)
            })

        # Sort descending by combined score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        return scored_chunks[:top_k]

    def answer_query(self, query: str, session_id: str, doc_id: Optional[str] = None,
                     api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes end-to-end RAG pipeline:
        1. Retrieves top matching chunks from vector database
        2. Constructs contextual academic prompt
        3. Generates response using Gemini 2.5 Flash
        4. Saves interaction to SQLite chat history
        """
        top_chunks = self.search_similar_chunks(query, doc_id=doc_id, top_k=5, api_key=api_key)
        client = self.get_client(api_key)

        sources = [
            {
                "document_id": ch["document_id"],
                "filename": ch["filename"],
                "page": ch["page"],
                "snippet": ch["content"][:200] + ("..." if len(ch["content"]) > 200 else ""),
                "score": ch["score"]
            }
            for ch in top_chunks
        ]

        if not client:
            # Fallback when API key is not configured
            if top_chunks:
                context_preview = "\n\n".join([f"• [Doc: {ch['filename']}, Page {ch['page']}]:\n\"{ch['content'][:300]}...\"" for ch in top_chunks[:3]])
                answer = f"""### Relevant Excerpts Found ({len(top_chunks)} Sources)

{context_preview}

---
> [!NOTE] 
> **Gemini AI API Key Required for Dynamic Reasoning:**
> To get comprehensive conversational AI explanations, answers with synthesis, and code examples, please configure your **Google Gemini API Key** in **Settings** or your `.env` file (`GEMINI_API_KEY=AIzaSy...`).
"""
            else:
                answer = "No matching excerpts found in the uploaded documents. Try uploading the relevant PDF in the **PDF Library** or search by different keywords."

            save_chat_message(session_id, "user", query, document_id=doc_id)
            save_chat_message(session_id, "model", answer, document_id=doc_id, sources=sources)
            return {
                "session_id": session_id,
                "answer": answer,
                "sources": sources,
                "ai_active": False
            }

        # Context formatting
        context_blocks = []
        for i, ch in enumerate(top_chunks):
            context_blocks.append(f"[SOURCE {i+1} | Document: {ch['filename']} | Page: {ch['page']}]\n{ch['content']}")
        
        context_str = "\n\n".join(context_blocks)

        # Retrieve recent conversation history for memory
        history = get_chat_history(session_id, limit=6)
        history_str = ""
        for msg in history[-4:]:
            role_label = "Student" if msg['role'] == "user" else "Professor"
            history_str += f"{role_label}: {msg['content'][:200]}\n"

        prompt = f"""You are an elite AI Computer Science Professor and Examination Mentor specialized in Indian Banking & Regulatory IT Officer Examinations:
1. SEBI Grade A (IT Stream)
2. SBI Specialist Cadre Officer (SCO IT / Deputy Manager)
3. IBPS SO (IT Officer - Professional Knowledge)

You have access to the following retrieved excerpts from the student's study materials:

=== RETRIEVED DOCUMENT EXCERPTS ===
{context_str}
===================================

Conversation History:
{history_str}

Student Question: {query}

INSTRUCTIONS:
1. Provide an authoritative, textbook-grade, in-depth explanation answering the question clearly.
2. Ground your answer in the retrieved document excerpts. **Explicitly cite the source document name and page number** whenever stating a rule, algorithm, or fact from the text (e.g., "[Document: 100_DBMS_Interview.pdf, Page 14]").
3. Include clear mathematical equations (KaTeX syntax $...$ or $$...$$), bullet lists, and code snippets where appropriate.
4. If the question involves exam traps (e.g., SEBI distractor options or subtle differences like BCNF vs 3NF, or TCP vs UDP headers), highlight them in a clear callout.
5. If the excerpts do not fully address the question, synthesize the answer based on standard IT officer syllabus guidelines while clearly indicating what was in the text vs curriculum knowledge.
"""

        try:
            response = client.models.generate_content(
                model=self.chat_model,
                contents=prompt
            )
            answer = response.text.strip()
            ai_active = True
        except Exception as e:
            print(f"[RAG] Gemini generation error: {e}")
            answer = f"Error during Gemini generation ({e}). Falling back to retrieved document snippets."
            ai_active = False

        save_chat_message(session_id, "user", query, document_id=doc_id)
        save_chat_message(session_id, "model", answer, document_id=doc_id, sources=sources)

        return {
            "session_id": session_id,
            "answer": answer,
            "sources": sources,
            "ai_active": ai_active
        }

# Global Singleton
rag_service = GoogleRAGService()
