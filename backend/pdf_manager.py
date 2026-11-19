# -*- coding: utf-8 -*-
"""
PDF Document Ingestion, Chunking & Library Manager
Extracts text using pypdf, splits into semantic chunks with page citations,
generates embeddings, and interfaces with the SQLite database.
"""

import os
import re
import uuid
import shutil
from typing import List, Dict, Optional, Any
from pypdf import PdfReader

from backend.db import (
    add_document,
    add_chunks_batch,
    get_document,
    list_documents,
    delete_document,
    update_document_summary
)
from backend.rag_engine import rag_service

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'data', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

WORKSPACE_ROOT = os.path.dirname(BASE_DIR)

def chunk_text_by_pages(pages_data: List[Dict[str, Any]], chunk_size: int = 1800, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Chunks document page-by-page while tracking exact page numbers and maintaining overlap.
    """
    chunks = []
    chunk_index = 0

    for item in pages_data:
        page_num = item["page"]
        text = item["text"].strip()
        if not text:
            continue

        # Clean excess whitespaces while keeping paragraph structure
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # If page text is within chunk_size, keep as a single chunk
        if len(text) <= chunk_size:
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page_num,
                "content": text,
                "token_count": len(text.split())
            })
            chunk_index += 1
        else:
            # Split with sliding window
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Attempt to break on paragraph or sentence boundary
                if end < len(text):
                    last_period = text.rfind('. ', start, end)
                    last_newline = text.rfind('\n', start, end)
                    split_pt = max(last_period, last_newline)
                    if split_pt > start + (chunk_size // 2):
                        end = split_pt + 1

                sub_content = text[start:end].strip()
                if sub_content:
                    chunks.append({
                        "chunk_index": chunk_index,
                        "page_number": page_num,
                        "content": sub_content,
                        "token_count": len(sub_content.split())
                    })
                    chunk_index += 1

                start += (chunk_size - overlap)

    return chunks

def process_and_index_pdf(file_path: str, original_filename: str, category: str = "Study Material",
                          doc_id: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Full pipeline: Reads PDF -> Chunks -> Generates Embeddings -> Saves to SQLite.
    """
    if not doc_id:
        doc_id = str(uuid.uuid4())

    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

    reader = PdfReader(file_path)
    page_count = len(reader.pages)

    pages_data = []
    text_sample_accum = []
    
    for i, page in enumerate(reader.pages):
        page_num = i + 1
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        pages_data.append({"page": page_num, "text": txt})
        if len("".join(text_sample_accum)) < 12000 and txt:
            text_sample_accum.append(f"--- Page {page_num} ---\n{txt}")

    # Chunk text
    raw_chunks = chunk_text_by_pages(pages_data)
    chunk_texts = [c["content"] for c in raw_chunks]

    # Generate Embeddings (batch via Google GenAI)
    embeddings = rag_service.generate_embeddings(chunk_texts, api_key=api_key)

    # Format chunks for database insertion
    formatted_chunks = []
    for c, emb in zip(raw_chunks, embeddings):
        blob = emb.tobytes() if emb is not None else None
        formatted_chunks.append({
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "chunk_index": c["chunk_index"],
            "page_number": c["page_number"],
            "content": c["content"],
            "embedding_blob": blob,
            "token_count": c["token_count"]
        })

    # Generate quick summary
    sample_text = "\n".join(text_sample_accum)
    summary = rag_service.summarize_document(
        text_sample=sample_text,
        title=original_filename,
        category=category,
        api_key=api_key
    )

    # Save document record
    doc_record = add_document(
        doc_id=doc_id,
        filename=os.path.basename(file_path),
        original_filename=original_filename,
        category=category,
        file_path=file_path,
        file_size=file_size,
        page_count=page_count,
        summary=summary,
        status="ready"
    )

    # Save chunks into SQLite vector store
    add_chunks_batch(formatted_chunks)

    doc_record["chunks_count"] = len(formatted_chunks)
    return doc_record

def scan_workspace_study_pdfs() -> List[Dict[str, Any]]:
    """
    Finds existing high-yield IT Officer PDFs in the workspace study material folders.
    """
    target_dirs = [
        os.path.join(WORKSPACE_ROOT, 'IBPS SO IT Officer'),
        os.path.join(WORKSPACE_ROOT, 'SBI Specialist Cadre Officer (IT)'),
        os.path.join(WORKSPACE_ROOT, 'SEBI Grade A (IT Stream)')
    ]

    discovered = []
    for base in target_dirs:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.lower().endswith('.pdf'):
                    full_p = os.path.join(root, f)
                    rel_dir = os.path.basename(root)
                    
                    # Deduce default category
                    cat = "Study Material"
                    if "question" in f.lower() or "qna" in f.lower() or "mcq" in f.lower():
                        cat = "Question Bank"
                    elif "exam" in f.lower() or "mock" in f.lower():
                        cat = "Previous Year Papers"
                    elif "cheat" in f.lower() or "notes" in f.lower():
                        cat = "Formula Cheatsheets"

                    discovered.append({
                        "path": full_p,
                        "filename": f,
                        "category": cat,
                        "folder": rel_dir,
                        "size_bytes": os.path.getsize(full_p)
                    })

    return discovered

def import_workspace_pdf(file_path: str, category: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Copies a workspace PDF into the uploads repository and runs the indexing pipeline.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source PDF not found: {file_path}")

    filename = os.path.basename(file_path)
    doc_id = str(uuid.uuid4())
    dest_path = os.path.join(UPLOADS_DIR, f"{doc_id}_{filename}")

    shutil.copy2(file_path, dest_path)

    if not category:
        category = "Question Bank" if ("question" in filename.lower() or "qna" in filename.lower()) else "Study Material"

    return process_and_index_pdf(
        file_path=dest_path,
        original_filename=filename,
        category=category,
        doc_id=doc_id,
        api_key=api_key
    )
