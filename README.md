# Pariksha Copilot (परीक्षा Copilot)

An AI-powered preparation platform and study copilot for Indian competitive examinations (**UPSC CSE, SEBI Grade A, SBI SCO, IBPS SO, SSC CGL, Banking & State PSCs**).

Pariksha Copilot combines an **Adaptive AI Strategy Generator**, a **Digital Book Vault** with split-screen reading desk, **PyMuPDF Structural Extraction**, and a **RAG-powered Faculty Mentor** supporting **Multi-Model Selection** (Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 1.5 Flash, Gemini 1.5 Pro, and Offline Curriculum Base) with token usage optimization.

---

## 🌟 Key Features

1. **Multi-Model AI Engine:**
   - **Gemini 2.5 Flash (Recommended):** High-velocity inference, optimal token economics, and sharp reasoning.
   - **Gemini 2.5 Pro (Deep Thinker):** Multi-step analytical reasoning for complex syllabus breakdowns and numerical problems.
   - **Gemini 1.5 Flash (Instant):** Streamlined, ultra-fast responses for quick doubt verification.
   - **Gemini 1.5 Pro (Long-Form):** Extended context window across multi-chapter textbooks.
   - **Offline Curriculum Base (100% Free / 0 Tokens):** Deterministic local semantic matching and standard syllabus doctrines without consuming any cloud API quota.

2. **Token Usage Optimization:**
   - **Dynamic Context Budgeting:** Filters and prunes retrieved RAG excerpts to top-k high-signal chunks (~1,100 tokens max), avoiding massive prompt token burns.
   - **Summary Caching:** Auto-generated summaries are computed once on upload and cached in SQLite.
   - **Real-Time Token Badges:** Every mentor response displays an efficiency indicator (e.g. `⚡ 804 tokens` or `⚡ 0 cloud tokens (Offline)`).

3. **High-Performance PyMuPDF (`fitz`) Text & Outline Extraction:**
   - **Book Outlines & Table of Contents (TOC):** Detects document chapter hierarchies with 1-click chapter jumps in the Reading Desk.
   - **Structural Heading & Section Detection:** Tags chunks with `section_title` metadata for precise vector search citations.
   - **Table Parsing:** Formats tables cleanly into structured Markdown.
   - **Semantic Paragraph Chunking:** Chunks text at natural paragraph boundaries without truncating formulas or sentences.
   - **Scanned PDF Fallback:** Graceful fallback support for image-only PDFs.

4. **Split-Screen PDF Reading Desk:**
   - Embedded native PDF viewer on the left side.
   - High-Yield Chapter Digest & dedicated "Ask this Book" RAG chat panel on the right side.
   - Clickable source citations with document names and page numbers.

5. **Multi-User Isolation & Session Resumption:**
   - Cryptographic PBKDF2-HMAC-SHA256 password hashing (100,000 iterations) with unique salts.
   - Bearer session token authentication cleanly isolating documents, strategies, and chats per user.
   - Multi-turn conversation history automatically saved to SQLite and resumed upon re-opening documents.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, `google-genai` SDK, PyMuPDF (`pymupdf`), PyPDF.
- **Frontend:** React (Vite), Tailwind CSS, Lucide Icons.
- **Vector Database (RAG):** ChromaDB (Persistent local storage) with Google Embeddings (`text-embedding-004`) and deterministic offline vector fallback.
- **Relational Database:** SQLite with SQLAlchemy (structured for easy migration to PostgreSQL).
- **File Storage:** Local filesystem (`/uploads/{user_id}/{category}/{uuid}_{filename}.pdf`) with SHA-256 deduplication hashing.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for building frontend)
- Google Gemini API key (optional for offline mode, recommended for live cloud AI)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/RGboss/pariksha-copilot.git
cd pariksha-copilot

# Install Python backend dependencies
python -m pip install -r requirements.txt

# (Optional) Install frontend dependencies & build
cd frontend
npm install
npm run build
cd ..
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
HOST=127.0.0.1
PORT=8000
```

### 4. Running the Application

```bash
python run_server.py
```

Open your browser at **`http://127.0.0.1:8000`**.

---

## 🧪 Testing & Verification

Run the automated test suites:

```bash
# Test multi-user auth and chat resumption
python test_account_chat_resumption.py

# Test multi-model selection, PyMuPDF extraction, and token optimization
python test_powerful_pdf_and_models.py
```

---

## 📄 License
MIT License. Built for aspirants preparing for competitive examinations.
