# 🚀 Pariksha Copilot: AI Feature & RAG Upgrade Radar

**Generated on:** Saturday, November 21, 2026  
**Target Repository:** `https://github.com/RGboss/pariksha-copilot`  
**Current Architecture:** FastAPI (`main:app`) on internal port 8000 + Nginx Gateway on port 8082, ChromaDB (814 vector chunks), SQLite (50 users), PyMuPDF 2.1+, Google GenAI SDK 2.0+.

---

## 🎯 Executive Summary: Top 3 High-Impact, Low-Effort AI Upgrades

Following an architectural multi-agent audit of `backend/chroma_rag.py`, `backend/quiz_service.py`, `backend/server.py`, and `requirements.txt`, the following 3 features offer the highest ROI for Indian competitive exam aspirants (UPSC CSE, SEBI Grade A, SSC CGL, IBPS SO):

| Priority | Feature Upgrade | Expected Impact | Effort Required | Key Technology |
| :---: | :--- | :---: | :---: | :--- |
| **#1** | **Zero-Hallucination CBT Mock Test & PYQ Engine** | **Very High** | **Low** | Gemini Structured Outputs (`response_schema`), Pydantic v2 |
| **#2** | **Live Exam Radar & Syllabus Amendment Grounding** | **Very High** | **Low** | Gemini Google Search Tool (`types.GoogleSearch`), `.gov.in` grounding |
| **#3** | **Multimodal Diagram & Flowchart RAG** | **High** | **Medium-Low** | Asymmetric Task Embeddings (`EmbedContentConfig`), PyMuPDF Drawing Extraction |

---

## Upgrade 1: Zero-Hallucination CBT Mock Test & PYQ Engine via Gemini Structured Outputs

### Aspirant Benefit & Motivation
Current quiz generation uses regex matching against free-form text JSON prompts (`re.search(r'\[.*\]', raw_text)`). Complex questions occasionally fail with JSON parse errors, missing distractors, or invalid answer indices.  
By switching to **Gemini Native Structured Outputs (`response_schema=CBTQuizPayload`)**, question generation becomes **100% deterministic and schema-enforced**. It also unlocks authentic Indian exam question patterns such as *Multi-Statement (Statements I, II & III)* and *Assertion-Reasoning (A & R)* with guaranteed 4 options, official page citations, and negative marking formulas.

### 📋 Copy-Ready Implementation Prompt
```markdown
Implement Gemini Structured Outputs using the official google-genai SDK (v2.0+) and Pydantic schemas in E:/study material/prep_platform/backend to guarantee zero-hallucination CBT mock quizzes and flashcards.

Specifically:
1. In `backend/chroma_rag.py`:
   - Implement the helper method `query_relevant_chunks(self, query_text: str, user_id: str, document_id: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]` on `ChromaRAGService` so quiz and flashcard services can reliably fetch top semantic text chunks with metadata (page, section, document name).
2. In `backend/quiz_service.py`:
   - Define strict Pydantic schemas:
     ```python
     from pydantic import BaseModel, Field
     from typing import List, Literal

     class CBTQuestion(BaseModel):
         question: str = Field(description="Rigorous exam question stem matching Indian competitive exam standard (e.g. UPSC, SEBI, SSC CGL)")
         question_type: Literal["single_choice", "multi_statement", "assertion_reasoning"] = Field(description="Question format")
         options: List[str] = Field(description="Exactly 4 distinct, plausible answer options", min_length=4, max_length=4)
         answer_index: int = Field(description="Zero-based index (0, 1, 2, or 3) of the correct option", ge=0, le=3)
         explanation: str = Field(description="Exhaustive rationale detailing why the correct option is right and others are incorrect")
         negative_marking: float = Field(default=0.25, description="Penalty deduction for wrong answer")
         subtopic: str = Field(description="Specific syllabus subtopic tested")
         reference_page: int = Field(description="Source textbook page number")
         reference_doc: str = Field(description="Source document name")

     class CBTQuizPayload(BaseModel):
         exam_name: str
         difficulty: Literal["Easy", "Medium", "Hard"]
         questions: List[CBTQuestion]
     ```
   - Update `generate_quiz_from_doc`:
     Replace string prompts and regex parsing with:
     ```python
     config = types.GenerateContentConfig(
         response_mime_type="application/json",
         response_schema=CBTQuizPayload,
         temperature=0.2
     )
     resp = client.models.generate_content(
         model="gemini-2.5-flash",
         contents=prompt,
         config=config
     )
     parsed = CBTQuizPayload.model_validate_json(resp.text)
     ```
   - Retain existing offline rule-based fallback generator if API key is unset or quota is exhausted.
3. In `backend/flashcards_service.py`:
   - Apply the same structured output pattern using a `FlashcardList` Pydantic schema with fields `front_prompt`, `back_answer`, `difficulty`, and `key_facts`.
4. Run validation tests to ensure quizzes and flashcards parse cleanly with 0 JSON errors and persist into SQLite correctly without disrupting the Nginx 8082 gateway or wiping ChromaDB.
```

---

## Upgrade 2: Live Exam Radar & Syllabus Amendment Grounding via Google Search Tool

### Aspirant Benefit & Motivation
Aspirants frequently need up-to-the-minute updates on exam dates, admit card releases, eligibility revisions, and syllabus changes for bodies like UPSC, SSC, SEBI, and IBPS.  
By enabling **Gemini Google Search Grounding (`types.GoogleSearch()`)**, Pariksha Copilot searches live official government portals (`.gov.in`, `.nic.in`) and returns answers with real-time official URLs and grounding attribution.

### 📋 Copy-Ready Implementation Prompt
```markdown
Integrate Google Search Grounding into Pariksha Copilot (E:/study material/prep_platform) to provide aspirants with real-time, verified government exam dates, vacancy notifications, and syllabus amendments.

Specifically:
1. In `backend/chroma_rag.py`:
   - Add a new method `answer_grounded_exam_query(self, query: str, exam_name: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]` to `ChromaRAGService`.
   - Configure Gemini Google Search Grounding using `google-genai`:
     ```python
     from google.genai import types

     grounding_tool = types.Tool(google_search=types.GoogleSearch())
     config = types.GenerateContentConfig(
         tools=[grounding_tool],
         temperature=0.2
     )
     response = client.models.generate_content(
         model=model or "gemini-2.5-flash",
         contents=f"You are the official Government Exam Advisory Officer for {exam_name or 'Indian Competitive Exams (UPSC, SEBI, SSC, Banking)'}. Answer this query with the latest official notifications, calendar dates, eligibility criteria, and syllabus amendments: {query}. Always cite official government domains (.gov.in, .nic.in, pib.gov.in).",
         config=config
     )
     ```
   - Parse `response.candidates[0].grounding_metadata`:
     - Extract `web_search_queries`
     - Extract `grounding_chunks` (URLs and Titles of official portals like upsc.gov.in, ssc.gov.in, sebi.gov.in)
     - Extract `grounding_supports`
   - Return `{ "answer": response.text, "sources": web_sources, "search_queries": search_queries, "grounded": True, "model": model }`.
   - Wrap the call in `_call_with_retry_and_fallback` and provide an offline curriculum fallback when offline or if quota is exceeded.
2. In `backend/server.py`:
   - In `/api/chat`, add support for `mode="live_radar"` or a boolean field `enable_web_grounding: bool = False` in `ChatRequest`. When active, route to `answer_grounded_exam_query`.
   - Add a dedicated endpoint `GET /api/exam-radar/latest?exam=UPSC` returning live notifications and calendar schedules.
   - Save the assistant response in `ChatHistory` with grounding URLs stored in `sources_json`.
3. Preserve all existing operational rules: keep FastAPI on internal port 8000 (proxied via Nginx on 8082), do not commit secrets, and do not modify or wipe persistent SQLite/ChromaDB directories.
```

---

## Upgrade 3: Multimodal Diagram & Flowchart RAG with Task-Aware Asymmetric Embeddings

### Aspirant Benefit & Motivation
Government exam textbooks (especially for SEBI IT, UPSC Geography/Economy, and SSC Mensuration) are filled with critical diagrams, architecture schemas, flowcharts, and statistical tables.  
Standard text chunking ignores image drawings or degrades vector similarity. Upgrading `text-embedding-004` to use **Asymmetric Task Types (`RETRIEVAL_DOCUMENT` during indexing vs `RETRIEVAL_QUERY` during search)** and adding PyMuPDF visual figure detection indexed with Gemini vision summaries enables aspirants to search and retrieve visual diagrams directly.

### 📋 Copy-Ready Implementation Prompt
```markdown
Upgrade the vector retrieval and PDF ingestion pipeline in E:/study material/prep_platform/backend/chroma_rag.py to support Asymmetric Task-Type Embeddings and Multimodal Flowchart/Diagram Understanding for complex question banks.

Specifically:
1. In `backend/chroma_rag.py`:
   - Upgrade `get_embedding(self, text: str, task_type: str = "RETRIEVAL_QUERY", title: Optional[str] = None) -> List[float]`:
     Configure `types.EmbedContentConfig`:
     ```python
     config = types.EmbedContentConfig(
         task_type=task_type, # "RETRIEVAL_DOCUMENT" when indexing, "RETRIEVAL_QUERY" when searching
         title=title[:100] if title else None,
         output_dimensionality=768
     )
     res = self.genai_client.models.embed_content(
         model="text-embedding-004",
         contents=text[:2048],
         config=config
     )
     ```
     Ensure `index_document()` uses `task_type="RETRIEVAL_DOCUMENT"` with the PDF filename as title, while `answer_rag_query()` and `query_relevant_chunks()` use `task_type="RETRIEVAL_QUERY"`. This eliminates asymmetric embedding mismatch penalties.
2. Multimodal Diagram & Figure Extraction:
   - In `extract_and_chunk_pdf()`:
     Use PyMuPDF (`fitz`) to inspect page drawings and images (`page.get_images()`, `page.get_drawings()`).
     For pages containing key diagrams, flowcharts, or architecture schemas, extract the image bytes or render the diagram bounding box.
     Use `gemini-2.5-flash` with a lightweight vision prompt:
     `"Generate a concise 2-sentence technical description of this exam textbook diagram/flowchart for semantic search indexing, listing all labels, axes, and concepts shown."`
   - Create a distinct chunk type `[Diagram/Flowchart on Page X]: <visual description>` and index it into ChromaDB with metadata `{"is_visual": True, "page_number": X, "section_title": "Visual Diagram"}`.
3. In `backend/server.py`:
   - Ensure visual diagram sources returned by `/api/chat` include an `is_visual: True` flag so the frontend can display a "📊 Diagram Source" badge and link to the exact PDF page.
4. Keep the deterministic 768-dim pseudo-vector fallback intact for offline use and do not erase existing ChromaDB collections.
```
