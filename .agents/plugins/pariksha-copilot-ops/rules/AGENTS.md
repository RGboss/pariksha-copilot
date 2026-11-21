# Pariksha Copilot Operational Rules & Architectural Guardrails

## 1. Network & Port Architecture
- **Primary Gateway:** The application is exposed to users and external clients strictly via the **Nginx Reverse Proxy on port `8082:80`** (`http://localhost:8082`).
- **Backend Internal Port:** The FastAPI application (`main:app`) runs internally on port `8000`. Do not expose port 8000 directly to host networks in production mode.
- **Healthcheck Endpoints:**
  - `GET http://localhost:8082/health` — Container healthcheck (returns `{"status": "healthy"}`).
  - `GET http://localhost:8082/api/health` — Application metadata (returns `{"status": "ok", "app": "pariksha-copilot", "version": "2.3.0"}`).

## 2. Persistent Storage Architecture (CRITICAL: Never Wipe)
- All persistent data is managed through Docker named volumes (or `/app/data/` bind mounts):
  - `pariksha_sqlite_data` mounted at `/app/data`: Contains SQLite database `gov_exam_portal.db` (candidate accounts, study planner tasks, flashcards, mock quizzes).
  - `pariksha_chroma_data` mounted at `/app/data/chroma_db`: Contains ChromaDB persistent vector index and embeddings.
  - `pariksha_uploads_data` mounted at `/app/data/uploads`: Contains uploaded PDF textbooks organized by candidate ID and category.
- **Safety Directive:** NEVER delete, overwrite, format, or recreate these volume directories without explicit human authorization. Preserving candidate test history, flashcards, and uploaded books across restarts is mandatory.

## 3. Secret & Credential Protection
- Never commit `.env` files or hardcode API keys (`GEMINI_API_KEY`, `POSTGRES_PASSWORD`) into Dockerfiles, code repositories, or chat artifacts.
- Keep `.env` strictly in `.dockerignore` and `.gitignore`.
- Reference secrets solely via environment variables loaded by `docker compose --env-file .env` or `env_file`.

## 4. API Resilience & Model Fallback
- All Gemini API interactions must maintain exponential backoff retry logic.
- If Gemini returns `503 UNAVAILABLE` or `429 TOO_MANY_REQUESTS`, gracefully fall back through candidate models (`gemini-2.5-flash` -> `gemini-2.5-pro` -> `gemini-1.5-flash` -> `gemini-1.5-pro` -> Offline deterministic fallback).
- Never allow an external API error to crash the user request.
