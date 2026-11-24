import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

print("=" * 70)
print("  PARIKSHA COPILOT - IN-PROCESS REGRESSION TEST SUITE (MAIN BRANCH)")
print("=" * 70)

results = []

def test_case(name, fn):
    t0 = time.time()
    try:
        ok, msg = fn()
        elapsed = time.time() - t0
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name} ({elapsed:.2f}s) - {msg}", flush=True)
        results.append({"name": name, "status": status, "elapsed": elapsed, "detail": msg})
    except Exception as e:
        elapsed = time.time() - t0
        import traceback
        tb = traceback.format_exc()
        print(f"[FAIL] {name} ({elapsed:.2f}s) - Exception: {e}", flush=True)
        print(tb)
        results.append({"name": name, "status": "FAIL", "elapsed": elapsed, "detail": str(e), "traceback": tb})

# 1. Healthcheck tests
def test_root_health():
    resp = client.get("/health")
    return resp.status_code == 200 and resp.json().get("status") == "healthy", f"Status {resp.status_code}, Body: {resp.text}"

def test_api_health():
    resp = client.get("/api/health")
    return resp.status_code == 200 and resp.json().get("app") == "pariksha-copilot", f"Status {resp.status_code}, Body: {resp.text}"

def test_models():
    resp = client.get("/api/models")
    data = resp.json()
    models = data.get("models", [])
    return resp.status_code == 200 and len(models) >= 4, f"Found {len(models)} models: {[m['id'] for m in models]}"

test_case("Root Health /health", test_root_health)
test_case("API Health /api/health", test_api_health)
test_case("Model Catalog /api/models", test_models)

# 2. Authentication
AUTH_TOKEN = None

def test_demo_login():
    global AUTH_TOKEN
    payload = {
        "email": "rahul.aspirant@examportal.in",
        "password": "DemoPassword123"
    }
    resp = client.post("/api/auth/login", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        AUTH_TOKEN = data.get("token")
        user = data.get("user", {})
        return True, f"Logged in as {user.get('name')}, token prefix: {AUTH_TOKEN[:10]}..."
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Aspirant Demo Login /api/auth/login", test_demo_login)

def test_auth_me():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    resp = client.get("/api/auth/me", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        user_info = data.get("user", data)
        return user_info.get("email") == "rahul.aspirant@examportal.in", f"Verified aspirant: {user_info.get('name')}, Exam: {user_info.get('target_exam')}"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Session Verification /api/auth/me", test_auth_me)

# 3. Workspace PDF Scanning
WORKSPACE_PDFS = []

def test_workspace_pdf_scanner():
    global WORKSPACE_PDFS
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    resp = client.get("/api/documents/workspace-available", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        WORKSPACE_PDFS = data.get("available", [])
        return len(WORKSPACE_PDFS) > 0, f"Discovered {len(WORKSPACE_PDFS)} PDFs in workspace folders"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Workspace PDF Scanner /api/documents/workspace-available", test_workspace_pdf_scanner)

# 4. Import Workspace PDF to ChromaDB
IMPORTED_DOC_ID = None

def test_import_workspace_pdf():
    global IMPORTED_DOC_ID
    if not AUTH_TOKEN or not WORKSPACE_PDFS:
        return False, "Skipped - no auth token or no PDFs"
    
    # Find DBMS or Networking PDF
    chosen = None
    for p in WORKSPACE_PDFS:
        if "DBMS_and_SQL" in p["filename"] or "Computer_Networks" in p["filename"]:
            chosen = p
            break
    if not chosen:
        chosen = WORKSPACE_PDFS[0]
        
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    data = {
        "full_path": chosen["full_path"],
        "category": chosen.get("suggested_category", "Study Material")
    }
    resp = client.post("/api/documents/import-workspace", data=data, headers=headers)
    if resp.status_code == 200:
        doc = resp.json()
        IMPORTED_DOC_ID = doc.get("id")
        return True, f"Imported '{doc.get('original_filename')}' -> Doc ID: {IMPORTED_DOC_ID}, Pages: {doc.get('page_count')}, Chunks: {doc.get('chunk_count')}, Chars: {doc.get('extracted_chars')}"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Import Workspace PDF & Index in ChromaDB", test_import_workspace_pdf)

# 5. Direct Upload PDF (Multipart)
UPLOADED_DOC_ID = None

def test_upload_pdf_multipart():
    global UPLOADED_DOC_ID
    if not AUTH_TOKEN or not WORKSPACE_PDFS:
        return False, "Skipped - no auth token or no PDFs"
    
    # Pick a different PDF for direct upload test
    chosen = None
    for p in WORKSPACE_PDFS:
        if "Computer_Networks" in p["filename"] or "Operating_Systems" in p["filename"]:
            chosen = p
            break
    if not chosen:
        chosen = WORKSPACE_PDFS[-1]
        
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    with open(chosen["full_path"], "rb") as f:
        file_bytes = f.read()
        
    files = {"file": (chosen["filename"], file_bytes, "application/pdf")}
    data = {"category": "Technical Revision"}
    resp = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    if resp.status_code == 200:
        doc = resp.json()
        UPLOADED_DOC_ID = doc.get("id")
        return True, f"Uploaded '{doc.get('original_filename')}' -> Doc ID: {UPLOADED_DOC_ID}, Chunks: {doc.get('chunk_count')}"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Direct Multipart PDF Upload /api/documents/upload", test_upload_pdf_multipart)

# 6. List Documents
def test_list_documents():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    resp = client.get("/api/documents", headers=headers)
    if resp.status_code == 200:
        docs = resp.json().get("documents", [])
        return len(docs) >= 1, f"User has {len(docs)} documents registered"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("List Documents /api/documents", test_list_documents)

# 7. Document Raw Content (Served inline as application/pdf for viewer)
def test_document_raw():
    doc_id = IMPORTED_DOC_ID or UPLOADED_DOC_ID
    if not AUTH_TOKEN or not doc_id:
        return False, "Skipped - no document"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    resp = client.get(f"/api/documents/{doc_id}/raw", headers=headers)
    if resp.status_code == 200:
        content_type = resp.headers.get("content-type", "")
        if "application/pdf" in content_type and resp.content.startswith(b"%PDF"):
            return True, f"Raw PDF served inline ({len(resp.content):,} bytes, Content-Type: {content_type})"
        return False, f"Unexpected response format: Content-Type={content_type}, length={len(resp.content)}"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Document Raw Text /api/documents/{id}/raw", test_document_raw)

# 8. AI Chat (Document Mode with RAG Citations)
def test_chat_document_mode():
    doc_id = IMPORTED_DOC_ID or UPLOADED_DOC_ID
    if not AUTH_TOKEN or not doc_id:
        return False, "Skipped - no document"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "message": "Explain the key concepts, definitions, and rules detailed in this study material",
        "mode": "document",
        "document_id": doc_id,
        "model": "offline-curriculum",
        "category": "All"
    }
    resp = client.post("/api/chat", json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        sources = data.get("sources", [])
        return len(data.get("response", "")) > 10, f"Model: {data.get('model')}, Sources cited: {len(sources)}, Response snippet: {data.get('response')[:100]}..."
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("AI Chat (Document RAG Mode with Citations)", test_chat_document_mode)

# 9. AI Chat (General Faculty Mentor Mode)
def test_chat_general_mode():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "message": "What is the recommended 60-day study strategy for SEBI Grade A IT Officer?",
        "mode": "general",
        "model": "offline-curriculum",
        "category": "All"
    }
    resp = client.post("/api/chat", json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return len(data.get("response", "")) > 10, f"Model: {data.get('model')}, Response snippet: {data.get('response')[:100]}..."
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("AI Chat (General Faculty Mentor Mode)", test_chat_general_mode)

# 10. Chat History
def test_chat_history():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    resp = client.get("/api/chat/history", headers=headers)
    if resp.status_code == 200:
        messages = resp.json().get("messages", [])
        return len(messages) >= 2, f"Retrieved {len(messages)} persisted chat interactions"
    return False, f"Status {resp.status_code}, Body: {resp.text}"

test_case("Chat History Persistence /api/chat/history", test_chat_history)

# 11. Flashcards Generation & Review
def test_flashcards():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    doc_id = IMPORTED_DOC_ID or UPLOADED_DOC_ID
    
    # Generate
    gen_payload = {
        "document_id": doc_id,
        "topic": "Core IT Exam Concepts",
        "count": 3,
        "category": "High-Yield Facts"
    }
    resp = client.post("/api/flashcards/generate", json=gen_payload, headers=headers)
    if resp.status_code != 200:
        return False, f"Generation failed: Status {resp.status_code}, Body: {resp.text}"
    cards = resp.json().get("flashcards", [])
    
    # List
    resp_list = client.get("/api/flashcards", headers=headers)
    all_cards = resp_list.json().get("flashcards", [])
    if not all_cards:
        return False, "No cards in list after generation"
        
    # Review
    card_id = all_cards[0]["id"]
    resp_rev = client.post(f"/api/flashcards/{card_id}/review", json={"rating": "good"}, headers=headers)
    if resp_rev.status_code != 200:
        return False, f"Review failed: Status {resp_rev.status_code}"
    updated = resp_rev.json().get("flashcard", {})
    return True, f"Generated {len(cards)} cards, total {len(all_cards)}, reviewed card {card_id} -> new box: {updated.get('box')}"

test_case("Flashcards Generation, Spaced Repetition & Leitner Review", test_flashcards)

# 12. Quiz Generation & Submission
def test_quiz():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    doc_id = IMPORTED_DOC_ID or UPLOADED_DOC_ID
    
    # Generate
    quiz_payload = {
        "document_id": doc_id,
        "topic": "Computer Networks and Database Systems",
        "exam_name": "SEBI Grade A (IT Stream)",
        "question_count": 3
    }
    resp = client.post("/api/quiz/generate", json=quiz_payload, headers=headers)
    if resp.status_code != 200:
        return False, f"Quiz generation failed: Status {resp.status_code}, Body: {resp.text}"
    quiz = resp.json().get("quiz", {})
    quiz_id = quiz.get("id")
    questions = quiz.get("questions", [])
    if not questions:
        return False, "Quiz generated without questions"
        
    # Submit attempt
    answers = {str(i): 0 for i in range(len(questions))}
    submit_payload = {"answers": answers, "time_spent_seconds": 30}
    resp_sub = client.post(f"/api/quiz/{quiz_id}/submit", json=submit_payload, headers=headers)
    if resp_sub.status_code != 200:
        return False, f"Quiz submit failed: Status {resp_sub.status_code}"
    attempt = resp_sub.json()
    return True, f"Quiz {quiz_id} created with {len(questions)} questions. Attempt submitted -> Score: {attempt.get('score')}/{attempt.get('total_questions')} ({attempt.get('percentage')}%)"

test_case("Quiz Generation, MCQ Formatting & Attempt Grading", test_quiz)

# 13. Study Planner Tasks & Stats
def test_planner():
    if not AUTH_TOKEN:
        return False, "Skipped - no auth token"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Create Task
    task_payload = {
        "title": "Complete 30 Questions on Normalization (1NF to BCNF)",
        "description": "Focus on lossless join and dependency preservation",
        "category": "Practice",
        "priority": "High"
    }
    resp = client.post("/api/planner/tasks", json=task_payload, headers=headers)
    if resp.status_code != 200:
        return False, f"Task create failed: Status {resp.status_code}"
    task = resp.json().get("task", {})
    task_id = task.get("id")
    
    # Toggle Task
    resp_tog = client.post(f"/api/planner/tasks/{task_id}/toggle", headers=headers)
    if resp_tog.status_code != 200:
        return False, f"Task toggle failed: Status {resp_tog.status_code}"
        
    # Stats
    resp_stats = client.get("/api/planner/stats", headers=headers)
    stats = resp_stats.json()
    return True, f"Created and toggled task {task_id}. Stats: {stats}"

test_case("Study Planner Tasks, Toggle & Completion Stats", test_planner)

# 14. Static Web SPA Delivery & Routing
def test_spa_routes():
    routes = ["/", "/strategy", "/documents", "/planner", "/flashcards"]
    all_ok = True
    details = []
    for r in routes:
        resp = client.get(r)
        has_html = resp.status_code == 200 and ("<!doctype html>" in resp.text.lower() or "<div id=\"root\">" in resp.text.lower())
        details.append(f"{r}: {resp.status_code} (HTML: {has_html})")
        if not has_html:
            all_ok = False
    return all_ok, ", ".join(details)

test_case("SPA Static Delivery & Client-Side Route Fallbacks", test_spa_routes)

# Summary
pass_cnt = sum(1 for r in results if r["status"] == "PASS")
fail_cnt = sum(1 for r in results if r["status"] == "FAIL")

print("\n" + "=" * 70)
print(f"  REGRESSION SUITE COMPLETED: {pass_cnt} PASSED, {fail_cnt} FAILED (Total: {len(results)})")
print("=" * 70)

report_md = "# Pariksha Copilot - Web Regression Test Report\n\n"
report_md += f"**Execution Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
report_md += f"**Overall Result:** {pass_cnt}/{len(results)} Passed ({fail_cnt} Failed)\n\n"
report_md += "| Test Case | Status | Duration | Details |\n"
report_md += "| :--- | :---: | :---: | :--- |\n"
for r in results:
    report_md += f"| {r['name']} | **{r['status']}** | {r['elapsed']:.2f}s | {r['detail']} |\n"

with open(os.path.join(BASE_DIR, "WEB_REGRESSION_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(report_md)
print("Report saved to WEB_REGRESSION_REPORT.md")

if fail_cnt > 0:
    sys.exit(1)
