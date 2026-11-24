"""
Pariksha Copilot - Complete End-to-End Feature Regression Test Suite
Validates all features against the live web server running on http://127.0.0.1:8082
"""

import os
import sys
import time
import uuid
import json
import httpx

BASE_URL = os.environ.get("TARGET_URL", "http://127.0.0.1:8082")
print("=" * 75)
print(f"  PARIKSHA COPILOT - COMPLETE WEB FEATURE REGRESSION SUITE")
print(f"  Target Server: {BASE_URL}")
print("=" * 75)

client = httpx.Client(base_url=BASE_URL, timeout=60.0)

results = []

def run_test(name, func):
    t0 = time.time()
    try:
        ok, details = func()
        dur = time.time() - t0
        status = "PASS" if ok else "FAIL"
        results.append({
            "name": name,
            "status": status,
            "duration": f"{dur:.2f}s",
            "details": details
        })
        print(f"[{status}] {name} ({dur:.2f}s) - {details[:100]}...")
    except Exception as e:
        dur = time.time() - t0
        results.append({
            "name": name,
            "status": "FAIL",
            "duration": f"{dur:.2f}s",
            "details": f"Exception: {str(e)}"
        })
        print(f"[FAIL] {name} ({dur:.2f}s) - Exception: {e}")

# -------------------------------------------------------------
# 1. Health & Server Metadata
# -------------------------------------------------------------
def test_container_health():
    r = client.get("/health")
    return r.status_code == 200 and r.json().get("status") == "healthy", f"Status: {r.status_code}, Body: {r.text}"

def test_api_health():
    r = client.get("/api/health")
    data = r.json()
    return r.status_code == 200 and data.get("app") == "pariksha-copilot", f"App: {data.get('app')}, Version: {data.get('version')}"

def test_models_catalog():
    r = client.get("/api/models")
    data = r.json()
    models = data.get("models", [])
    model_ids = [m["id"] for m in models]
    return len(models) >= 4 and "offline-curriculum" in model_ids, f"Available models ({len(models)}): {model_ids}"

run_test("1. Container Healthcheck /health", test_container_health)
run_test("2. Application API Metadata /api/health", test_api_health)
run_test("3. Model Catalog & Zero-Quota Engine /api/models", test_models_catalog)

# -------------------------------------------------------------
# 2. Authentication & User Profile Life-Cycle
# -------------------------------------------------------------
AUTH_TOKEN = None
USER_ID = None
TEST_EMAIL = f"test.candidate.{uuid.uuid4().hex[:6]}@aspirant.gov.in"

def test_user_signup():
    global AUTH_TOKEN, USER_ID
    payload = {
        "name": "Regression Candidate",
        "email": TEST_EMAIL,
        "password": "SecurePassword#2026",
        "target_exam": "SEBI Grade A (IT Stream)"
    }
    r = client.post("/api/auth/signup", json=payload)
    if r.status_code == 200:
        data = r.json()
        AUTH_TOKEN = data.get("token")
        USER_ID = data.get("user", {}).get("id")
        return True, f"User created: {USER_ID}, token prefix: {AUTH_TOKEN[:10]}..."
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_user_login():
    global AUTH_TOKEN
    payload = {
        "email": TEST_EMAIL,
        "password": "SecurePassword#2026"
    }
    r = client.post("/api/auth/login", json=payload)
    if r.status_code == 200:
        AUTH_TOKEN = r.json().get("token")
        return True, f"Re-authenticated successfully with token: {AUTH_TOKEN[:10]}..."
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_auth_me():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get("/api/auth/me", headers=headers)
    if r.status_code == 200:
        u = r.json().get("user", {})
        return u.get("email") == TEST_EMAIL, f"Verified aspirant: {u.get('name')} | Exam: {u.get('target_exam')}"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_update_profile():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "name": "Candidate Officer Rank 1",
        "target_exam": "IBPS SO IT Officer",
        "preferred_model": "offline-curriculum"
    }
    r = client.put("/api/user", json=payload, headers=headers)
    if r.status_code == 200:
        u = r.json()
        return u.get("target_exam") == "IBPS SO IT Officer" and u.get("preferred_model") == "offline-curriculum", f"Updated to {u.get('name')} | Exam: {u.get('target_exam')} | Model: {u.get('preferred_model')}"
    return False, f"Status: {r.status_code}, Body: {r.text}"

run_test("4. Aspirant Signup /api/auth/signup", test_user_signup)
run_test("5. Aspirant Login /api/auth/login", test_user_login)
run_test("6. Current Aspirant Profile /api/auth/me", test_auth_me)
run_test("7. Update Profile & Target Exam /api/user", test_update_profile)

# -------------------------------------------------------------
# 3. Topper's Strategy Blueprint
# -------------------------------------------------------------
def test_generate_strategy():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "exam_name": "IBPS SO IT Officer",
        "daily_hours": 5.0,
        "prep_level": "Intermediate",
        "model": "offline-curriculum"
    }
    r = client.post("/api/strategy/generate", json=payload, headers=headers)
    if r.status_code == 200:
        data = r.json()
        plan_md = data.get("strategy_markdown", "")
        return len(plan_md) > 100, f"Strategy generated ({len(plan_md)} chars), preview: {plan_md[:80]}..."
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_strategy_history():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get("/api/strategy/history", headers=headers)
    if r.status_code == 200:
        plans = r.json()
        return len(plans) >= 1, f"Retrieved {len(plans)} persisted study blueprints"
    return False, f"Status: {r.status_code}, Body: {r.text}"

run_test("8. AI Exam Strategy Blueprint /api/strategy/generate", test_generate_strategy)
run_test("9. Strategy History & Audit Trail /api/strategy/history", test_strategy_history)

# -------------------------------------------------------------
# 4. Study Vault & Real PDF Management
# -------------------------------------------------------------
WORKSPACE_PDFS = []
IMPORTED_DOC_ID = None

def test_workspace_available():
    global WORKSPACE_PDFS
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get("/api/documents/workspace-available", headers=headers)
    if r.status_code == 200:
        data = r.json()
        WORKSPACE_PDFS = data.get("available", [])
        return len(WORKSPACE_PDFS) >= 50, f"Found {len(WORKSPACE_PDFS)} PDFs across categories: {list(data.get('categories', {}).keys())}"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_import_workspace_pdf():
    global IMPORTED_DOC_ID
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    # Pick a high-yield study notes PDF
    target_pdf = None
    for p in WORKSPACE_PDFS:
        if "DBMS" in p["filename"]:
            target_pdf = p
            break
    if not target_pdf and WORKSPACE_PDFS:
        target_pdf = WORKSPACE_PDFS[0]
        
    payload = {
        "full_path": target_pdf.get("full_path") or target_pdf.get("rel_path"),
        "category": target_pdf.get("suggested_category", "Study Material")
    }
    r = client.post("/api/documents/import-workspace", json=payload, headers=headers, timeout=180.0)
    if r.status_code == 200:
        doc = r.json()
        IMPORTED_DOC_ID = doc["id"]
        return True, f"Imported '{doc['original_filename']}' (Pages: {doc.get('page_count')}, Chunks: {doc.get('chunk_count')}, Size: {doc.get('file_size'):,} bytes)"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_document_list_and_search():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    # List all
    r = client.get("/api/documents", headers=headers)
    if r.status_code != 200:
        return False, f"List failed: {r.status_code}"
    total = r.json().get("total", 0)
    
    # Search
    r_search = client.get("/api/documents?search=DBMS", headers=headers)
    found = len(r_search.json().get("documents", []))
    return total >= 1 and found >= 1, f"Total vault documents: {total}, Search matches for 'DBMS': {found}"

def test_document_raw_inline():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get(f"/api/documents/{IMPORTED_DOC_ID}/raw", headers=headers)
    if r.status_code == 200:
        ct = r.headers.get("content-type", "")
        return "application/pdf" in ct and r.content.startswith(b"%PDF"), f"Served binary PDF ({len(r.content):,} bytes, Content-Type: {ct})"
    return False, f"Status: {r.status_code}, Body: {r.text}"

run_test("10. Workspace PDF Scanner /api/documents/workspace-available", test_workspace_available)
run_test("11. 1-Click Import & Vector Indexing /api/documents/import-workspace", test_import_workspace_pdf)
run_test("12. Vault List & Filename Search /api/documents", test_document_list_and_search)
run_test("13. Inline PDF Viewer Streaming /api/documents/{id}/raw", test_document_raw_inline)

# -------------------------------------------------------------
# 5. Interactive Reading Desk & Document RAG Q&A
# -------------------------------------------------------------
def test_document_rag_chat():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "message": "Explain relational database normalization, Boyce-Codd Normal Form (BCNF), and ACID transactions",
        "mode": "document",
        "document_id": IMPORTED_DOC_ID,
        "model": "offline-curriculum",
        "category": "All"
    }
    r = client.post("/api/chat", json=payload, headers=headers)
    if r.status_code == 200:
        data = r.json()
        ans = data.get("answer") or data.get("response") or ""
        sources = data.get("sources", [])
        return len(ans) > 50 and len(sources) > 0, f"Answer length: {len(ans)} chars, Sources cited: {len(sources)} (Top: {sources[0].get('filename')}, Page {sources[0].get('page')})"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_faculty_mentor_chat():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "message": "What is the strategic weightage of System Analysis and Design vs RDBMS in IBPS SO IT Mains?",
        "mode": "general",
        "model": "offline-curriculum",
        "category": "All"
    }
    r = client.post("/api/chat", json=payload, headers=headers)
    if r.status_code == 200:
        data = r.json()
        ans = data.get("answer") or data.get("response") or ""
        return len(ans) > 50, f"Mentor advice generated: {ans[:80]}..."
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_chat_history_and_clear():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    # Check history
    r = client.get(f"/api/chat/history?document_id={IMPORTED_DOC_ID}", headers=headers)
    if r.status_code != 200:
        return False, f"History fetch failed: {r.status_code}"
    msgs = r.json().get("messages", [])
    if len(msgs) < 2:
        return False, f"Expected at least 2 messages in history, found {len(msgs)}"
        
    # Clear history
    r_del = client.delete(f"/api/chat/history?document_id={IMPORTED_DOC_ID}", headers=headers)
    if r_del.status_code != 200:
        return False, f"Clear history failed: {r_del.status_code}"
        
    # Verify cleared
    r_verify = client.get(f"/api/chat/history?document_id={IMPORTED_DOC_ID}", headers=headers)
    remaining = len(r_verify.json().get("messages", []))
    return remaining == 0, f"History had {len(msgs)} messages; cleared successfully (remaining: {remaining})"

run_test("14. Document RAG Chat with Page Citations /api/chat", test_document_rag_chat)
run_test("15. 24/7 Faculty Mentor General Guidance /api/chat", test_faculty_mentor_chat)
run_test("16. Chat History Auto-Save & Reset /api/chat/history", test_chat_history_and_clear)

# -------------------------------------------------------------
# 6. Active Recall Flashcards & Leitner Spaced Repetition
# -------------------------------------------------------------
FLASHCARD_ID = None

def test_flashcard_generation():
    global FLASHCARD_ID
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "document_id": IMPORTED_DOC_ID,
        "topic": "High-Yield DBMS & SQL Facts",
        "count": 4,
        "category": "High-Yield Facts"
    }
    r = client.post("/api/flashcards/generate", json=payload, headers=headers)
    if r.status_code == 200:
        cards = r.json().get("flashcards", [])
        if cards:
            FLASHCARD_ID = cards[0]["id"]
            return True, f"Generated {len(cards)} flashcards from document. Card 1: {cards[0].get('front')[:60]}..."
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_flashcard_leitner_review():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    # Review with 'good'
    r1 = client.post(f"/api/flashcards/{FLASHCARD_ID}/review", json={"rating": "good"}, headers=headers)
    if r1.status_code != 200:
        return False, f"Review rating 'good' failed: {r1.status_code}"
    box_after_good = r1.json().get("flashcard", {}).get("box") or r1.json().get("flashcard", {}).get("mastery_level")
    
    # Review with 'again'
    r2 = client.post(f"/api/flashcards/{FLASHCARD_ID}/review", json={"rating": "again"}, headers=headers)
    if r2.status_code != 200:
        return False, f"Review rating 'again' failed: {r2.status_code}"
    box_after_again = r2.json().get("flashcard", {}).get("box") if r2.json().get("flashcard", {}).get("box") is not None else r2.json().get("flashcard", {}).get("mastery_level")
    
    return (box_after_good == 1 or box_after_good == 2) and (box_after_again == 0 or box_after_again == 1), f"Leitner progression verified: initial -> box {box_after_good} ('good') -> reset to box {box_after_again} ('again')"

def test_flashcard_export():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get("/api/flashcards/export", headers=headers)
    if r.status_code == 200:
        cards = r.json()
        return len(cards) >= 1, f"Exported {len(cards)} cards in portable format"
    return False, f"Status: {r.status_code}, Body: {r.text}"

run_test("17. Spaced Repetition Flashcard Generation /api/flashcards/generate", test_flashcard_generation)
run_test("18. Leitner 5-Box Interval Review Engine /api/flashcards/{id}/review", test_flashcard_leitner_review)
run_test("19. Flashcard Deck Export /api/flashcards/export", test_flashcard_export)

# -------------------------------------------------------------
# 7. Mock Exam & CBT Simulator
# -------------------------------------------------------------
QUIZ_ID = None
QUIZ_QUESTIONS = []

def test_quiz_generation():
    global QUIZ_ID, QUIZ_QUESTIONS
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "document_id": IMPORTED_DOC_ID,
        "topic": "SQL Queries, Primary Keys and Relational Algebra",
        "exam_name": "IBPS SO IT Officer",
        "question_count": 4
    }
    r = client.post("/api/quiz/generate", json=payload, headers=headers)
    if r.status_code == 200:
        quiz = r.json().get("quiz", {})
        QUIZ_ID = quiz.get("id")
        QUIZ_QUESTIONS = quiz.get("questions", [])
        return len(QUIZ_QUESTIONS) == 4, f"Generated CBT Quiz ({QUIZ_ID}) with {len(QUIZ_QUESTIONS)} MCQs. Q1: {QUIZ_QUESTIONS[0].get('question')[:60]}..."
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_quiz_submission_and_scoring():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    # Formulate responses (choose option 0 for each question)
    answers = {str(i): 0 for i in range(len(QUIZ_QUESTIONS))}
    payload = {
        "answers": answers,
        "time_spent_seconds": 45
    }
    r = client.post(f"/api/quiz/{QUIZ_ID}/submit", json=payload, headers=headers)
    if r.status_code == 200:
        res = r.json().get("attempt") or r.json()
        score = res.get("score")
        total = res.get("total_questions")
        pct = res.get("percentage")
        feedback = res.get("feedback", [])
        has_citations = any(f.get("citation") for f in feedback)
        return total == 4, f"Score: {score}/{total} ({pct}%), Evaluated {len(feedback)} questions with question-level rationales (Has citations: {has_citations})"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_quiz_history():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.get("/api/quiz", headers=headers)
    if r.status_code == 200:
        quizzes = r.json().get("quizzes", [])
        return len(quizzes) >= 1, f"Found {len(quizzes)} past mock assessments in candidate dossier"
    return False, f"Status: {r.status_code}, Body: {r.text}"

run_test("20. Mock Exam & CBT Question Generation /api/quiz/generate", test_quiz_generation)
run_test("21. Timed Attempt Submission & Assessment /api/quiz/{id}/submit", test_quiz_submission_and_scoring)
run_test("22. Candidate Past Quiz History /api/quiz", test_quiz_history)

# -------------------------------------------------------------
# 8. Daily Study Planner & Focus Desk
# -------------------------------------------------------------
PLANNER_TASK_ID = None

def test_planner_create_task():
    global PLANNER_TASK_ID
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {
        "title": "Revise BCNF vs 3NF Lossless Join Decomposition",
        "description": "Solve 20 Mains numerical problems from question bank",
        "category": "Revision",
        "priority": "High"
    }
    r = client.post("/api/planner/tasks", json=payload, headers=headers)
    if r.status_code == 200:
        t = r.json().get("task", {})
        PLANNER_TASK_ID = t.get("id")
        return bool(t.get("is_completed")) is False or bool(t.get("completed")) is False, f"Created High-Priority task: {t.get('title')} (ID: {PLANNER_TASK_ID})"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_planner_toggle_and_stats():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    # Toggle to complete
    r_tog = client.post(f"/api/planner/tasks/{PLANNER_TASK_ID}/toggle", headers=headers)
    if r_tog.status_code != 200:
        return False, f"Toggle failed: {r_tog.status_code}"
    is_completed = r_tog.json().get("task", {}).get("is_completed") or r_tog.json().get("task", {}).get("completed")
    
    # Check stats
    r_stats = client.get("/api/planner/stats", headers=headers)
    if r_stats.status_code != 200:
        return False, f"Stats failed: {r_stats.status_code}"
    stats = r_stats.json()
    return is_completed is True and stats.get("completed_tasks", 0) >= 1, f"Task completed: {is_completed} | Total: {stats.get('total_tasks')}, Completed: {stats.get('completed_tasks')}, Rate: {stats.get('completion_rate')}%"

def test_planner_delete_task():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    r = client.delete(f"/api/planner/tasks/{PLANNER_TASK_ID}", headers=headers)
    return r.status_code == 200 and r.json().get("status") == "success", f"Status: {r.status_code}, Deleted ID: {r.json().get('deleted_id')}"

run_test("23. Study Planner Task Creation /api/planner/tasks", test_planner_create_task)
run_test("24. Task Toggle & Productivity Analytics /api/planner/stats", test_planner_toggle_and_stats)
run_test("25. Task Cleanup & Deletion /api/planner/tasks/{id}", test_planner_delete_task)

# -------------------------------------------------------------
# 9. Curriculum Stages & Question Bank
# -------------------------------------------------------------
def test_curriculum_stages():
    r = client.get("/api/stages")
    if r.status_code == 200:
        stages = r.json().get("stages", [])
        return len(stages) >= 1, f"Found {len(stages)} official curriculum stages"
    return False, f"Status: {r.status_code}, Body: {r.text}"

def test_question_bank():
    r = client.get("/api/questions?limit=5&offset=0")
    if r.status_code == 200:
        data = r.json()
        return data.get("limit") == 5, f"Question bank pagination functional (Total: {data.get('total')}, returned: {len(data.get('questions', []))})"
    return False, f"Status: {r.status_code}, Body: {r.text}"

run_test("26. Curriculum Blueprint & Stages /api/stages", test_curriculum_stages)
run_test("27. Question Bank Pagination & Retrieval /api/questions", test_question_bank)

# -------------------------------------------------------------
# 10. Single-Page Application (SPA) Delivery & Routing
# -------------------------------------------------------------
def test_spa_client_routes():
    routes = ["/", "/strategy", "/documents", "/planner", "/flashcards", "/quiz"]
    all_ok = True
    details = []
    for route in routes:
        r = client.get(route)
        has_html = r.status_code == 200 and ("<!doctype html>" in r.text.lower() or "<div id=\"root\">" in r.text.lower())
        details.append(f"{route}: {r.status_code} (HTML: {has_html})")
        if not has_html:
            all_ok = False
    return all_ok, ", ".join(details)

run_test("28. SPA Routing & Client-Side URL Fallbacks", test_spa_client_routes)

# -------------------------------------------------------------
# Summary & Markdown Report Generation
# -------------------------------------------------------------
pass_count = sum(1 for r in results if r["status"] == "PASS")
fail_count = sum(1 for r in results if r["status"] == "FAIL")

print("\n" + "=" * 75)
print(f"  FEATURE REGRESSION COMPLETED: {pass_count} PASSED, {fail_count} FAILED (Total: {len(results)})")
print("=" * 75)

report = "# Pariksha Copilot - Complete Web Feature Regression Report\n\n"
report += f"**Target Base URL:** `{BASE_URL}`\n"
report += f"**Execution Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
report += f"**Overall Result:** **{pass_count}/{len(results)} Passed** ({fail_count} Failed)\n"
report += f"**Success Rate:** {(pass_count / len(results) * 100):.1f}%\n\n"
report += "### Feature-by-Feature Results Matrix\n\n"
report += "| # | Feature / Endpoint | Status | Latency | Verification Details |\n"
report += "| :--- | :--- | :---: | :---: | :--- |\n"
for i, r in enumerate(results, 1):
    badge = "**PASS**" if r["status"] == "PASS" else "<span style='color:red;'>FAIL</span>"
    report += f"| {i} | {r['name']} | {badge} | {r['duration']} | {r['details']} |\n"

report += "\n---\n*Report generated by automated regression runner against live Pariksha Copilot instance.*"

report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FULL_FEATURE_REGRESSION_REPORT.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)
print(f"Detailed Markdown report generated: {report_path}")

sys.exit(0 if fail_count == 0 else 1)
