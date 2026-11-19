"""
Government Exam Preparation Platform - Unified FastAPI Application Server
"""
import os
import shutil
import uuid
import json
import urllib.parse
from typing import Optional, List, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
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
    ChatHistory as ChatModel, get_or_create_default_user
)
from backend.chroma_rag import rag_service

app = FastAPI(
    title="Government Exam Preparation Platform & AI Tutor",
    version="2.0.0",
    description="Full-stack AI platform with Exam Strategy Agent, PDF Resource Manager, and ChromaDB Google RAG."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
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

class StrategyRequest(BaseModel):
    user_id: Optional[str] = None
    exam_name: str
    daily_hours: float = 4.0
    prep_level: str = "Intermediate"

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    mode: str = "document"  # "document" or "general"
    document_id: Optional[str] = None
    category: Optional[str] = None
    query: str

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    target_exam: Optional[str] = None

class ApiKeyUpdate(BaseModel):
    api_key: str

# ==============================================================
# USER / PROFILE ENDPOINTS
# ==============================================================

@app.get("/api/user")
def get_user_profile():
    user = get_or_create_default_user()
    return user.to_dict()

@app.put("/api/user")
def update_user_profile(req: UserUpdateRequest):
    session = SessionLocal()
    try:
        user = session.query(User).first()
        if not user:
            user = get_or_create_default_user()
        if req.name:
            user.name = req.name.strip()
        if req.email:
            user.email = req.email.strip()
        if req.target_exam:
            user.target_exam = req.target_exam.strip()
        session.commit()
        session.refresh(user)
        return user.to_dict()
    finally:
        session.close()

# ==============================================================
# EXAM STRATEGY AI AGENT
# ==============================================================

@app.post("/api/strategy/generate")
def generate_strategy(req: StrategyRequest):
    session = SessionLocal()
    try:
        user_id = req.user_id
        if not user_id:
            user = session.query(User).first()
            user_id = user.id if user else "default_aspirant_user"

        strategy_md = rag_service.generate_exam_strategy(
            exam_name=req.exam_name,
            daily_hours=req.daily_hours,
            prep_level=req.prep_level
        )

        plan = PlanModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
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
def get_strategy_history(user_id: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(PlanModel)
        if user_id:
            query = query.filter(PlanModel.user_id == user_id)
        plans = query.order_by(PlanModel.created_at.desc()).limit(10).all()
        return [p.to_dict() for p in plans]
    finally:
        session.close()

# ==============================================================
# PDF RESOURCE MANAGER & EMBEDDED VIEWER
# ==============================================================

@app.get("/api/documents")
def list_documents(category: Optional[str] = None, search: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(DocModel)
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
    user_id: Optional[str] = Form(None)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    session = SessionLocal()
    try:
        if not user_id:
            user = session.query(User).first()
            user_id = user.id if user else "default_aspirant_user"

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id[:8]}_{file.filename.replace(' ', '_')}"
        safe_category = category.replace(" ", "_").replace("/", "_")

        user_upload_dir = os.path.join(UPLOADS_DIR, user_id, safe_category)
        os.makedirs(user_upload_dir, exist_ok=True)
        file_dest = os.path.join(user_upload_dir, safe_filename)

        with open(file_dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_dest)

        # Count pages
        import pypdf
        reader = pypdf.PdfReader(file_dest)
        page_count = len(reader.pages)

        # Index in ChromaDB
        chunk_count = rag_service.index_document(
            doc_id=doc_id,
            file_path=file_dest,
            category=category,
            original_filename=file.filename
        )

        # Auto-generate Quick Summary
        summary = rag_service.generate_quick_summary(
            file_path=file_dest,
            filename=file.filename,
            category=category
        )

        doc = DocModel(
            id=doc_id,
            user_id=user_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_path=file_dest,
            category=category,
            summary=summary,
            vector_collection_id="gov_exam_rag_docs",
            page_count=page_count,
            file_size=file_size
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        res = doc.to_dict()
        res["chunk_count"] = chunk_count
        return res
    finally:
        session.close()

@app.get("/api/documents/{doc_id}/raw")
def get_document_raw(doc_id: str):
    session = SessionLocal()
    try:
        doc = session.query(DocModel).filter(DocModel.id == doc_id).first()
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
def delete_document(doc_id: str):
    session = SessionLocal()
    try:
        doc = session.query(DocModel).filter(DocModel.id == doc_id).first()
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
def get_available_workspace_pdfs():
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
def import_workspace_document(full_path: str = Form(...), category: str = Form("Study Material")):
    if not os.path.exists(full_path) or not full_path.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Specified workspace file does not exist or is not a PDF.")

    session = SessionLocal()
    try:
        user = session.query(User).first()
        user_id = user.id if user else "default_aspirant_user"

        filename = os.path.basename(full_path)
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id[:8]}_{filename.replace(' ', '_')}"
        safe_category = category.replace(" ", "_").replace("/", "_")

        user_upload_dir = os.path.join(UPLOADS_DIR, user_id, safe_category)
        os.makedirs(user_upload_dir, exist_ok=True)
        dest_path = os.path.join(user_upload_dir, safe_filename)

        shutil.copy2(full_path, dest_path)
        file_size = os.path.getsize(dest_path)

        import pypdf
        reader = pypdf.PdfReader(dest_path)
        page_count = len(reader.pages)

        # Index in ChromaDB
        rag_service.index_document(
            doc_id=doc_id,
            file_path=dest_path,
            category=category,
            original_filename=filename
        )

        summary = rag_service.generate_quick_summary(
            file_path=dest_path,
            filename=filename,
            category=category
        )

        doc = DocModel(
            id=doc_id,
            user_id=user_id,
            filename=safe_filename,
            original_filename=filename,
            file_path=dest_path,
            category=category,
            summary=summary,
            vector_collection_id="gov_exam_rag_docs",
            page_count=page_count,
            file_size=file_size
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc.to_dict()
    finally:
        session.close()

# ==============================================================
# RAG-POWERED AI CHATBOT
# ==============================================================

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest):
    session = SessionLocal()
    try:
        user_id = req.user_id
        if not user_id:
            user = session.query(User).first()
            user_id = user.id if user else "default_aspirant_user"

        # Save user message
        user_msg = ChatModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            document_id=req.document_id,
            role="user",
            content=req.query
        )
        session.add(user_msg)
        session.commit()

        # Execute Query
        if req.mode == "general":
            res = rag_service.answer_general_mentor_query(req.query)
        else:
            res = rag_service.answer_rag_query(
                query=req.query,
                doc_id=req.document_id,
                category=req.category
            )

        # Save assistant message with citation metadata
        assistant_msg = ChatModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            document_id=req.document_id,
            role="assistant",
            content=res["answer"],
            sources_json=json.dumps(res.get("sources", []))
        )
        session.add(assistant_msg)
        session.commit()

        return {
            "answer": res["answer"],
            "sources": res.get("sources", []),
            "model": res.get("model", "gemini-2.5-flash"),
            "mode": req.mode
        }
    finally:
        session.close()

@app.get("/api/chat/history")
def get_chat_history(document_id: Optional[str] = None, user_id: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(ChatModel)
        if user_id:
            query = query.filter(ChatModel.user_id == user_id)
        if document_id:
            query = query.filter(ChatModel.document_id == document_id)
        else:
            query = query.filter(ChatModel.document_id.is_(None))
        messages = query.order_by(ChatModel.timestamp.asc()).all()
        return {"messages": [m.to_dict() for m in messages]}
    finally:
        session.close()

@app.delete("/api/chat/history")
def clear_chat_history(document_id: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(ChatModel)
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
# SETTINGS & API KEY
# ==============================================================

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
def update_api_key(req: ApiKeyUpdate):
    key = req.api_key.strip()
    if len(key) < 15:
        raise HTTPException(status_code=400, detail="Invalid Gemini API key.")
    
    os.environ["GEMINI_API_KEY"] = key
    rag_service._load_client()
    return {"status": "updated", "gemini_configured": rag_service.is_configured()}

# ==============================================================
# CURRICULUM & QUESTIONS PRESERVATION
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

# Check if Vite frontend dist directory exists
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
STATIC_LEGACY = os.path.join(BASE_DIR, "static")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
elif os.path.exists(STATIC_LEGACY):
    app.mount("/static", StaticFiles(directory=STATIC_LEGACY), name="static")
    @app.get("/")
    def serve_legacy_frontend():
        return FileResponse(os.path.join(STATIC_LEGACY, "index.html"))
