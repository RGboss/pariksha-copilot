"""
Mock Quiz and Previous Year Questions (PYQ) Assessment Engine for Pariksha Copilot
Generates high-yield multiple choice tests with rationales and page citations.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.db_models import SessionLocal, Quiz, QuizAttempt, Document as DocModel
from backend.chroma_rag import rag_service

def generate_quiz_from_doc(
    user_id: str,
    document_id: Optional[str] = None,
    topic: Optional[str] = None,
    exam_name: str = "UPSC / Banking / Regulatory",
    question_count: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Generates a timed Computer-Based Test (CBT) mock quiz from document chunks or topic.
    """
    session = SessionLocal()
    try:
        doc_title = "Curriculum Review"
        doc_context = ""
        citation_doc = "Standard Syllabus"
        citation_page = 1

        if document_id:
            doc = session.query(DocModel).filter(DocModel.id == document_id, DocModel.user_id == user_id).first()
            if doc:
                doc_title = doc.filename
                citation_doc = doc.filename
                chunks = rag_service.query_relevant_chunks(
                    query_text=topic or "important provisions questions exam patterns facts",
                    user_id=user_id,
                    document_id=document_id,
                    top_k=5
                )
                if chunks:
                    citation_page = chunks[0].get("page", 1)
                    doc_context = "\n---\n".join([f"(Page {c.get('page', 1)}): {c.get('text', '')[:350]}" for c in chunks])

        if not doc_context:
            doc_context = f"Foundational concepts for {exam_name} focusing on {topic or 'Core syllabus topics'}."

        questions = []
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()

        if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                prompt = f"""You are a master examiner for Indian competitive examinations ({exam_name}).
Generate a mock test of exactly {question_count} high-standard multiple choice questions based on the reference excerpt below:

REFERENCE EXCERPT:
{doc_context[:2500]}

Respond ONLY with a valid JSON array of question objects with this schema:
[
  {{
    "question": "Clear, rigorous question stem",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer_index": 0,
    "explanation": "Detailed rationale explaining why the correct option is right and others are incorrect.",
    "reference_page": {citation_page},
    "reference_doc": "{citation_doc}"
  }}
]
"""
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                raw_text = resp.text.strip()
                match = re.search(r'\[.*\]', raw_text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    for q in parsed[:question_count]:
                        if len(q.get("options", [])) == 4 and "answer_index" in q:
                            questions.append(q)
            except Exception as e:
                print(f"[Quiz] Gemini quiz generation failed ({e}), using offline exam syllabus generator.")

        if not questions:
            questions = _generate_offline_quiz_questions(doc_title, citation_doc, citation_page, question_count)

        quiz = Quiz(
            user_id=user_id,
            document_id=document_id,
            title=f"Mock Test: {doc_title[:40]}",
            exam_name=exam_name,
            questions_json=json.dumps(questions),
            created_at=datetime.utcnow()
        )
        session.add(quiz)
        session.commit()
        session.refresh(quiz)
        return quiz.to_dict()
    finally:
        session.close()

def _generate_offline_quiz_questions(doc_title: str, citation_doc: str, citation_page: int, count: int) -> List[Dict[str, Any]]:
    """Generates standard scholarly MCQs with realistic distractors and citations."""
    templates = [
        {
            "question": f"According to the core principles discussed in '{doc_title}', what is the primary regulatory or operational requirement?",
            "options": [
                "Mandatory statutory compliance and transparent procedural oversight",
                "Complete exemption from periodic auditing protocols",
                "Ad-hoc decision making without documentation",
                "Immediate unilateral cessation of administrative guidelines"
            ],
            "answer_index": 0,
            "explanation": "Indian administrative and regulatory doctrines prioritize procedural transparency, accountability, and statutory compliance.",
            "reference_page": citation_page,
            "reference_doc": citation_doc
        },
        {
            "question": f"Which of the following best characterizes the analytical approach recommended in '{doc_title}'?",
            "options": [
                "Multi-dimensional stakeholder assessment and risk mitigation",
                "Superficial heuristic evaluations without empirical benchmarks",
                "Strict adherence to outdated obsolete statutes",
                "Ignoring macro-economic indicators during implementation"
            ],
            "answer_index": 0,
            "explanation": "Standard exam answers require evaluating multidimensional impacts, constitutional limits, and risk parameters.",
            "reference_page": citation_page,
            "reference_doc": citation_doc
        },
        {
            "question": f"In competitive exam answer writing regarding '{doc_title}', which structural element carries the highest weightage?",
            "options": [
                "Merely memorizing dates and isolated trivia",
                "Substantiating claims with constitutional articles, case laws, or official economic data",
                "Writing long unstructured narrative paragraphs",
                "Omitting the critical challenges or counter-perspectives"
            ],
            "answer_index": 1,
            "explanation": "High scoring candidates substantiate their arguments with constitutional doctrines, committee reports, and empirical data.",
            "reference_page": citation_page,
            "reference_doc": citation_doc
        },
        {
            "question": "Under standard Indian financial regulations and fiscal federalism, which institution holds constitutional authority for tax distribution?",
            "options": [
                "The Finance Commission (Article 280)",
                "The Central Board of Direct Taxes (CBDT)",
                "The Securities and Exchange Board of India (SEBI)",
                "The Department of Telecommunications"
            ],
            "answer_index": 0,
            "explanation": "Article 280 mandates the President of India to constitute the Finance Commission every five years for recommendations on tax devolution.",
            "reference_page": 1,
            "reference_doc": "Indian Polity & Governance"
        },
        {
            "question": "What is the primary role of the Monetary Policy Committee (MPC) in the Reserve Bank of India framework?",
            "options": [
                "Formulate and decide the policy repo rate to maintain price stability while supporting growth",
                "Directly manage equity share prices on the National Stock Exchange",
                "Appoint civil service officers to the Cabinet Secretariat",
                "Supervise district-level revenue collection"
            ],
            "answer_index": 0,
            "explanation": "The 6-member MPC sets the policy repo rate to target inflation within the 4% (+/- 2%) band under the RBI Act, 1934.",
            "reference_page": 1,
            "reference_doc": "Indian Financial System"
        }
    ]
    return templates[:count]

def submit_quiz_attempt(
    user_id: str,
    quiz_id: str,
    answers: Dict[str, int],
    time_spent_seconds: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Grades user submission against the answer key, computes accuracy, and saves attempt.
    """
    session = SessionLocal()
    try:
        quiz = session.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return None

        questions = json.loads(quiz.questions_json or "[]")
        total = len(questions)
        score = 0
        feedback = []

        for idx, q in enumerate(questions):
            user_choice = answers.get(str(idx))
            is_correct = (user_choice == q["answer_index"])
            if is_correct:
                score += 1

            feedback.append({
                "question_index": idx,
                "question": q["question"],
                "options": q["options"],
                "user_choice": user_choice,
                "correct_choice": q["answer_index"],
                "is_correct": is_correct,
                "explanation": q.get("explanation", ""),
                "reference_page": q.get("reference_page", 1),
                "reference_doc": q.get("reference_doc", "")
            })

        percentage = (score / total * 100.0) if total > 0 else 0.0

        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            total_questions=total,
            percentage=percentage,
            time_spent_seconds=time_spent_seconds,
            answers_json=json.dumps(answers),
            completed_at=datetime.utcnow()
        )
        session.add(attempt)
        session.commit()
        session.refresh(attempt)

        result = attempt.to_dict()
        result["detailed_feedback"] = feedback
        return result
    finally:
        session.close()

def get_user_quizzes(user_id: str) -> List[Dict[str, Any]]:
    """Returns all created quizzes with attempt history for user."""
    session = SessionLocal()
    try:
        quizzes = session.query(Quiz).filter(Quiz.id.isnot(None)).order_by(Quiz.created_at.desc()).all()
        # Filter for user_id
        user_quizzes = [q for q in quizzes if q.user_id == user_id]
        results = []
        for q in user_quizzes:
            q_dict = q.to_dict()
            attempts = session.query(QuizAttempt).filter(QuizAttempt.quiz_id == q.id, QuizAttempt.user_id == user_id).order_by(QuizAttempt.completed_at.desc()).all()
            q_dict["attempts"] = [a.to_dict() for a in attempts]
            results.append(q_dict)
        return results
    finally:
        session.close()
