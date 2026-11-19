"""
SQLAlchemy Database Models and SQLite Engine for Government Exam Preparation Platform
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Text, DateTime, ForeignKey, desc
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "gov_exam_portal.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    target_exam = Column(String(120), default="SEBI Grade A (IT Stream)")
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "target_exam": self.target_exam,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

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
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")

    def to_dict(self):
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
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

# Initialize tables
Base.metadata.create_all(bind=engine)

def get_or_create_default_user() -> User:
    """Ensures at least one active user profile exists for seamless isolated sessions."""
    session = SessionLocal()
    try:
        user = session.query(User).first()
        if not user:
            user = User(
                id="default_aspirant_user",
                name="Aspirant Rahul",
                email="rahul.aspirant@examportal.in",
                target_exam="SEBI Grade A (IT Stream)"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()
