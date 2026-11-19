import os
import json
import uuid
import shutil
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

from backend.db import (
    init_db,
    get_all_progress,
    update_chapter_progress,
    record_quiz_attempt,
    get_stats,
    list_documents,
    get_document,
    delete_document,
    get_chat_history,
    clear_chat_history,
    get_setting,
    set_setting
)
from backend.rag_engine import rag_service
from backend.pdf_manager import (
    process_and_index_pdf,
    scan_workspace_study_pdfs,
    import_workspace_pdf,
    UPLOADS_DIR
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Initialize SQLite database
init_db()

# Load Curriculum JSON
with open(os.path.join(DATA_DIR, 'curriculum.json'), 'r', encoding='utf-8') as f:
    CURRICULUM = json.load(f)

# Load Extracted Question Bank JSON
with open(os.path.join(DATA_DIR, 'extracted_qas.json'), 'r', encoding='utf-8') as f:
    QUESTION_BANK = json.load(f)

app = FastAPI(
    title="IT Officer Exam Prep Platform API with Gemini RAG",
    description="Backend API for SEBI Grade A, SBI SCO, and IBPS SO Progressive Preparation Hub with PDF Library & AI Tutor",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# PYDANTIC SCHEMAS
# ==============================================================

class ProgressUpdate(BaseModel):
    completed: Optional[bool] = None
    bookmarked: Optional[bool] = None
    notes: Optional[str] = None

class QuizSubmission(BaseModel):
    answers: Dict[str, int] # question_id (as str) -> selected_option_index

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    document_id: Optional[str] = None
    api_key: Optional[str] = None

class ApiKeyUpdate(BaseModel):
    api_key: str

class WorkspaceImportRequest(BaseModel):
    file_path: str
    category: Optional[str] = "Study Material"

# ==============================================================
# CURRICULUM & PROGRESS ENDPOINTS
# ==============================================================

@app.get("/api/stages")
def get_stages(exam: Optional[str] = None):
    """
    Returns all stages and chapters with current user progress and quiz scores.
    Optional filter by exam ('sebi', 'sbi', 'ibps').
    """
    progress_map, quiz_map = get_all_progress()
    
    stages_copy = []
    for stage in CURRICULUM["stages"]:
        filtered_chapters = []
        for ch in stage["chapters"]:
            if exam and exam != "all" and exam not in ch["exams"]:
                continue
            
            p = progress_map.get(ch["id"], {"completed": False, "bookmarked": False, "notes": ""})
            q = quiz_map.get(ch["id"], None)
            
            ch_summary = {
                "id": ch["id"],
                "stage_id": ch["stage_id"],
                "number": ch["number"],
                "title": ch["title"],
                "exams": ch["exams"],
                "reading_time_mins": ch["reading_time_mins"],
                "summary": ch["summary"],
                "completed": p["completed"],
                "bookmarked": p["bookmarked"],
                "quiz_score": q
            }
            filtered_chapters.append(ch_summary)
            
        if filtered_chapters or not exam:
            stages_copy.append({
                "id": stage["id"],
                "number": stage["number"],
                "title": stage["title"],
                "badge": stage["badge"],
                "description": stage["description"],
                "chapters": filtered_chapters
            })
            
    return {"stages": stages_copy}

@app.get("/api/chapters/{chapter_id}")
def get_chapter(chapter_id: str):
    """
    Returns full lesson details, notes, checkpoints, and embedded quiz.
    """
    found_ch = None
    stage_info = None
    for s in CURRICULUM["stages"]:
        for ch in s["chapters"]:
            if ch["id"] == chapter_id:
                found_ch = dict(ch)
                stage_info = {"id": s["id"], "number": s["number"], "title": s["title"]}
                break
        if found_ch:
            break
            
    if not found_ch:
        raise HTTPException(status_code=404, detail="Chapter not found")
        
    progress_map, quiz_map = get_all_progress()
    user_state = progress_map.get(chapter_id, {"completed": False, "bookmarked": False, "notes": ""})
    latest_quiz = quiz_map.get(chapter_id, None)
    
    found_ch["stage"] = stage_info
    found_ch["user_state"] = user_state
    found_ch["latest_quiz_score"] = latest_quiz
    return found_ch

@app.post("/api/chapters/{chapter_id}/progress")
def update_progress(chapter_id: str, update: ProgressUpdate):
    """
    Saves completion status, bookmarking, and personal notes into SQLite.
    """
    update_chapter_progress(
        chapter_id,
        completed=update.completed,
        bookmarked=update.bookmarked,
        notes=update.notes
    )
    return {"status": "success", "chapter_id": chapter_id}

@app.post("/api/chapters/{chapter_id}/quiz")
def submit_quiz(chapter_id: str, submission: QuizSubmission):
    """
    Evaluates submitted quiz answers, saves score in SQLite, and returns detailed explanations.
    """
    found_ch = None
    for s in CURRICULUM["stages"]:
        for ch in s["chapters"]:
            if ch["id"] == chapter_id:
                found_ch = ch
                break
        if found_ch:
            break
            
    if not found_ch:
        raise HTTPException(status_code=404, detail="Chapter not found")
        
    quiz_items = found_ch.get("quiz", [])
    total = len(quiz_items)
    correct_count = 0
    evaluations = []
    
    for item in quiz_items:
        qid_str = str(item["id"])
        user_choice = submission.answers.get(qid_str)
        is_correct = (user_choice == item["answer"])
        if is_correct:
            correct_count += 1
            
        evaluations.append({
            "id": item["id"],
            "question": item["q"],
            "options": item["options"],
            "correct_answer": item["answer"],
            "user_answer": user_choice,
            "is_correct": is_correct,
            "explanation": item["explanation"]
        })
        
    # Record in SQLite
    record_quiz_attempt(chapter_id, correct_count, total, submission.answers)
    
    pct = round((correct_count / total * 100.0), 1) if total > 0 else 0.0
    return {
        "chapter_id": chapter_id,
        "score": correct_count,
        "total": total,
        "percentage": pct,
        "evaluations": evaluations
    }

@app.get("/api/stats")
def get_user_stats():
    """
    Calculates overall progress, quiz metrics, and document library statistics.
    """
    total_chapters = CURRICULUM["stats"]["total_chapters"]
    return get_stats(total_chapters)

@app.get("/api/search")
def search_curriculum(q: str = Query(..., min_length=2)):
    """
    Searches across all chapters, lecture notes, checkpoints, and question banks.
    """
    query = q.lower()
    chapter_results = []
    
    for s in CURRICULUM["stages"]:
        for ch in s["chapters"]:
            match_title = query in ch["title"].lower()
            match_summary = query in ch["summary"].lower()
            match_notes = query in ch["lecture_notes"].lower()
            if match_title or match_summary or match_notes:
                chapter_results.append({
                    "type": "chapter",
                    "chapter_id": ch["id"],
                    "number": ch["number"],
                    "title": ch["title"],
                    "stage_title": s["title"],
                    "summary": ch["summary"],
                    "exams": ch["exams"]
                })
                
    qa_results = []
    for item in QUESTION_BANK:
        if query in item["question"].lower() or query in item["answer"].lower():
            qa_results.append(item)
            if len(qa_results) >= 20: # cap top 20
                break
                
    return {
        "query": q,
        "chapters": chapter_results,
        "questions": qa_results
    }

@app.get("/api/questions")
def get_questions(category: Optional[str] = None, limit: int = 50, offset: int = 0):
    """
    Returns extracted questions & answers from PDF question banks.
    """
    filtered = QUESTION_BANK
    if category and category != "all":
        filtered = [item for item in filtered if item["category"].lower() == category.lower()]
        
    paged = filtered[offset : offset + limit]
    return {
        "total": len(filtered),
        "limit": limit,
        "offset": offset,
        "questions": paged
    }

@app.get("/api/mock-exam")
def get_mock_exam(count: int = 30, exam: Optional[str] = None):
    """
    Returns a randomized set of calibrated quiz questions from across curriculum chapters.
    Supports filtering by target exam (sebi, sbi, ibps).
    """
    import random
    pool = []
    for s in CURRICULUM["stages"]:
        for ch in s["chapters"]:
            if exam and exam != "all" and exam not in ch.get("exams", []):
                continue
            for q in ch.get("quiz", []):
                pool.append({
                    "id": q["id"],
                    "q": q["q"],
                    "options": q["options"],
                    "answer": q["answer"],
                    "explanation": q["explanation"],
                    "chapterId": ch["id"],
                    "chapterTitle": ch["title"],
                    "chapterNumber": ch["number"],
                    "stageTitle": s["title"]
                })
    selected = random.sample(pool, min(count, len(pool))) if pool else []
    return {
        "count": len(selected),
        "total_available": len(pool),
        "exam_filter": exam or "all",
        "questions": selected
    }

# ==============================================================
# PDF LIBRARY & DOCUMENT MANAGEMENT ENDPOINTS
# ==============================================================

@app.get("/api/documents")
def get_documents(category: Optional[str] = None, search: Optional[str] = None):
    """
    Lists all uploaded study PDFs and question banks with metadata.
    """
    docs = list_documents(category=category, search=search)
    return {"total": len(docs), "documents": docs}

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Study Material")
):
    """
    Uploads a PDF, indexes it into chunks with vector embeddings, and generates an AI summary.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = str(uuid.uuid4())
    stored_filename = f"{doc_id}_{file.filename}"
    save_path = os.path.join(UPLOADS_DIR, stored_filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc = process_and_index_pdf(
            file_path=save_path,
            original_filename=file.filename,
            category=category,
            doc_id=doc_id
        )
        return {"status": "success", "document": doc}
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.get("/api/documents/workspace-available")
def get_available_workspace_pdfs():
    """
    Discovers all 51 IT Officer study PDFs located in the workspace directories.
    """
    pdfs = scan_workspace_study_pdfs()
    return {"total": len(pdfs), "pdfs": pdfs}

@app.post("/api/documents/import-workspace")
def import_from_workspace(req: WorkspaceImportRequest):
    """
    Imports and indexes an existing study PDF from the workspace.
    """
    try:
        doc = import_workspace_pdf(file_path=req.file_path, category=req.category)
        return {"status": "success", "document": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import workspace PDF: {str(e)}")

@app.get("/api/documents/{doc_id}")
def get_document_details(doc_id: str):
    """
    Returns document metadata and AI summary.
    """
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.get("/api/documents/{doc_id}/raw")
def get_document_raw(doc_id: str):
    """
    Serves the raw PDF file for in-browser viewing.
    """
    doc = get_document(doc_id)
    if not doc or not os.path.exists(doc["file_path"]):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(
        doc["file_path"],
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{doc["original_filename"]}"'}
    )

@app.delete("/api/documents/{doc_id}")
def delete_document_endpoint(doc_id: str):
    """
    Deletes the PDF from disk and cleans up all vector chunks from the database.
    """
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": doc_id}

# ==============================================================
# RAG CHATBOT & EMBEDDINGS ENDPOINTS
# ==============================================================

@app.post("/api/chat")
def chat_with_tutor(req: ChatRequest):
    """
    Executes RAG Q&A grounded in document vector embeddings.
    """
    session_id = req.session_id or str(uuid.uuid4())
    result = rag_service.answer_query(
        query=req.query,
        session_id=session_id,
        doc_id=req.document_id,
        api_key=req.api_key
    )
    return result

@app.get("/api/chat/history")
def get_history(session_id: str = Query(...)):
    """
    Fetches conversational chat history for a session.
    """
    history = get_chat_history(session_id)
    return {"session_id": session_id, "messages": history}

@app.delete("/api/chat/history")
def clear_history(session_id: str = Query(...)):
    """
    Clears messages for the specified session.
    """
    clear_chat_history(session_id)
    return {"status": "cleared", "session_id": session_id}

# ==============================================================
# SETTINGS & API KEY CONFIGURATION
# ==============================================================

@app.get("/api/settings/status")
def get_settings_status():
    """
    Checks if Google Gemini API key is configured and valid.
    """
    is_active = rag_service.is_configured()
    active_key = rag_service.get_api_key()
    masked_key = f"{active_key[:6]}...{active_key[-4:]}" if active_key and len(active_key) > 10 else None
    return {
        "gemini_api_configured": is_active,
        "masked_key": masked_key,
        "embedding_model": rag_service.embedding_model,
        "chat_model": rag_service.chat_model
    }

@app.post("/api/settings/api-key")
def update_api_key(req: ApiKeyUpdate):
    """
    Saves user-provided Gemini API key in SQLite and updates the active runtime.
    """
    key = req.api_key.strip()
    if not key or len(key) < 15:
        raise HTTPException(status_code=400, detail="Invalid Gemini API Key format.")
    
    set_setting("gemini_api_key", key)
    # Also attempt writing to .env file if feasible
    env_file = os.path.join(BASE_DIR, '.env')
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"GEMINI_API_KEY={key}\n")
    except Exception:
        pass
        
    rag_service._cached_client = None # Reset cached client
    return {"status": "success", "message": "Gemini API key saved and activated successfully."}

# Serve static frontend files
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=True)
