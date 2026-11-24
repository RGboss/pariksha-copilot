"""
Government Exam Preparation Platform - Unified FastAPI Application Server
With Full User Authentication, Account Creation & Isolated User Data
"""
import os
import shutil
import uuid
import json
import urllib.parse
from typing import Optional, List, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

from backend.db_models import (
    SessionLocal, User, Document as DocModel, StudyPlan as PlanModel,
    ChatHistory as ChatModel, UserSession,
    Flashcard, Quiz, QuizAttempt, StudyTask,
    hash_password, verify_password, create_user_session,
    get_user_from_token, delete_user_session, seed_demo_user, init_db
)
from backend.chroma_rag import rag_service, compute_file_hash
from backend.flashcards_service import (
    generate_flashcards_from_doc, review_flashcard, get_user_flashcards
)
from backend.quiz_service import (
    generate_quiz_from_doc, submit_quiz_attempt, get_user_quizzes
)
from backend.planner_service import (
    create_task, get_tasks, toggle_task, delete_task, get_planner_stats
)

app = FastAPI(
    title="Government Exam Preparation Platform & AI Tutor",
    version="2.3.0",
    description="Full-stack AI platform with PostgreSQL, Multi-Model Selection, PyMuPDF Analysis, and Token-Optimized ChromaDB RAG."
)

@app.on_event("startup")
def on_startup():
    """Ensure database schema is verified and seeded on application startup."""
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def root_health():
    """Root health check endpoint for Docker container healthchecks."""
    return {"status": "healthy"}

@app.get("/api/health")
def health_check():
    """Health check endpoint for platform monitoring."""
    return {"status": "ok", "app": "pariksha-copilot", "version": "2.3.0"}

UPLOADS_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount uploads directory for static file access
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Load curriculum and question banks for progressive learning
CURRICULUM_PATH = os.path.join(BASE_DIR, "data", "curriculum.json")
CURRICULUM = {"stages": []}
if os.path.exists(CURRICULUM_PATH):
    try:
        with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
            CURRICULUM = json.load(f)
    except Exception as e:
        print(f"[Server] Warning reading curriculum.json: {e}")

QUESTION_BANK_PATH = os.path.join(BASE_DIR, "data", "extracted_qas.json")
QUESTION_BANK = []
if os.path.exists(QUESTION_BANK_PATH):
    try:
        with open(QUESTION_BANK_PATH, "r", encoding="utf-8") as f:
            QUESTION_BANK = json.load(f)
    except Exception as e:
        print(f"[Server] Warning reading extracted_qas.json: {e}")

# ==============================================================
# PYDANTIC SCHEMAS
# ==============================================================

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    target_exam: str = "SEBI Grade A (IT Stream)"

class LoginRequest(BaseModel):
    email: str
    password: str

class StrategyRequest(BaseModel):
    exam_name: str
    daily_hours: float = 4.0
    prep_level: str = "Intermediate"
    model: Optional[str] = None

class ChatRequest(BaseModel):
    mode: str = "document"  # "document" or "general"
    document_id: Optional[str] = None
    category: Optional[str] = None
    query: Optional[str] = None
    message: Optional[str] = None
    model: Optional[str] = None

    def get_query_text(self) -> str:
        return (self.query or self.message or "").strip()

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    target_exam: Optional[str] = None
    preferred_model: Optional[str] = None

class ApiKeyUpdate(BaseModel):
    api_key: str

class GenerateFlashcardsRequest(BaseModel):
    document_id: Optional[str] = None
    topic: Optional[str] = None
    count: Optional[int] = 5
    category: Optional[str] = "High-Yield Facts"

class ReviewFlashcardRequest(BaseModel):
    rating: str  # 'again', 'hard', 'good', 'easy'

class GenerateQuizRequest(BaseModel):
    document_id: Optional[str] = None
    topic: Optional[str] = None
    exam_name: Optional[str] = "Competitive Exam"
    question_count: Optional[int] = 5

class SubmitQuizRequest(BaseModel):
    answers: Dict[str, int]
    time_spent_seconds: Optional[int] = 0

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = "Revision"
    priority: Optional[str] = "High"
    due_date: Optional[str] = None

# ==============================================================
# AUTHENTICATION DEPENDENCY & HELPERS
# ==============================================================

def get_current_user(request: Request) -> User:
    """Extracts bearer session token and validates user session."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        token = request.query_params.get("token")

    if token:
        user = get_user_from_token(token)
        if user:
            return user

    raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")

def get_optional_user(request: Request) -> Optional[User]:
    """Tolerant user extractor for public endpoints."""
    try:
        return get_current_user(request)
    except Exception:
        return None

# ==============================================================
# AUTHENTICATION & ACCOUNT ENDPOINTS
# ==============================================================

@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    session = SessionLocal()
    try:
        email = req.email.strip().lower()
        if not email or "@" not in email or "." not in email:
            raise HTTPException(status_code=400, detail="Please enter a valid email address.")
        if len(req.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

        existing = session.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        pw_hash, salt = hash_password(req.password)
        new_user = User(
            id=str(uuid.uuid4()),
            name=req.name.strip() or "Aspirant",
            email=email,
            password_hash=pw_hash,
            salt=salt,
            target_exam=req.target_exam.strip() or "SEBI Grade A (IT Stream)"
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        user_dict = new_user.to_dict()

        token = create_user_session(new_user.id, session=session)
        return {
            "token": token,
            "user": user_dict
        }
    finally:
        session.close()

@app.post("/api/auth/login")
def login(req: LoginRequest):
    session = SessionLocal()
    try:
        email = req.email.strip().lower()
        user = session.query(User).filter(User.email == email).first()
        if not user or not user.password_hash or not user.salt:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if not verify_password(req.password, user.salt, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        user_dict = user.to_dict()
        token = create_user_session(user.id, session=session)
        return {
            "token": token,
            "user": user_dict
        }
    finally:
        session.close()

@app.post("/api/auth/logout")
def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        delete_user_session(token)
    return {"status": "logged_out"}

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"user": current_user.to_dict()}

@app.get("/api/user")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@app.put("/api/user")
def update_user_profile(req: UserUpdateRequest, current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        if req.name:
            user.name = req.name.strip()
        if req.target_exam:
            user.target_exam = req.target_exam.strip()
        if req.preferred_model:
            user.preferred_model = req.preferred_model.strip()
        session.commit()
        session.refresh(user)
        return user.to_dict()
    finally:
        session.close()

# ==============================================================
# EXAM STRATEGY AI AGENT (USER-ISOLATED)
# ==============================================================

@app.post("/api/strategy/generate")
def generate_strategy(req: StrategyRequest, current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    try:
        selected_model = req.model or getattr(current_user, "preferred_model", None) or "gemini-2.5-flash"
        strategy_md = rag_service.generate_exam_strategy(
            exam_name=req.exam_name,
            daily_hours=req.daily_hours,
            prep_level=req.prep_level,
            model=selected_model
        )

        plan = PlanModel(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            exam_name=req.exam_name,
            daily_hours=req.daily_hours,
            prep_level=req.prep_level,
            strategy_markdown=strategy_md
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return plan.to_dict()
    finally:
        session.close()

@app.get("/api/strategy/history")
def get_strategy_history(current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    try:
        plans = session.query(PlanModel).filter(
            PlanModel.user_id == current_user.id
        ).order_by(PlanModel.created_at.desc()).limit(10).all()
        return [p.to_dict() for p in plans]
    finally:
        session.close()

# ==============================================================
# PDF RESOURCE MANAGER & EMBEDDED VIEWER (USER-ISOLATED)
# ==============================================================

@app.get("/api/documents")
def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    session = SessionLocal()
    try:
        query = session.query(DocModel).filter(DocModel.user_id == current_user.id)
        if category and category != "all":
            query = query.filter(DocModel.category == category)
        if search:
            query = query.filter(DocModel.original_filename.ilike(f"%{search}%"))
        docs = query.order_by(DocModel.uploaded_at.desc()).all()
        return {"documents": [d.to_dict() for d in docs], "total": len(docs)}
    finally:
        session.close()

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Study Material"),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    session = SessionLocal()
    try:
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id[:8]}_{file.filename.replace(' ', '_')}"
        safe_category = category.replace(" ", "_").replace("/", "_")

        user_upload_dir = os.path.join(UPLOADS_DIR, current_user.id, safe_category)
        os.makedirs(user_upload_dir, exist_ok=True)
        file_dest = os.path.join(user_upload_dir, safe_filename)

        with open(file_dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_dest)
        file_hash = compute_file_hash(file_dest)

        # Index in ChromaDB with user isolation and deep PyMuPDF analysis
        index_res = rag_service.index_document(
            doc_id=doc_id,
            file_path=file_dest,
            category=category,
            original_filename=file.filename,
            user_id=current_user.id
        )

        page_count = index_res.get("page_count", 1) or 1
        chunk_count = index_res.get("chunk_count", 0)
        toc_json = json.dumps(index_res.get("toc", []))
        extracted_chars = index_res.get("total_chars", 0)

        # Auto-generate Quick Summary
        selected_model = getattr(current_user, "preferred_model", None) or "gemini-2.5-flash"
        summary = rag_service.generate_quick_summary(
            file_path=file_dest,
            filename=file.filename,
            category=category,
            model=selected_model
        )

        doc = DocModel(
            id=doc_id,
            user_id=current_user.id,
            filename=safe_filename,
            original_filename=file.filename,
            file_path=file_dest,
            category=category,
            summary=summary,
            vector_collection_id="gov_exam_rag_docs",
            page_count=page_count,
            file_size=file_size,
            file_hash=file_hash,
            toc_json=toc_json,
            chunk_count=chunk_count,
            extracted_chars=extracted_chars
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc.to_dict()
    finally:
        session.close()

@app.get("/api/documents/{doc_id}/raw")
def get_document_raw(doc_id: str, request: Request):
    # Allow token from query param or header for <iframe> embedded viewers
    token = request.query_params.get("token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    user = get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    session = SessionLocal()
    try:
        doc = session.query(DocModel).filter(
            DocModel.id == doc_id,
            DocModel.user_id == user.id
        ).first()
        if not doc or not os.path.exists(doc.file_path):
            raise HTTPException(status_code=404, detail="Document file not found.")
        
        encoded_filename = urllib.parse.quote(doc.original_filename)
        return FileResponse(
            path=doc.file_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"}
        )
    finally:
        session.close()

@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str, current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    try:
        doc = session.query(DocModel).filter(
            DocModel.id == doc_id,
            DocModel.user_id == current_user.id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        # 1. Delete physical file from disk
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception as e:
                print(f"[Server] Warning removing file {doc.file_path}: {e}")

        # 2. Purge vector chunks from ChromaDB
        rag_service.delete_document_vectors(doc_id)

        # 3. Delete database record
        session.delete(doc)
        session.commit()
        return {"status": "success", "deleted_id": doc_id}
    finally:
        session.close()

# ==============================================================
# WORKSPACE PDF SCANNER & 1-CLICK IMPORTER
# ==============================================================

@app.get("/api/documents/workspace-available")
def get_available_workspace_pdfs(current_user: User = Depends(get_current_user)):
    workspace_root = os.path.dirname(BASE_DIR)
    available = []
    
    for root, dirs, files in os.walk(workspace_root):
        if "prep_platform" in root or ".git" in root or "node_modules" in root:
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, workspace_root)
                size_kb = round(os.path.getsize(full_path) / 1024, 1)

                cat = "Study Material"
                lower = f.lower()
                if "question" in lower or "mcq" in lower or "mock" in lower or "qna" in lower:
                    cat = "Question Bank"
                elif "syllabus" in lower or "strategy" in lower or "pattern" in lower:
                    cat = "Syllabus & Pattern"
                elif "previous" in lower or "pyq" in lower or "solved" in lower:
                    cat = "Previous Year Paper"

                available.append({
                    "filename": f,
                    "rel_path": rel_path,
                    "full_path": full_path,
                    "size_kb": size_kb,
                    "suggested_category": cat
                })

    return {"available": available, "total": len(available)}

@app.post("/api/documents/import-workspace")
async def import_workspace_document(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    content_type = request.headers.get("content-type", "")
    full_path = None
    category = "Study Material"

    if "application/json" in content_type:
        try:
            body = await request.json()
            full_path = body.get("full_path") or body.get("rel_path") or body.get("relative_path")
            category = body.get("category", "Study Material")
        except Exception:
            pass

    if not full_path:
        try:
            form = await request.form()
            full_path = form.get("full_path") or form.get("rel_path") or form.get("relative_path")
            category = form.get("category", "Study Material")
        except Exception:
            pass

    if not full_path:
        raise HTTPException(status_code=400, detail="Missing full_path or rel_path parameter.")

    workspace_root = os.path.dirname(BASE_DIR)
    if not os.path.isabs(full_path):
        full_path = os.path.abspath(os.path.join(workspace_root, full_path))

    if not os.path.exists(full_path) or not full_path.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail=f"Specified workspace file does not exist or is not a PDF: {full_path}")

    session = SessionLocal()
    try:
        filename = os.path.basename(full_path)
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id[:8]}_{filename.replace(' ', '_')}"
        safe_category = category.replace(" ", "_").replace("/", "_")

        user_upload_dir = os.path.join(UPLOADS_DIR, current_user.id, safe_category)
        os.makedirs(user_upload_dir, exist_ok=True)
        dest_path = os.path.join(user_upload_dir, safe_filename)

        shutil.copy2(full_path, dest_path)
        file_size = os.path.getsize(dest_path)
        file_hash = compute_file_hash(dest_path)

        # Index in ChromaDB with user isolation and deep PyMuPDF analysis
        index_res = rag_service.index_document(
            doc_id=doc_id,
            file_path=dest_path,
            category=category,
            original_filename=filename,
            user_id=current_user.id
        )

        page_count = index_res.get("page_count", 1) or 1
        chunk_count = index_res.get("chunk_count", 0)
        toc_json = json.dumps(index_res.get("toc", []))
        extracted_chars = index_res.get("total_chars", 0)

        selected_model = getattr(current_user, "preferred_model", None) or "gemini-2.5-flash"
        summary = rag_service.generate_quick_summary(
            file_path=dest_path,
            filename=filename,
            category=category,
            model=selected_model
        )

        doc = DocModel(
            id=doc_id,
            user_id=current_user.id,
            filename=safe_filename,
            original_filename=filename,
            file_path=dest_path,
            category=category,
            summary=summary,
            vector_collection_id="gov_exam_rag_docs",
            page_count=page_count,
            file_size=file_size,
            file_hash=file_hash,
            toc_json=toc_json,
            chunk_count=chunk_count,
            extracted_chars=extracted_chars
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc.to_dict()
    finally:
        session.close()

# ==============================================================
# RAG-POWERED AI CHATBOT (USER-ISOLATED)
# ==============================================================

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest, current_user: User = Depends(get_current_user)):
    query_text = req.get_query_text()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query or message is required.")

    session = SessionLocal()
    try:
        # Save user message
        user_msg = ChatModel(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            document_id=req.document_id,
            role="user",
            content=query_text
        )
        session.add(user_msg)
        session.commit()

        # Determine Model Preference
        selected_model = req.model or getattr(current_user, "preferred_model", None) or "gemini-2.5-flash"

        # Execute Query with User Scoping & Model Selection
        if req.mode == "general":
            res = rag_service.answer_general_mentor_query(query_text, model=selected_model)
        else:
            res = rag_service.answer_rag_query(
                query=query_text,
                doc_id=req.document_id,
                category=req.category,
                user_id=current_user.id,
                model=selected_model
            )

        token_usage = res.get("token_usage", {})
        total_tokens = token_usage.get("total_tokens", 0)

        # Save assistant message with citation metadata & token metrics
        assistant_msg = ChatModel(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            document_id=req.document_id,
            role="assistant",
            content=res["answer"],
            sources_json=json.dumps(res.get("sources", [])),
            model=res.get("model", selected_model),
            token_count=total_tokens
        )
        session.add(assistant_msg)
        session.commit()

        return {
            "answer": res["answer"],
            "response": res["answer"],
            "sources": res.get("sources", []),
            "model": res.get("model", selected_model),
            "token_usage": token_usage,
            "mode": req.mode
        }
    finally:
        session.close()

@app.get("/api/chat/history")
def get_chat_history(
    document_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    session = SessionLocal()
    try:
        query = session.query(ChatModel).filter(ChatModel.user_id == current_user.id)
        if document_id:
            query = query.filter(ChatModel.document_id == document_id)
        else:
            query = query.filter(ChatModel.document_id.is_(None))
        messages = query.order_by(ChatModel.timestamp.asc()).all()
        return {"messages": [m.to_dict() for m in messages]}
    finally:
        session.close()

@app.delete("/api/chat/history")
def clear_chat_history(
    document_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    session = SessionLocal()
    try:
        query = session.query(ChatModel).filter(ChatModel.user_id == current_user.id)
        if document_id:
            query = query.filter(ChatModel.document_id == document_id)
        else:
            query = query.filter(ChatModel.document_id.is_(None))
        query.delete(synchronize_session=False)
        session.commit()
        return {"status": "cleared"}
    finally:
        session.close()

# ==============================================================
# SETTINGS, MODELS & API KEY
# ==============================================================

@app.get("/api/models")
def get_available_models():
    """Returns supported AI models and token efficiency catalog."""
    return {
        "models": rag_service.get_supported_models(),
        "default": "gemini-2.5-flash"
    }

@app.get("/api/settings/status")
def get_settings_status():
    active_key = os.environ.get("GEMINI_API_KEY", "").strip()
    is_active = len(active_key) > 15
    masked = f"{active_key[:6]}...{active_key[-4:]}" if is_active else None
    return {
        "gemini_api_configured": is_active,
        "masked_key": masked,
        "embedding_model": rag_service.embedding_model,
        "chat_model": rag_service.active_chat_model,
        "candidate_models": rag_service.candidate_models
    }

@app.post("/api/settings/api-key")
def update_api_key(req: ApiKeyUpdate, current_user: User = Depends(get_current_user)):
    key = req.api_key.strip()
    if len(key) < 15:
        raise HTTPException(status_code=400, detail="Invalid Gemini API key.")
    
    os.environ["GEMINI_API_KEY"] = key
    rag_service._load_client()
    return {"status": "updated", "gemini_configured": rag_service.is_configured()}

# ==============================================================
# FLASHCARDS & ACTIVE RECALL (SPACED REPETITION)
# ==============================================================

@app.post("/api/flashcards/generate")
def create_flashcards(req: GenerateFlashcardsRequest, current_user: User = Depends(get_current_user)):
    """Generates structured revision flashcards from a document or syllabus topic."""
    cards = generate_flashcards_from_doc(
        user_id=current_user.id,
        document_id=req.document_id,
        topic=req.topic,
        count=req.count or 5,
        category=req.category or "High-Yield Facts"
    )
    return {"status": "success", "flashcards": cards, "count": len(cards)}

@app.get("/api/flashcards")
def list_flashcards(
    document_id: Optional[str] = None,
    due_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Lists flashcards belonging to the current authenticated aspirant."""
    cards = get_user_flashcards(
        user_id=current_user.id,
        document_id=document_id,
        due_only=due_only
    )
    return {"flashcards": cards, "total": len(cards)}

@app.post("/api/flashcards/{card_id}/review")
def review_single_flashcard(
    card_id: str,
    req: ReviewFlashcardRequest,
    current_user: User = Depends(get_current_user)
):
    """Processes Leitner box progression for a flashcard based on recall rating."""
    updated = review_flashcard(
        user_id=current_user.id,
        card_id=card_id,
        rating=req.rating
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Flashcard not found.")
    return {"status": "success", "flashcard": updated}

@app.get("/api/flashcards/export")
def export_flashcards_markdown(
    document_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Exports flashcard decks in structured Markdown format for offline study."""
    cards = get_user_flashcards(user_id=current_user.id, document_id=document_id)
    lines = ["# 🗂️ High-Yield Study Flashcards Deck", f"**Aspirant:** {current_user.name}", f"**Exam:** {current_user.target_exam}", f"**Exported:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ""]
    for i, c in enumerate(cards, 1):
        lines.append(f"### Card {i}: {c['category']} ({c['difficulty']})")
        lines.append(f"**Q:** {c['front_prompt']}")
        lines.append(f"**A:** {c['back_answer']}")
        lines.append(f"*Mastery Box: {c['mastery_level']}/5 | Total Reviews: {c['review_count']}*\n---")
    return {"markdown": "\n".join(lines)}

# ==============================================================
# MOCK QUIZ & PYQ ASSESSMENT ENGINE (CBT SIMULATOR)
# ==============================================================

@app.post("/api/quiz/generate")
def create_quiz(req: GenerateQuizRequest, current_user: User = Depends(get_current_user)):
    """Generates a timed Computer-Based Test (CBT) mock exam from syllabus/docs."""
    quiz = generate_quiz_from_doc(
        user_id=current_user.id,
        document_id=req.document_id,
        topic=req.topic,
        exam_name=req.exam_name or current_user.target_exam,
        question_count=req.question_count or 5
    )
    if not quiz:
        raise HTTPException(status_code=500, detail="Failed to generate quiz.")
    return {"status": "success", "quiz": quiz}

@app.get("/api/quiz")
def list_quizzes(current_user: User = Depends(get_current_user)):
    """Lists all quizzes and user score reports."""
    quizzes = get_user_quizzes(user_id=current_user.id)
    return {"quizzes": quizzes, "total": len(quizzes)}

@app.post("/api/quiz/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str,
    req: SubmitQuizRequest,
    current_user: User = Depends(get_current_user)
):
    """Submits answer sheet, grades with explanations, and records attempt."""
    result = submit_quiz_attempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        answers=req.answers,
        time_spent_seconds=req.time_spent_seconds or 0
    )
    if not result:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return {"status": "success", "attempt": result, **result}

# ==============================================================
# STUDY PLANNER, REVISION CHECKLIST & STATS
# ==============================================================

@app.get("/api/planner/tasks")
def list_tasks(current_user: User = Depends(get_current_user)):
    """Retrieves all daily study tasks and revision items."""
    tasks = get_tasks(user_id=current_user.id)
    return {"tasks": tasks, "total": len(tasks)}

@app.post("/api/planner/tasks")
def add_task(req: CreateTaskRequest, current_user: User = Depends(get_current_user)):
    """Adds a new study or revision task."""
    due = None
    if req.due_date:
        try:
            due = datetime.fromisoformat(req.due_date.replace("Z", "+00:00"))
        except Exception:
            due = None
    task = create_task(
        user_id=current_user.id,
        title=req.title,
        description=req.description or "",
        category=req.category or "Revision",
        priority=req.priority or "High",
        due_date=due
    )
    return {"status": "success", "task": task}

@app.post("/api/planner/tasks/{task_id}/toggle")
def toggle_single_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Toggles completion state of a task."""
    task = toggle_task(user_id=current_user.id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "success", "task": task}

@app.delete("/api/planner/tasks/{task_id}")
def remove_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Deletes a study task."""
    ok = delete_task(user_id=current_user.id, task_id=task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "success", "deleted_id": task_id}

@app.get("/api/planner/stats")
def planner_statistics(current_user: User = Depends(get_current_user)):
    """Returns study metrics, completion rate, and current streak."""
    stats = get_planner_stats(user_id=current_user.id)
    return stats

# ==============================================================
# CURRICULUM & QUESTIONS PRESERVATION (PUBLIC)
# ==============================================================

@app.get("/api/curriculum")
def get_curriculum():
    return CURRICULUM

@app.get("/api/stages")
def get_stages():
    return {"stages": CURRICULUM.get("stages", [])}

@app.get("/api/chapters/{chapter_id}")
def get_chapter(chapter_id: str):
    for s in CURRICULUM.get("stages", []):
        for ch in s.get("chapters", []):
            if ch.get("id") == chapter_id:
                return ch
    raise HTTPException(status_code=404, detail="Chapter not found.")

@app.get("/api/questions")
def get_questions(category: Optional[str] = None, limit: int = 50, offset: int = 0):
    filtered = QUESTION_BANK
    if category and category != "all":
        filtered = [x for x in filtered if x.get("category", "").lower() == category.lower()]
    return {
        "total": len(filtered),
        "limit": limit,
        "offset": offset,
        "questions": filtered[offset: offset + limit]
    }

# ==============================================================
# STATIC MOUNT & ROOT ROUTE
# ==============================================================

FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
STATIC_LEGACY = os.path.join(BASE_DIR, "static")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Exclude /api, /health, /docs, /openapi.json which are matched by route precedence
        potential_file = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(potential_file):
            return FileResponse(potential_file)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
elif os.path.exists(STATIC_LEGACY):
    app.mount("/static", StaticFiles(directory=STATIC_LEGACY), name="static")

    @app.get("/{full_path:path}")
    def serve_legacy_spa(full_path: str):
        potential_file = os.path.join(STATIC_LEGACY, full_path)
        if full_path and os.path.isfile(potential_file):
            return FileResponse(potential_file)
        return FileResponse(os.path.join(STATIC_LEGACY, "index.html"))
