"""
Flashcard Generation & Leitner Spaced Repetition Engine for Pariksha Copilot
Supports AI-driven extraction (Gemini) and offline rule-based semantic extraction from documents.
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from backend.db_models import SessionLocal, Flashcard, Document as DocModel
from backend.chroma_rag import rag_service

LEITNER_INTERVALS = {
    0: timedelta(days=1),     # Box 0: Daily review
    1: timedelta(days=2),     # Box 1: Every 2 days
    2: timedelta(days=4),     # Box 2: Every 4 days
    3: timedelta(days=7),     # Box 3: Weekly
    4: timedelta(days=14),    # Box 4: Fortnightly
    5: timedelta(days=30),    # Box 5: Monthly (Mastered)
}

def generate_flashcards_from_doc(
    user_id: str,
    document_id: Optional[str] = None,
    topic: Optional[str] = None,
    count: int = 5,
    category: str = "High-Yield Facts"
) -> List[Dict[str, Any]]:
    """
    Generates structured flashcards from an uploaded document or topic.
    Extracts high-yield constitutional provisions, economic metrics, or core principles.
    """
    session = SessionLocal()
    try:
        doc_text = ""
        doc_name = "Study Syllabus"
        if document_id:
            doc = session.query(DocModel).filter(DocModel.id == document_id, DocModel.user_id == user_id).first()
            if doc:
                doc_name = doc.filename
                # Fetch relevant chunks
                chunks = rag_service.query_relevant_chunks(
                    query_text=topic or "key concepts formulas definitions summary facts",
                    user_id=user_id,
                    document_id=document_id,
                    top_k=6
                )
                if chunks:
                    doc_text = "\n---\n".join([c.get("text", "")[:400] for c in chunks])

        if not doc_text:
            doc_text = f"Key exam preparation syllabus concepts for {topic or 'Indian Governance and Economics'}."

        cards_data = []

        # Try Google Gemini if configured
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                prompt = f"""You are an elite exam preparation mentor. Generate exactly {count} high-yield revision flashcards for competitive exam aspirants based on the following text:
                
SOURCE TEXT:
{doc_text[:2500]}

Respond ONLY with a valid JSON array of objects with the exact keys:
[
  {{
    "front_prompt": "Question or prompt testing active recall (e.g. What is Article 32 of the Indian Constitution?)",
    "back_answer": "Concise, definitive answer with key keywords.",
    "difficulty": "Easy" | "Medium" | "Hard"
  }}
]
"""
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                raw_text = resp.text.strip()
                match = re.search(r'\[.*\]', raw_text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    for item in parsed[:count]:
                        cards_data.append({
                            "front_prompt": item.get("front_prompt", "").strip(),
                            "back_answer": item.get("back_answer", "").strip(),
                            "difficulty": item.get("difficulty", "Medium")
                        })
            except Exception as e:
                print(f"[Flashcard] Gemini generation failed ({e}), falling back to offline generator.")

        # Fallback offline generator if Gemini didn't return cards
        if not cards_data:
            cards_data = _generate_offline_flashcards(doc_text, doc_name, count)

        # Persist cards to DB
        saved_cards = []
        for c in cards_data:
            card = Flashcard(
                user_id=user_id,
                document_id=document_id,
                category=category,
                front_prompt=c["front_prompt"],
                back_answer=c["back_answer"],
                difficulty=c.get("difficulty", "Medium"),
                mastery_level=0,
                review_count=0,
                next_review_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            session.add(card)
            session.commit()
            session.refresh(card)
            saved_cards.append(card.to_dict())

        return saved_cards
    finally:
        session.close()

def _generate_offline_flashcards(text: str, doc_name: str, count: int) -> List[Dict[str, Any]]:
    """Heuristic offline flashcard extractor from document text."""
    cards = []
    # Extract sentences with key terms like is, defined as, refers to, provides, articles, metrics
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 30]
    
    defaults = [
        {
            "front_prompt": f"What is the primary objective outlined in {doc_name}?",
            "back_answer": f"Provides core conceptual foundations and syllabus directives detailed in {doc_name}.",
            "difficulty": "Easy"
        },
        {
            "front_prompt": f"Identify the key constitutional / statutory framework referenced in {doc_name}.",
            "back_answer": "Established statutory doctrines, regulatory compliance guidelines, and constitutional mandates.",
            "difficulty": "Medium"
        },
        {
            "front_prompt": f"What are the major high-yield revision points emphasized in {doc_name}?",
            "back_answer": "Procedural workflows, analytical criteria, and previous year exam trends.",
            "difficulty": "Hard"
        },
        {
            "front_prompt": f"How should an aspirant structure answers related to topics in {doc_name}?",
            "back_answer": "1. Definition & Context 2. Core Legal/Economic Provisions 3. Challenges 4. Way Forward.",
            "difficulty": "Medium"
        },
        {
            "front_prompt": f"What formula or quantitative metric is vital in {doc_name}?",
            "back_answer": "Ratio analysis, fiscal parameters, and statutory limit computations.",
            "difficulty": "Hard"
        }
    ]

    for i, line in enumerate(lines[:count]):
        # If line contains punctuation/semicolon, split into Q & A
        if ":" in line:
            parts = line.split(":", 1)
            cards.append({
                "front_prompt": f"Define / Explain: {parts[0].strip()}",
                "back_answer": parts[1].strip()[:200],
                "difficulty": "Medium"
            })
        elif "?" in line:
            parts = line.split("?", 1)
            cards.append({
                "front_prompt": f"{parts[0].strip()}?",
                "back_answer": parts[1].strip()[:200] if parts[1].strip() else "Refer to textbook section.",
                "difficulty": "Medium"
            })

    # Fill remainder from defaults
    while len(cards) < count:
        cards.append(defaults[len(cards) % len(defaults)])

    return cards[:count]

def review_flashcard(user_id: str, card_id: str, rating: str) -> Optional[Dict[str, Any]]:
    """
    Applies Leitner Spaced Repetition algorithm:
    rating options: 'again' (reset), 'hard' (slight advance), 'good' (+1 box), 'easy' (+2 boxes)
    """
    session = SessionLocal()
    try:
        card = session.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == user_id).first()
        if not card:
            return None

        current_box = card.mastery_level or 0
        if rating == "again":
            current_box = 0
        elif rating == "hard":
            current_box = max(0, current_box)
        elif rating == "good":
            current_box = min(5, current_box + 1)
        elif rating == "easy":
            current_box = min(5, current_box + 2)

        interval = LEITNER_INTERVALS.get(current_box, timedelta(days=1))
        card.mastery_level = current_box
        card.review_count = (card.review_count or 0) + 1
        card.next_review_at = datetime.utcnow() + interval

        session.commit()
        session.refresh(card)
        return card.to_dict()
    finally:
        session.close()

def get_user_flashcards(user_id: str, document_id: Optional[str] = None, due_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieves all flashcards or due flashcards for the user."""
    session = SessionLocal()
    try:
        query = session.query(Flashcard).filter(Flashcard.user_id == user_id)
        if document_id:
            query = query.filter(Flashcard.document_id == document_id)
        if due_only:
            query = query.filter(Flashcard.next_review_at <= datetime.utcnow())
        
        cards = query.order_by(Flashcard.next_review_at.asc()).all()
        return [c.to_dict() for c in cards]
    finally:
        session.close()
