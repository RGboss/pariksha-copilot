# Pariksha Copilot (परीक्षा Copilot)

An AI-powered preparation platform and study copilot for Indian competitive examinations (**UPSC CSE, SEBI Grade A, SBI SCO, IBPS SO, SSC CGL, Banking & State PSCs**).

Pariksha Copilot combines an **Adaptive AI Strategy Generator**, a **Digital Book Vault** with split-screen reading desk, **PyMuPDF Structural Extraction**, and a **RAG-powered Faculty Mentor** supporting **Multi-Model Selection** (Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 1.5 Flash, Gemini 1.5 Pro, and Offline Curriculum Base), token usage optimization, **PostgreSQL** relational storage, and containerized **Docker & Nginx** deployment.

---

## 🌟 Key Features

1. **Multi-Model AI Engine:**
   - **Gemini 2.5 Flash (Recommended):** High-velocity inference, optimal token economics, and sharp reasoning.
   - **Gemini 2.5 Pro (Deep Thinker):** Multi-step analytical reasoning for complex syllabus breakdowns and numerical problems.
   - **Gemini 1.5 Flash (Instant):** Streamlined, ultra-fast responses for quick doubt verification.
   - **Gemini 1.5 Pro (Long-Form):** Extended context window across multi-chapter textbooks.
   - **Offline Curriculum Base (100% Free / 0 Tokens):** Deterministic local semantic matching and standard syllabus doctrines without consuming any cloud API quota.

2. **Enterprise Relational Storage (PostgreSQL & SQLite):**
   - Supports production-grade **PostgreSQL 16** with robust connection pooling (`pool_size=10, max_overflow=20, pool_pre_ping=True`).
   - Seamless fallback to local **SQLite** when running without a database server.
   - Database-agnostic automatic schema migrations.

3. **Production Containerization (Docker & Nginx):**
   - **Multi-stage Docker builds** for optimized frontend and backend images.
   - **Nginx Reverse Proxy:** Serves the compiled React SPA, reverse-proxies `/api/` and `/uploads/` to the FastAPI backend, provides gzip compression, client body sizes up to 100MB for textbooks, and extended timeouts for deep RAG inference.
   - **Docker Compose:** One-command startup orchestrating PostgreSQL, FastAPI, and Nginx.

4. **Token Usage Optimization:**
   - **Dynamic Context Budgeting:** Filters and prunes retrieved RAG excerpts to top-k high-signal chunks (~1,100 tokens max), avoiding massive prompt token burns.
   - **Summary Caching:** Auto-generated summaries are computed once on upload and cached in the database.
   - **Real-Time Token Badges:** Every mentor response displays an efficiency indicator (e.g. `⚡ 804 tokens` or `⚡ 0 cloud tokens (Offline)`).

5. **High-Performance PyMuPDF (`fitz`) Text & Outline Extraction:**
   - **Book Outlines & Table of Contents (TOC):** Detects document chapter hierarchies with 1-click chapter jumps in the Reading Desk.
   - **Structural Heading & Section Detection:** Tags chunks with `section_title` metadata for precise vector search citations.
   - **Table Parsing:** Formats tables cleanly into structured Markdown.
   - **Semantic Paragraph Chunking:** Chunks text at natural paragraph boundaries without truncating formulas or sentences.
   - **Scanned PDF Fallback:** Graceful fallback support for image-only PDFs.

6. **Split-Screen PDF Reading Desk:**
   - Embedded native PDF viewer on the left side.
   - High-Yield Chapter Digest & dedicated "Ask this Book" RAG chat panel on the right side.
   - Clickable source citations with document names and page numbers.

7. **Multi-User Isolation & Session Resumption:**
   - Cryptographic PBKDF2-HMAC-SHA256 password hashing (100,000 iterations) with unique salts.
   - Bearer session token authentication cleanly isolating documents, strategies, and chats per user.
   - Multi-turn conversation history automatically saved and resumed upon re-opening documents.

8. **Active Recall Flashcards (Leitner Spaced Repetition):**
   - AI-generated flashcards extracted directly from uploaded textbooks or custom syllabus topics.
   - 5-stage Leitner spaced repetition review algorithm (`Again`, `Hard`, `Good`, `Easy`) to maximize long-term retention of constitutional articles, statutory metrics, and high-yield formulas.
   - 1-click Markdown revision deck export for offline review.

9. **Timed CBT Mock Exam Simulator & PYQs:**
   - Computer-Based Test (CBT) interface simulating real exam pressure with countdown timers and question palettes.
   - 4-option multiple choice questions with detailed explanations, official rationales, and exact page/document citations.
   - Instant scorecards, percentage calculations, and historical attempt analytics.

10. **Daily Study Planner & Focus Desk:**
    - Daily syllabus milestone checklist with priority ratings (`High`, `Medium`, `Low`) and categories.
    - Integrated Pomodoro focus timer (25 min deep work / 5 min break intervals).
    - Preparation streak counter and completion rate benchmarks.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, `google-genai` SDK, PyMuPDF (`pymupdf`), PyPDF, `psycopg2-binary`.
- **Frontend:** React (Vite), Tailwind CSS, Lucide Icons.
- **Web Server & Reverse Proxy:** Nginx (Alpine).
- **Vector Database (RAG):** ChromaDB (Persistent local storage) with Google Embeddings (`text-embedding-004`) and deterministic offline vector fallback.
- **Relational Database:** PostgreSQL 16 (Production) / SQLite (Local standalone).
- **File Storage:** Local filesystem (`/uploads/{user_id}/{category}/{uuid}_{filename}.pdf`) with SHA-256 deduplication hashing.

---

## 🐳 Running with Docker & Docker Compose (Recommended)

Run the full production stack (PostgreSQL + FastAPI Backend + Nginx Reverse Proxy & React UI) with a single command:

### 1. Configure Environment
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=80
```

### 2. Start the Stack
```bash
docker compose up --build -d
```

### 3. Access the Application
Open your browser at:
```
http://localhost
```

To view logs:
```bash
docker compose logs -f
```

To stop containers:
```bash
docker compose down
```

---

## 🚀 Running Locally (Without Docker)

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

# Install frontend dependencies & build
cd frontend
npm install
npm run build
cd ..
```

### 3. Environment Setup

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
# Optional: Set DATABASE_URL to your PostgreSQL instance, or leave empty to use SQLite
# DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/pariksha_copilot
PORT=8000
```

### 4. Running the Server

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

# Test active recall flashcards, CBT mock quiz, and daily planner
python test_extended_features.py
```

---

## 📄 License
MIT License. Built for aspirants preparing for competitive examinations.
