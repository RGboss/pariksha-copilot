# IT Officer Preparation Platform & AI Tutor

A full-stack, book-oriented study and examination preparation platform for **SEBI Grade A (IT Stream)**, **SBI Specialist Cadre Officer (SCO - IT)**, and **IBPS SO (IT Officer)** exams.

The platform provides a comprehensive 6-stage, 21-chapter curriculum, 299+ categorized exam questions, an in-browser PDF library with PDF categorizer and viewer, and an AI Chatbot powered by **Google Gemini Embeddings & RAG** with source citations.

---

## Key Highlights

- **Scholarly & Bookish UI:** Designed for focused, distraction-free reading with Paper, Pure White, and Night themes, readable serif/sans typography, adjustable font sizes, and chapter progress tracking.
- **21 Comprehensive Technical Chapters:** Spanning DBMS, Operating Systems, Networking, Data Structures & Algorithms, Software Engineering, Cloud & Security, Banking Regulations, and Python.
- **PDF Library & Document Categorization:** Upload external PDFs or import from local workspace collections. Categorize as *Study Material*, *Question Bank*, *Previous Year Paper*, or *Syllabus / Regulations*.
- **Integrated PDF Reader:** Read PDFs directly in-browser side-by-side with the AI assistant.
- **RAG & Vector Search Engine:**
  - Extracts and chunks documents with page-level metadata.
  - Generates 768-dimensional vector embeddings using Google GenAI (`text-embedding-004`).
  - Employs zero-dependency SQLite vector BLOB storage and fast NumPy cosine similarity search with term-overlap scoring.
  - AI Assistant (`gemini-2.5-flash`) answers questions based on uploaded documents with clickable page citations.
  - Graceful fallback mode ensures all viewer and search features function even before an API key is supplied.
- **Self-Contained Architecture:** Single SQLite database (`data/study_portal.db`) for all user notes, reading progress, quiz scores, uploaded documents, vector chunks, and chat history.

---

## Directory Layout

```
prep_platform/
├── backend/
│   ├── server.py              # FastAPI application, REST endpoints, static file server
│   ├── db.py                  # SQLite schema, vector chunk persistence, chat storage
│   ├── rag_engine.py          # Google Embeddings & RAG service, NumPy cosine similarity
│   └── pdf_manager.py         # PDF text extraction, chunking, and metadata parsing
├── static/
│   ├── index.html             # Academic study interface with split-screen PDF/Chat workspace
│   ├── app.js                 # Frontend application, reactive tabs, chat stream, PDF viewer
│   └── styles.css             # Book-like styling, serif/sans switches, responsive grid
├── data/
│   ├── curriculum.json        # 6 Stages, 21 Chapters with comprehensive study material
│   ├── extracted_qas.json     # 299+ parsed technical multiple-choice questions
│   ├── study_portal.db        # SQLite database (documents, vectors, chat, progress)
│   └── uploads/               # Managed document storage folder
├── .env.example               # Template environment configuration
├── requirements.txt           # Python dependencies
├── run_server.py              # Launcher script
└── start_server.bat           # Windows one-click batch launcher
```

---

## Quickstart Guide

### 1. Requirements

- Python 3.10+ (tested on Python 3.14)
- Google Gemini API key (optional for offline features, required for live AI RAG)

### 2. Setup

Clone the repository and install the dependencies:

```bash
git clone <repository-url>
cd prep_platform
python -m pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your Google Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
HOST=127.0.0.1
```

*(Note: You can also set or change the Gemini API key anytime directly inside the web UI by clicking the Settings icon).*

### 4. Running the Server

Run via Python:

```bash
python run_server.py
```

Or on Windows:

```cmd
start_server.bat
```

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

---

## API Overview

- `GET /api/curriculum` - Full curriculum hierarchy and reading chapters.
- `GET /api/documents` - List uploaded and indexed PDFs with category filtering.
- `POST /api/documents/upload` - Upload and vectorize a new PDF document.
- `GET /api/documents/workspace-available` - Scan workspace directories for existing study PDFs.
- `POST /api/documents/import-workspace` - Ingest and index a workspace PDF.
- `GET /api/documents/{id}/raw` - Stream PDF for the browser viewer.
- `DELETE /api/documents/{id}` - Remove a document and its vector embeddings.
- `POST /api/chat` - Perform semantic RAG Q&A over selected documents.
- `GET /api/chat/history` - Retrieve prior conversation messages.
- `POST /api/settings/api-key` - Configure API key at runtime.
