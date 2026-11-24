# Pariksha Copilot - Web Regression Test Report

**Execution Time:** 2026-11-24 16:35:40
**Overall Result:** 17/17 Passed (0 Failed)

| Test Case | Status | Duration | Details |
| :--- | :---: | :---: | :--- |
| Root Health /health | **PASS** | 0.03s | Status 200, Body: {"status":"healthy"} |
| API Health /api/health | **PASS** | 0.00s | Status 200, Body: {"status":"ok","app":"pariksha-copilot","version":"2.3.0"} |
| Model Catalog /api/models | **PASS** | 0.00s | Found 5 models: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-flash', 'gemini-1.5-pro', 'offline-curriculum'] |
| Aspirant Demo Login /api/auth/login | **PASS** | 0.12s | Logged in as Aspirant Rahul, token prefix: Nf2ovTjvAD... |
| Session Verification /api/auth/me | **PASS** | 0.01s | Verified aspirant: Aspirant Rahul, Exam: SEBI Grade A (IT Stream) |
| Workspace PDF Scanner /api/documents/workspace-available | **PASS** | 0.49s | Discovered 910 PDFs in workspace folders |
| Import Workspace PDF & Index in ChromaDB | **PASS** | 104.58s | Imported 'Computer_Networks_OSI_TCPIP_Notes.pdf' -> Doc ID: 5b3dfc25-548b-421c-9a6d-357fbe419e00, Pages: 213, Chunks: 470, Chars: 370178 |
| Direct Multipart PDF Upload /api/documents/upload | **PASS** | 106.22s | Uploaded 'Computer_Networks_OSI_TCPIP_Notes.pdf' -> Doc ID: 8832ac73-3f84-4eef-a24e-84bccb1bfc69, Chunks: 470 |
| List Documents /api/documents | **PASS** | 0.04s | User has 10 documents registered |
| Document Raw Text /api/documents/{id}/raw | **PASS** | 0.05s | Raw PDF served inline (3,649,894 bytes, Content-Type: application/pdf) |
| AI Chat (Document RAG Mode with Citations) | **PASS** | 0.36s | Model: offline-curriculum, Sources cited: 3, Response snippet: **Extracted Reference Excerpt (Computer_Networks_OSI_TCPIP_Notes.pdf, Page 80):**

The classes repre... |
| AI Chat (General Faculty Mentor Mode) | **PASS** | 0.01s | Model: offline-curriculum, Response snippet: **Faculty Mentor Insights on 'What is the recommended 60-day study strategy for SEBI Grade A IT Offi... |
| Chat History Persistence /api/chat/history | **PASS** | 0.01s | Retrieved 8 persisted chat interactions |
| Flashcards Generation, Spaced Repetition & Leitner Review | **PASS** | 1.30s | Generated 3 cards, total 15, reviewed card a84c6900-e05d-4ef7-9a26-eab6610acbfa -> new box: None |
| Quiz Generation, MCQ Formatting & Attempt Grading | **PASS** | 1.28s | Quiz 4ad565d4-0270-4dc3-8d8a-84a2890fe198 created with 3 questions. Attempt submitted -> Score: None/None (None%) |
| Study Planner Tasks, Toggle & Completion Stats | **PASS** | 0.03s | Created and toggled task 091471ba-5d29-4169-8948-d3f82ce2a480. Stats: {'total_tasks': 3, 'completed_tasks': 3, 'pending_tasks': 0, 'completion_rate': 100.0, 'streak_days': 4} |
| SPA Static Delivery & Client-Side Route Fallbacks | **PASS** | 0.08s | /: 200 (HTML: True), /strategy: 200 (HTML: True), /documents: 200 (HTML: True), /planner: 200 (HTML: True), /flashcards: 200 (HTML: True) |
