---
name: pariksha-doctor
description: Diagnoses and inspects Pariksha Copilot health, container status, Docker logs, PDF ingestion, ChromaDB vector retrieval, and Gemini API quota/503/429 errors.
---

# Pariksha Doctor (`/pariksha-doctor`)

Runbook and automated diagnostic procedure to inspect, troubleshoot, and heal the Pariksha Copilot application stack running on `http://localhost:8082` (or standalone `http://localhost:8000`).

---

## 1. Quick Diagnostic Checklist

When the user triggers `/pariksha-doctor` or requests diagnostics:

### Step 1: Probe Gateway & Backend Health
Execute an HTTP check against the primary gateway and internal endpoints:
```powershell
# Probe Nginx Gateway
try {
    $res = Invoke-RestMethod -Uri "http://localhost:8082/api/health" -TimeoutSec 5
    Write-Host "[Doctor] Nginx Gateway (8082): ONLINE - Version $($res.version)"
} catch {
    Write-Host "[Doctor] Nginx Gateway (8082): OFFLINE or UNREACHABLE"
}

# Probe Direct Backend
try {
    $res2 = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "[Doctor] Direct Backend (8000): ONLINE - Version $($res2.version)"
} catch {
    Write-Host "[Doctor] Direct Backend (8000): OFFLINE"
}
```

### Step 2: Check Docker Container Lifecycle
```bash
docker compose ps
```
Verify that:
- `pariksha_backend` is in status `healthy`.
- `pariksha_frontend` is in status `running` or `healthy` on port `8082:80`.
- Named volumes (`pariksha_sqlite_data`, `pariksha_chroma_data`, `pariksha_uploads_data`) are mounted.

### Step 3: Scan Logs for Gemini API Quota & 503 / 429 Errors
```bash
docker compose logs --tail=100 backend | Select-String -Pattern "503|429|RESOURCE_EXHAUSTED|UNAVAILABLE|API_KEY_INVALID"
```
If errors are detected:
- Confirm whether exponential backoff retried successfully.
- Verify candidate fallback models (`gemini-2.5-flash` -> `gemini-2.5-pro` -> `gemini-1.5-flash` -> `gemini-1.5-pro` -> Offline syllabus doctrine).
- Advise user if their `GEMINI_API_KEY` quota is exhausted or needs renewal.

### Step 4: Verify Persistent Storage & ChromaDB Vector Index
Inspect data directory and vector store:
```powershell
python -c "
import os
from backend.db_models import SessionLocal, User, Document
from backend.chroma_rag import rag_service

session = SessionLocal()
u_count = session.query(User).count()
d_count = session.query(Document).count()
session.close()

c_count = rag_service.collection.count()
print(f'[Doctor] SQLite: {u_count} registered users, {d_count} indexed documents.')
print(f'[Doctor] ChromaDB: {c_count} embedded vector chunks in collection.')
"
```

---

## 2. Self-Healing & Remediation Runbook

| Symptom | Root Cause | Immediate Remediation |
| :--- | :--- | :--- |
| **Port 8082 Connection Refused** | Nginx container stopped or port conflict | Run `docker compose restart frontend` or `.\scripts\windows-startup\start-pariksha-copilot.ps1`. |
| **Docker Daemon not running** | Docker Desktop stopped or WSL2 disabled | Start Docker Desktop or run fallback server `python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000`. |
| **Uploads 413 Payload Too Large** | PDF exceeds body limit | Verify `client_max_body_size 50M;` is active in `nginx/nginx.conf`. |
| **Gemini 503 UNAVAILABLE** | High Google API server load | The application auto-retries with exponential backoff and falls back to offline syllabus doctrines. |
| **Empty RAG Answers** | Zero chunks returned from ChromaDB | Check document index status via `rag_service.collection.count()`. Re-index PDF if needed. |
