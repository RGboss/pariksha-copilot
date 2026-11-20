"""
SQLAlchemy Database Models and SQLite Engine for Government Exam Preparation Platform
With Full User Authentication & Session Management
"""
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Text, DateTime, ForeignKey, desc, text, inspect
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "gov_exam_portal.db")

# PostgreSQL & SQLite Multi-Database Support
raw_db_url = os.environ.get("DATABASE_URL", "").strip()
if raw_db_url:
    # Standardize postgres:// or postgresql:// to postgresql+psycopg2://
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+"):
        raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    DATABASE_URL = raw_db_url
else:
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# Connection Engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=True)
    salt = Column(String(64), nullable=True)
    target_exam = Column(String(120), default="SEBI Grade A (IT Stream)")
    preferred_model = Column(String(50), default="gemini-2.5-flash")
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "target_exam": self.target_exam,
            "preferred_model": self.preferred_model or "gemini-2.5-flash",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    token = Column(String(128), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    category = Column(String(100), default="Study Material")
    summary = Column(Text, default="")
    vector_collection_id = Column(String(100), default="gov_exam_docs")
    page_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    file_hash = Column(String(64), nullable=True)
    toc_json = Column(Text, default="[]")
    chunk_count = Column(Integer, default=0)
    extracted_chars = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")

    def to_dict(self):
        import json
        toc = []
        try:
            toc = json.loads(self.toc_json or "[]")
        except Exception:
            toc = []
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "category": self.category,
            "summary": self.summary,
            "vector_collection_id": self.vector_collection_id,
            "page_count": self.page_count,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "toc": toc,
            "chunk_count": self.chunk_count or 0,
            "extracted_chars": self.extracted_chars or 0,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class StudyPlan(Base):
    __tablename__ = "study_plans"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    exam_name = Column(String(150), nullable=False)
    daily_hours = Column(Float, default=4.0)
    prep_level = Column(String(50), default="Intermediate")
    strategy_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="study_plans")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "exam_name": self.exam_name,
            "daily_hours": self.daily_hours,
            "prep_level": self.prep_level,
            "strategy_markdown": self.strategy_markdown,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    document_id = Column(String(64), nullable=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources_json = Column(Text, default="[]")
    model = Column(String(50), default="gemini-2.5-flash")
    token_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")

    def to_dict(self):
        import json
        sources = []
        try:
            sources = json.loads(self.sources_json or "[]")
        except Exception:
            pass
        return {
            "id": self.id,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "role": self.role,
            "content": self.content,
            "sources": sources,
            "model": self.model or "gemini-2.5-flash",
            "token_count": self.token_count or 0,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

# Automatic Migration & Table Initialization
def _run_migrations():
    try:
        with engine.connect() as conn:
            inspector = inspect(conn)

            # Check users columns
            if inspector.has_table("users"):
                user_cols = [c["name"] for c in inspector.get_columns("users")]
                if "password_hash" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(256)"))
                if "salt" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN salt VARCHAR(64)"))
                if "preferred_model" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN preferred_model VARCHAR(50) DEFAULT 'gemini-2.5-flash'"))

            # Check documents columns
            if inspector.has_table("documents"):
                doc_cols = [c["name"] for c in inspector.get_columns("documents")]
                if "file_hash" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN file_hash VARCHAR(64)"))
                if "toc_json" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN toc_json TEXT DEFAULT '[]'"))
                if "chunk_count" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN chunk_count INTEGER DEFAULT 0"))
                if "extracted_chars" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN extracted_chars INTEGER DEFAULT 0"))

            # Check chat_history columns
            if inspector.has_table("chat_history"):
                chat_cols = [c["name"] for c in inspector.get_columns("chat_history")]
                if "model" not in chat_cols:
                    conn.execute(text("ALTER TABLE chat_history ADD COLUMN model VARCHAR(50) DEFAULT 'gemini-2.5-flash'"))
                if "token_count" not in chat_cols:
                    conn.execute(text("ALTER TABLE chat_history ADD COLUMN token_count INTEGER DEFAULT 0"))

            conn.commit()
    except Exception as e:
        print(f"[DB] Database migration notice: {e}")

def init_db():
    """Initializes tables, executes schema migrations, and seeds demo account."""
    try:
        Base.metadata.create_all(bind=engine)
        _run_migrations()
        seed_demo_user()
    except Exception as e:
        print(f"[DB] Database initialization notice: {e}")

# ==============================================================
# CRYPTOGRAPHIC AUTHENTICATION UTILITIES
# ==============================================================

def hash_password(password: str) -> Tuple[str, str]:
    """Generates a secure PBKDF2-HMAC-SHA256 password hash and salt."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        100000
    ).hex()
    return pw_hash, salt

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """Verifies a plain password against stored salt and hash."""
    if not salt or not password_hash:
        return False
    computed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        100000
    ).hex()
    return secrets.compare_digest(computed, password_hash)

def create_user_session(user_id: str, days: int = 30) -> str:
    """Generates an authenticated session token for the user."""
    session = SessionLocal()
    try:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=days)
        user_sess = UserSession(token=token, user_id=user_id, expires_at=expires_at)
        session.add(user_sess)
        session.commit()
        return token
    finally:
        session.close()

def get_user_from_token(token: str) -> Optional[User]:
    """Retrieves the active user matching the bearer session token."""
    if not token:
        return None
    session = SessionLocal()
    try:
        user_sess = session.query(UserSession).filter(
            UserSession.token == token,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        if not user_sess:
            return None
        return session.query(User).filter(User.id == user_sess.user_id).first()
    finally:
        session.close()

def delete_user_session(token: str):
    """Logs out user by invalidating the session token."""
    session = SessionLocal()
    try:
        session.query(UserSession).filter(UserSession.token == token).delete()
        session.commit()
    finally:
        session.close()

def seed_demo_user():
    """Seeds an initial demo account and ensures its password is set."""
    session = SessionLocal()
    try:
        demo_user = session.query(User).filter(User.email == "rahul.aspirant@examportal.in").first()
        pw_hash, salt = hash_password("DemoPassword123")
        if not demo_user:
            demo_user = User(
                id="default_aspirant_user",
                name="Aspirant Rahul",
                email="rahul.aspirant@examportal.in",
                password_hash=pw_hash,
                salt=salt,
                target_exam="SEBI Grade A (IT Stream)"
            )
            session.add(demo_user)
        elif not demo_user.password_hash or not demo_user.salt:
            demo_user.password_hash = pw_hash
            demo_user.salt = salt
        session.commit()
    finally:
        session.close()

init_db()
