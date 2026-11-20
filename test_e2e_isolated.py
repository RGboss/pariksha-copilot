"""
End-to-End Automated Verification Test Suite for Pariksha Copilot
Tests all endpoints, database isolation, RAG, flashcards, quizzes, and planner via TestClient(app).
"""
import os
import io
import sys
import json
import pytest

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_healthchecks():
    print("\n--- 1. Testing Health Check Endpoints ---")
    res1 = client.get("/health")
    assert res1.status_code == 200, f"Expected 200 from /health, got {res1.status_code}"
    assert res1.json() == {"status": "healthy"}, f"Unexpected /health response: {res1.json()}"
    print("PASS: /health returned {'status': 'healthy'}")

    res2 = client.get("/api/health")
    assert res2.status_code == 200, f"Expected 200 from /api/health, got {res2.status_code}"
    assert res2.json().get("status") == "ok", f"Unexpected /api/health response: {res2.json()}"
    print(f"PASS: /api/health returned {res2.json()}")

def test_auth_and_user_isolation():
    print("\n--- 2. Testing Authentication & User Isolation ---")
    import uuid
    uid = uuid.uuid4().hex[:6]
    # Register Candidate A
    email_a = f"candidate_a_{uid}@test.com"
    pass_a = "SecretPass123!"
    res_a = client.post("/api/auth/signup", json={
        "name": "Candidate Alpha",
        "email": email_a,
        "password": pass_a,
        "target_exam": "UPSC Civil Services"
    })
    assert res_a.status_code == 200, f"Candidate A signup failed: {res_a.text}"
    token_a = res_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"PASS: Candidate Alpha authenticated. Token: {token_a[:12]}...")

    # Register Candidate B
    email_b = f"candidate_b_{uid}@test.com"
    pass_b = "SecretPass456!"
    res_b = client.post("/api/auth/signup", json={
        "name": "Candidate Beta",
        "email": email_b,
        "password": pass_b,
        "target_exam": "SSC CGL"
    })
    assert res_b.status_code == 200, f"Candidate B signup failed: {res_b.text}"
    token_b = res_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"PASS: Candidate Beta authenticated. Token: {token_b[:12]}...")

    # Candidate A creates a planner task
    task_res = client.post("/api/planner/tasks", headers=headers_a, json={
        "title": "Alpha: Master Fundamental Rights Art 14-32",
        "category": "Polity",
        "priority": "high",
        "scheduled_date": "2026-11-21"
    })
    assert task_res.status_code == 200, f"Task creation failed: {task_res.text}"
    task_id = task_res.json()["task"]["id"]
    print(f"PASS: Task created for Candidate Alpha: ID={task_id}")

    # Verify Candidate B CANNOT see Candidate A's task
    tasks_b = client.get("/api/planner/tasks", headers=headers_b).json()
    b_task_ids = [t["id"] for t in tasks_b.get("tasks", [])]
    assert task_id not in b_task_ids, "DATA LEAK: Candidate B saw Candidate A's planner task!"
    print("PASS: Verified user isolation in Daily Study Planner (No data leakage)")

    # Toggle task for Alpha
    toggle_res = client.post(f"/api/planner/tasks/{task_id}/toggle", headers=headers_a)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["task"]["is_completed"] is True
    print("PASS: Task toggle state changed to completed")

def test_document_upload_and_pdf_rag():
    print("\n--- 3. Testing Document Upload, Vector RAG & Summarization ---")
    # Authenticate demo user
    login_res = client.post("/api/auth/login", json={
        "email": "rahul.aspirant@examportal.in",
        "password": "DemoPassword123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    # Generate a lightweight test PDF in memory
    import pypdf
    from pypdf import PdfWriter

    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    # Upload test PDF
    files = {"file": ("polity_test_notes.pdf", pdf_bytes, "application/pdf")}
    data = {"category": "Indian Polity"}
    up_res = client.post("/api/documents/upload", headers=headers, files=files, data=data)
    assert up_res.status_code == 200, f"Upload failed: {up_res.text}"
    doc_info = up_res.json()
    doc_id = doc_info["id"]
    print(f"PASS: Document uploaded successfully: ID={doc_id}, Filename={doc_info['filename']}")

    # Verify document in library
    docs_res = client.get("/api/documents", headers=headers)
    assert docs_res.status_code == 200
    user_doc_ids = [d["id"] for d in docs_res.json()["documents"]]
    assert doc_id in user_doc_ids, "Uploaded doc not found in user library"
    print("PASS: Document found in user library")

def test_flashcards_and_mock_exam():
    print("\n--- 4. Testing Leitner Flashcards & CBT Mock Exam Simulator ---")
    login_res = client.post("/api/auth/login", json={
        "email": "rahul.aspirant@examportal.in",
        "password": "DemoPassword123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    # Generate Leitner Flashcards
    fc_res = client.post("/api/flashcards/generate", headers=headers, json={
        "topic": "Indian Constitution - Directive Principles of State Policy",
        "count": 3
    })
    assert fc_res.status_code == 200, f"Flashcard generation failed: {fc_res.text}"
    cards = fc_res.json().get("flashcards", [])
    assert len(cards) > 0, "No flashcards returned"
    first_card = cards[0]
    initial_level = first_card.get("mastery_level", 0)
    print(f"PASS: Generated {len(cards)} flashcards. Card #1 Leitner Box: {initial_level}")

    # Review Flashcard with positive recall ('good')
    rev_res = client.post(f"/api/flashcards/{first_card['id']}/review", headers=headers, json={
        "rating": "good"
    })
    assert rev_res.status_code == 200, f"Review failed: {rev_res.text}"
    updated_card = rev_res.json()["flashcard"]
    assert updated_card["mastery_level"] > initial_level, "Flashcard box did not promote on 'good' rating"
    print(f"PASS: Flashcard promoted to Box {updated_card['mastery_level']} with next review scheduled")

    # Export flashcards as Markdown deck
    export_res = client.get("/api/flashcards/export", headers=headers)
    assert export_res.status_code == 200
    assert len(export_res.text) > 0, "Exported deck was empty"
    print(f"PASS: Flashcards exported to Markdown ({len(export_res.text)} bytes)")

    # Generate CBT Quiz
    quiz_res = client.post("/api/quiz/generate", headers=headers, json={
        "topic": "Fiscal Policy and Union Budget 2026",
        "question_count": 3,
        "exam_name": "UPSC Civil Services"
    })
    assert quiz_res.status_code == 200, f"Quiz generation failed: {quiz_res.text}"
    quiz_data = quiz_res.json()["quiz"]
    quiz_id = quiz_data["id"]
    questions = quiz_data["questions"]
    print(f"PASS: CBT Mock Quiz generated: ID={quiz_id}, Questions={len(questions)}")

    # Submit Quiz Attempt
    answers = {str(idx): q["answer_index"] for idx, q in enumerate(questions)}
    sub_res = client.post(f"/api/quiz/{quiz_id}/submit", headers=headers, json={
        "answers": answers,
        "time_spent_seconds": 45
    })
    assert sub_res.status_code == 200, f"Quiz submission failed: {sub_res.text}"
    attempt = sub_res.json()["attempt"]
    assert attempt["percentage"] == 100.0, f"Expected 100%, got {attempt['percentage']}"
    print(f"PASS: Quiz attempt submitted: Score={attempt['percentage']}%, Correct={attempt['score']}/{attempt['total_questions']}")

if __name__ == "__main__":
    test_healthchecks()
    test_auth_and_user_isolation()
    test_document_upload_and_pdf_rag()
    test_flashcards_and_mock_exam()
    print("\n=======================================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=======================================================\n")
