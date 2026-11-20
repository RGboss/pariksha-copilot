"""
Automated Test Suite for Pariksha Copilot Extended Features:
- Flashcard Generation & Leitner Spaced Repetition Review
- Timed Mock Quiz (CBT Assessment) & Explanations
- Study Planner Tasks, Habit Streak & Statistics
- Strict Multi-User Security Isolation
"""

import uuid
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=== STARTING EXTENDED FEATURES TEST SUITE ===")

    # 1. Register User A
    uid = uuid.uuid4().hex[:6]
    email_a = f"aspirant.vikram.{uid}@portal.in"
    res_a = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "name": "Vikram Singh",
        "email": email_a,
        "password": "Password123!",
        "target_exam": "UPSC CSE 2027"
    })
    assert res_a.status_code == 200, f"Signup failed: {res_a.text}"
    token_a = res_a.json()["token"]
    user_a = res_a.json()["user"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"[1] Registered User A: {user_a['name']} ({email_a})")

    # 2. Test Flashcard Generation
    print("\n[2] Testing POST /api/flashcards/generate")
    fc_gen = requests.post(
        f"{BASE_URL}/api/flashcards/generate",
        headers=headers_a,
        json={"topic": "Fundamental Rights and Directive Principles", "count": 4, "category": "Polity"}
    )
    assert fc_gen.status_code == 200, f"Flashcard gen failed: {fc_gen.text}"
    fc_data = fc_gen.json()
    cards = fc_data["flashcards"]
    print(f"-> Generated {len(cards)} flashcards successfully!")
    assert len(cards) >= 1
    sample_card = cards[0]
    print(f"-> Sample Front: {sample_card['front_prompt']}")
    print(f"-> Sample Back: {sample_card['back_answer']}")

    # 3. Test Flashcard Listing
    print("\n[3] Testing GET /api/flashcards")
    fc_list = requests.get(f"{BASE_URL}/api/flashcards", headers=headers_a)
    assert fc_list.status_code == 200
    assert fc_list.json()["total"] == len(cards)
    print(f"-> Verified: Total saved cards: {fc_list.json()['total']}")

    # 4. Test Flashcard Leitner Spaced Review
    print("\n[4] Testing POST /api/flashcards/{id}/review")
    card_id = sample_card["id"]
    rev_res = requests.post(
        f"{BASE_URL}/api/flashcards/{card_id}/review",
        headers=headers_a,
        json={"rating": "good"}
    )
    assert rev_res.status_code == 200, f"Review failed: {rev_res.text}"
    updated_card = rev_res.json()["flashcard"]
    print(f"-> Card Box promoted to: {updated_card['mastery_level']}/5, Reviews: {updated_card['review_count']}")
    assert updated_card["mastery_level"] >= 1
    assert updated_card["review_count"] == 1

    # 5. Test Flashcard Markdown Export
    print("\n[5] Testing GET /api/flashcards/export")
    exp_res = requests.get(f"{BASE_URL}/api/flashcards/export", headers=headers_a)
    assert exp_res.status_code == 200
    md = exp_res.json()["markdown"]
    assert "High-Yield Study Flashcards Deck" in md
    print("-> Flashcard markdown export generated cleanly.")

    # 6. Test Mock Quiz Generation
    print("\n[6] Testing POST /api/quiz/generate")
    q_gen = requests.post(
        f"{BASE_URL}/api/quiz/generate",
        headers=headers_a,
        json={"topic": "Monetary Policy & Fiscal Responsibility", "exam_name": "SEBI / Banking", "question_count": 3}
    )
    assert q_gen.status_code == 200, f"Quiz gen failed: {q_gen.text}"
    quiz = q_gen.json()["quiz"]
    quiz_id = quiz["id"]
    print(f"-> Quiz Created: '{quiz['title']}' with {quiz['question_count']} questions.")
    assert quiz["question_count"] >= 1
    first_q = quiz["questions"][0]
    print(f"-> Sample Question: {first_q['question']}")
    print(f"-> Options: {first_q['options']}")
    print(f"-> Reference citation: Page {first_q.get('reference_page', 1)} of '{first_q.get('reference_doc')}'")

    # 7. Test Mock Quiz Submission & Grading
    print("\n[7] Testing POST /api/quiz/{id}/submit")
    # Provide answers: choose correct answer for first question, intentional distractor for second
    correct_idx = first_q["answer_index"]
    user_answers = {"0": correct_idx, "1": 3, "2": 2}
    sub_res = requests.post(
        f"{BASE_URL}/api/quiz/{quiz_id}/submit",
        headers=headers_a,
        json={"answers": user_answers, "time_spent_seconds": 145}
    )
    assert sub_res.status_code == 200, f"Submission failed: {sub_res.text}"
    attempt = sub_res.json()["attempt"]
    print(f"-> Attempt Scored: {attempt['score']} / {attempt['total_questions']} ({attempt['percentage']}%) in {attempt['time_spent_seconds']}s")
    assert "detailed_feedback" in attempt
    fb = attempt["detailed_feedback"][0]
    print(f"-> Detailed Feedback on Q1: Correct={fb['is_correct']}, Explanation: {fb['explanation'][:80]}...")
    assert fb["is_correct"] is True

    # 8. Test Quiz Listing
    print("\n[8] Testing GET /api/quiz")
    qz_list = requests.get(f"{BASE_URL}/api/quiz", headers=headers_a)
    assert qz_list.status_code == 200
    assert qz_list.json()["total"] >= 1
    print(f"-> Verified user quiz list: {qz_list.json()['total']} quizzes with recorded attempts.")

    # 9. Test Study Planner Tasks
    print("\n[9] Testing Study Planner Task Management")
    task_res = requests.post(
        f"{BASE_URL}/api/planner/tasks",
        headers=headers_a,
        json={"title": "Revise Laxmikanth Chapter 7 (Fundamental Rights)", "priority": "High", "category": "Polity"}
    )
    assert task_res.status_code == 200
    task1 = task_res.json()["task"]
    task1_id = task1["id"]
    print(f"-> Created task: '{task1['title']}', Priority: {task1['priority']}")

    task_res2 = requests.post(
        f"{BASE_URL}/api/planner/tasks",
        headers=headers_a,
        json={"title": "Solve 25 CSAT Quantitative Reasoning questions", "priority": "Medium", "category": "Aptitude"}
    )
    assert task_res2.status_code == 200

    # Toggle task
    tog_res = requests.post(f"{BASE_URL}/api/planner/tasks/{task1_id}/toggle", headers=headers_a)
    assert tog_res.status_code == 200
    assert tog_res.json()["task"]["is_completed"] is True
    print(f"-> Toggled task completion: is_completed = {tog_res.json()['task']['is_completed']}")

    # Get Planner Stats
    stats_res = requests.get(f"{BASE_URL}/api/planner/stats", headers=headers_a)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    print(f"-> Planner Stats: Total: {stats['total_tasks']}, Completed: {stats['completed_tasks']}, Rate: {stats['completion_rate']}%, Streak: {stats['streak_days']} days")
    assert stats["total_tasks"] == 2
    assert stats["completed_tasks"] == 1
    assert stats["completion_rate"] == 50.0

    # 10. Multi-User Isolation Verification
    print("\n[10] Testing Strict Multi-User Isolation")
    email_b = f"aspirant.kavita.{uid}@portal.in"
    res_b = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "name": "Kavita Rao",
        "email": email_b,
        "password": "Password123!",
        "target_exam": "RBI Grade B"
    })
    token_b = res_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B should have 0 flashcards, 0 quizzes, and 0 tasks
    b_fc = requests.get(f"{BASE_URL}/api/flashcards", headers=headers_b).json()
    b_qz = requests.get(f"{BASE_URL}/api/quiz", headers=headers_b).json()
    b_tsk = requests.get(f"{BASE_URL}/api/planner/tasks", headers=headers_b).json()

    assert b_fc["total"] == 0, f"User B saw User A's flashcards! {b_fc}"
    assert b_qz["total"] == 0, f"User B saw User A's quizzes! {b_qz}"
    assert b_tsk["total"] == 0, f"User B saw User A's tasks! {b_tsk}"
    print("-> Strict isolation confirmed: User B has 0 flashcards, 0 quizzes, and 0 tasks.")

    print("\n=== ALL EXTENDED FEATURE TESTS PASSED WITH 100% SUCCESS! ===")

if __name__ == "__main__":
    run_tests()
