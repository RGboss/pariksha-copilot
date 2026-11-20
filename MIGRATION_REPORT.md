# 📋 Migration Report: Pariksha Copilot Docker + Nginx Containerization

**Date:** November 20, 2026  
**Application:** Pariksha Copilot (परीक्षा Copilot) - v2.3.0  
**Repository:** [https://github.com/RGboss/pariksha-copilot.git](https://github.com/RGboss/pariksha-copilot.git)  
**Host Target:** Docker Compose Stack with Nginx Gateway on Port **8082:80**

---

## 1. Executive Summary

This report documents the containerization and production hardening of **Pariksha Copilot**, migrating the full-stack AI platform to a containerized multi-service architecture powered by **Docker Compose**, **Nginx Reverse Proxy**, and **Gunicorn + Uvicorn Workers**.

All project deliverables have been achieved:
1. **Hardened Backend Container:** Multi-worker Gunicorn server (`gunicorn -k uvicorn.workers.UvicornWorker -w 2 --timeout 180 -b 0.0.0.0:8000 main:app`), non-root execution (`appuser:1000`), container health checks (`GET /health`), and configurable persistence paths via environment variables.
2. **Nginx Reverse Proxy & Static Gateway:** Multi-stage frontend build (`node:lts-alpine` -> `nginx:alpine`) with SPA client-side routing fallback (`try_files $uri $uri/ /index.html;`), 50MB payload limits for large PDF textbooks, reverse proxies for `/api/`, `/health`, and `/uploads/` with 180s timeouts, gzip compression, and security headers.
3. **Persistent Volume Architecture:** Named Docker volumes ensuring zero data loss across container restarts for SQLite databases (`gov_exam_portal.db`), ChromaDB persistent vector embeddings (`/app/data/chroma_db`), and uploaded PDF textbooks (`/app/data/uploads`).
4. **Isolated Orchestration:** Isolated Docker network (`pariksha-copilot-net`), backend service kept internal-only, Nginx exposed on port **`8082:80`**, and robust service health dependency checking.
5. **Zero-Regression Test Suite:** Automated verification covering healthchecks, user authentication, data isolation, PyMuPDF extraction, ChromaDB RAG, Leitner flashcards, CBT mock quizzes, and study planner tasks with 100% pass rate.

---

## 2. Architecture & Service Topology

```
                      Internet / Browser Traffic
                                  │
                                  ▼
               ┌───────────────────────────────────────┐
               │    Host Port 8082 (Nginx Alpine)      │
               │  - client_max_body_size: 50M          │
               │  - Gzip Compression                   │
               │  - Security Headers (X-Frame, X-XSS)  │
               │  - SPA Fallback: /index.html          │
               └──────────────────┬────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │ Reverse Proxy (/api, /uploads)  │
                 │ Timeout: 180s                   │
                 ▼                                 ▼
      ┌───────────────────────┐         ┌───────────────────────┐
      │  React Static Assets  │         │  FastAPI Backend      │
      │  (Compiled Vite SPA)  │         │  Gunicorn (2 Workers) │
      └───────────────────────┘         │  Port 8000 (Internal) │
                                        └──────────┬────────────┘
                                                   │
                   ┌───────────────────────────────┴───────────────────────────────┐
                   ▼                               ▼                               ▼
       ┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
       │     sqlite_data       │       │      chroma_data      │       │     uploads_data      │
       │   (/app/data/*.db)    │       │ (/app/data/chroma_db) │       │ (/app/data/uploads/*) │
       └───────────────────────┘       └───────────────────────┘       └───────────────────────┘
```

---

## 3. Container & Service Specifications

### A. Backend Service (`backend/Dockerfile` & `Dockerfile.backend`)
- **Base Image:** `python:3.12-slim`
- **System Dependencies:** `curl` (for healthchecks), `build-essential`, `libpq-dev` (for PostgreSQL `psycopg2` driver).
- **Process Manager:** Gunicorn 21.2.0 executing Uvicorn async workers:
  ```bash
  gunicorn -k uvicorn.workers.UvicornWorker -w 2 --timeout 180 -b 0.0.0.0:8000 main:app
  ```
- **Security:** Non-root execution under user `appuser` (UID 1000), owning `/app/data` and `/app/uploads`.
- **Healthcheck:**
  ```dockerfile
  HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
      CMD curl -f http://localhost:8000/health || exit 1
  ```
- **Environment Paths:**
  - `DATABASE_URL`: Defaults to `sqlite:////app/data/gov_exam_portal.db` (or PostgreSQL connection string when set).
  - `CHROMA_PERSIST_DIR`: Defaults to `/app/data/chroma_db`.
  - `UPLOAD_DIR`: Defaults to `/app/data/uploads`.
  - `DATA_DIR`: Defaults to `/app/data`.

### B. Frontend Service (`frontend/Dockerfile` & `Dockerfile.frontend`)
- **Multi-Stage Build:**
  - **Stage 1 (Builder):** `node:lts-alpine` running `npm ci` and `npm run build` with Vite.
  - **Stage 2 (Runtime):** `nginx:alpine` serving compiled assets from `/usr/share/nginx/html`.
- **Nginx Configuration (`nginx/nginx.conf`):**
  - **Client Request Limit:** `client_max_body_size 50M;` to support multi-hundred-page textbooks.
  - **SPA Fallback:** `try_files $uri $uri/ /index.html;` preventing HTTP 404s on browser reloads.
  - **Timeouts:** `proxy_read_timeout 180s;` and `proxy_send_timeout 180s;` for long-running RAG inference.
  - **Security Headers:**
    - `X-Frame-Options: SAMEORIGIN`
    - `X-Content-Type-Options: nosniff`
    - `X-XSS-Protection: 1; mode=block`
    - `Referrer-Policy: strict-origin-when-cross-origin`
  - **Gzip:** Active for `text/plain`, `text/css`, `application/json`, `application/javascript`, `image/svg+xml`.

### C. Orchestration (`docker-compose.yml`)
- **Project Name:** `pariksha-copilot`
- **Network:** `pariksha-copilot-net` (custom bridge driver).
- **Service Dependency:** `frontend` waits on `backend: { condition: service_healthy }`.
- **Port Mapping:** Exposes port **`8082:80`** on host; backend remains strictly internal.

---

## 4. Persistent Volume Layout

| Named Volume | Container Mount Path | Stored Data |
| :--- | :--- | :--- |
| `pariksha_sqlite_data` | `/app/data` | Primary SQLite database (`gov_exam_portal.db`), user accounts, session tokens, flashcards, quizzes, and planner tasks. |
| `pariksha_chroma_data` | `/app/data/chroma_db` | Persistent ChromaDB vector collections, chunk index metadata, and embeddings. |
| `pariksha_uploads_data` | `/app/data/uploads` | Uploaded PDF textbooks organized by candidate ID and category. |
| `pariksha_postgres_data` | `/var/lib/postgresql/data` | PostgreSQL cluster data files (active when using PostgreSQL). |

---

## 5. Automated Verification Results

All core features and container endpoints were validated via automated end-to-end integration tests:

| Test Suite Component | Tested Behavior | Status |
| :--- | :--- | :---: |
| **Health Check (`GET /health`)** | Root healthcheck returning `{"status": "healthy"}` for Docker daemon | ✅ PASS |
| **App Status (`GET /api/health`)** | Application metadata returning `{"status": "ok", "version": "2.3.0"}` | ✅ PASS |
| **User Authentication** | Signup, login, PBKDF2-HMAC password hashing, and Bearer session tokens | ✅ PASS |
| **Candidate Data Isolation** | Candidate Alpha's study planner tasks verified invisible to Candidate Beta | ✅ PASS |
| **PyMuPDF Document Ingestion** | PDF upload, SHA-256 deduplication, TOC extraction, and semantic chunking | ✅ PASS |
| **Vector RAG Persistence** | ChromaDB vector indexing and fallback pseudo-vector resilience | ✅ PASS |
| **Leitner Flashcard Engine** | Spaced repetition card generation, box promotion (Box 0 -> Box 1), and export | ✅ PASS |
| **CBT Mock Exam Simulator** | MCQ exam generation, submission grading, score reporting (100%), and rationale storage | ✅ PASS |
| **Frontend Production Build** | Vite production bundle compilation (`dist/assets/index-*.js`, gzip: 90.81 kB) | ✅ PASS |

---

## 6. How to Deploy

### Option 1: Docker Compose (Recommended)
```bash
# 1. Clone repository
git clone https://github.com/RGboss/pariksha-copilot.git
cd pariksha-copilot

# 2. Configure environment
cp .env.example .env
# Set your GEMINI_API_KEY in .env

# 3. Build and launch containers in background
docker compose up --build -d

# 4. Access the platform
# Web UI & Gateway: http://localhost:8082
# Health Endpoint:  http://localhost:8082/health
```

### Option 2: Standalone Local Run
```bash
python -m pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
python run_server.py
# Web UI: http://localhost:8000
```
