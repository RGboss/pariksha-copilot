import sqlite3
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'study_portal.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Existing tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS chapter_progress (
            chapter_id TEXT PRIMARY KEY,
            completed INTEGER DEFAULT 0,
            bookmarked INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id TEXT,
            score INTEGER,
            total INTEGER,
            percentage REAL,
            answers_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id TEXT,
            action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NEW: Uploaded Documents Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            category TEXT DEFAULT 'Study Material',
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            page_count INTEGER DEFAULT 0,
            summary TEXT DEFAULT '',
            status TEXT DEFAULT 'ready',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NEW: Document Chunks for Vector & RAG Search
    c.execute('''
        CREATE TABLE IF NOT EXISTS document_chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding_blob BLOB,
            token_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES uploaded_documents(id) ON DELETE CASCADE
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks(document_id)')
    
    # NEW: Chat History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            document_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id)')

    # NEW: App Key/Value Settings Table (persists user configured API key etc.)
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Chapter Progress Functions
def get_all_progress():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM chapter_progress')
    rows = c.fetchall()
    progress_map = {}
    for r in rows:
        progress_map[r['chapter_id']] = {
            'completed': bool(r['completed']),
            'bookmarked': bool(r['bookmarked']),
            'notes': r['notes'],
            'updated_at': r['updated_at']
        }
    
    c.execute('''
        SELECT chapter_id, score, total, percentage, created_at 
        FROM quiz_attempts 
        WHERE id IN (SELECT MAX(id) FROM quiz_attempts GROUP BY chapter_id)
    ''')
    quiz_rows = c.fetchall()
    quiz_map = {}
    for q in quiz_rows:
        quiz_map[q['chapter_id']] = {
            'score': q['score'],
            'total': q['total'],
            'percentage': round(q['percentage'], 1),
            'taken_at': q['created_at']
        }
    conn.close()
    return progress_map, quiz_map

def update_chapter_progress(chapter_id: str, completed: bool = None, bookmarked: bool = None, notes: str = None):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM chapter_progress WHERE chapter_id = ?', (chapter_id,))
    existing = c.fetchone()
    
    if existing:
        new_completed = existing['completed'] if completed is None else (1 if completed else 0)
        new_bookmarked = existing['bookmarked'] if bookmarked is None else (1 if bookmarked else 0)
        new_notes = existing['notes'] if notes is None else notes
        c.execute('''
            UPDATE chapter_progress 
            SET completed = ?, bookmarked = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE chapter_id = ?
        ''', (new_completed, new_bookmarked, new_notes, chapter_id))
    else:
        new_completed = 1 if completed else 0
        new_bookmarked = 1 if bookmarked else 0
        new_notes = notes or ''
        c.execute('''
            INSERT INTO chapter_progress (chapter_id, completed, bookmarked, notes)
            VALUES (?, ?, ?, ?)
        ''', (chapter_id, new_completed, new_bookmarked, new_notes))
    
    conn.commit()
    conn.close()

def record_quiz_attempt(chapter_id: str, score: int, total: int, answers: dict):
    conn = get_connection()
    c = conn.cursor()
    pct = (score / total * 100.0) if total > 0 else 0.0
    c.execute('''
        INSERT INTO quiz_attempts (chapter_id, score, total, percentage, answers_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (chapter_id, score, total, pct, json.dumps(answers)))
    conn.commit()
    conn.close()
    return {'score': score, 'total': total, 'percentage': round(pct, 1)}

def get_stats(total_chapters: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as cnt FROM chapter_progress WHERE completed = 1')
    completed_count = c.fetchone()['cnt']
    
    c.execute('SELECT COUNT(*) as cnt FROM chapter_progress WHERE bookmarked = 1')
    bookmarked_count = c.fetchone()['cnt']
    
    c.execute('SELECT AVG(percentage) as avg_pct, COUNT(*) as attempts FROM quiz_attempts')
    row = c.fetchone()
    avg_score = round(row['avg_pct'] or 0.0, 1)
    quiz_attempts_count = row['attempts']
    
    # Document statistics
    c.execute('SELECT COUNT(*) as doc_count, COALESCE(SUM(page_count), 0) as total_pages FROM uploaded_documents')
    doc_row = c.fetchone()
    doc_count = doc_row['doc_count']
    total_pages = doc_row['total_pages']
    
    c.execute('SELECT COUNT(*) as chunk_count FROM document_chunks')
    chunk_count = c.fetchone()['chunk_count']
    
    conn.close()
    pct_progress = round((completed_count / total_chapters * 100.0), 1) if total_chapters > 0 else 0.0
    return {
        'total_chapters': total_chapters,
        'completed_chapters': completed_count,
        'progress_percentage': pct_progress,
        'bookmarked_chapters': bookmarked_count,
        'quiz_average_percentage': avg_score,
        'total_quizzes_taken': quiz_attempts_count,
        'total_documents': doc_count,
        'total_document_pages': total_pages,
        'total_chunks_indexed': chunk_count
    }

# ==============================================================
# DOCUMENT MANAGEMENT & VECTOR PERSISTENCE
# ==============================================================

def add_document(doc_id: str, filename: str, original_filename: str, category: str,
                 file_path: str, file_size: int, page_count: int, summary: str = "",
                 status: str = "ready") -> Dict[str, Any]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO uploaded_documents 
        (id, filename, original_filename, category, file_path, file_size, page_count, summary, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (doc_id, filename, original_filename, category, file_path, file_size, page_count, summary, status))
    conn.commit()
    conn.close()
    return get_document(doc_id)

def update_document_summary(doc_id: str, summary: str, status: str = "ready"):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE uploaded_documents SET summary = ?, status = ? WHERE id = ?', (summary, status, doc_id))
    conn.commit()
    conn.close()

def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM uploaded_documents WHERE id = ?', (doc_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def list_documents(category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    query = '''
        SELECT d.*, COUNT(c.id) AS chunk_count
        FROM uploaded_documents d
        LEFT JOIN document_chunks c ON d.id = c.document_id
        WHERE 1=1
    '''
    params = []
    if category and category != 'all':
        query += ' AND d.category = ?'
        params.append(category)
    if search:
        query += ' AND (d.original_filename LIKE ? OR d.summary LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    query += ' GROUP BY d.id ORDER BY d.created_at DESC'
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_document(doc_id: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT file_path FROM uploaded_documents WHERE id = ?', (doc_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    file_path = row['file_path']
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
    c.execute('DELETE FROM document_chunks WHERE document_id = ?', (doc_id,))
    c.execute('DELETE FROM uploaded_documents WHERE id = ?', (doc_id,))
    conn.commit()
    conn.close()
    return True

# Document Chunks and Vector Embeddings
def add_chunks_batch(chunks: List[Dict[str, Any]]):
    """
    Inserts a batch of text chunks with their binary embedding blobs.
    """
    conn = get_connection()
    c = conn.cursor()
    data = [
        (
            ch.get('id', str(uuid.uuid4())),
            ch['document_id'],
            ch['chunk_index'],
            ch['page_number'],
            ch['content'],
            ch.get('embedding_blob', None),
            ch.get('token_count', 0)
        )
        for ch in chunks
    ]
    c.executemany('''
        INSERT OR REPLACE INTO document_chunks 
        (id, document_id, chunk_index, page_number, content, embedding_blob, token_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def get_chunks_for_document(doc_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, document_id, chunk_index, page_number, content, embedding_blob, token_count
        FROM document_chunks 
        WHERE document_id = ?
        ORDER BY chunk_index ASC
    ''', (doc_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_chunks_for_vector_search(doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    if doc_id and doc_id != 'all':
        c.execute('''
            SELECT c.id, c.document_id, c.chunk_index, c.page_number, c.content, c.embedding_blob,
                   d.original_filename, d.category
            FROM document_chunks c
            JOIN uploaded_documents d ON c.document_id = d.id
            WHERE c.document_id = ?
        ''', (doc_id,))
    else:
        c.execute('''
            SELECT c.id, c.document_id, c.chunk_index, c.page_number, c.content, c.embedding_blob,
                   d.original_filename, d.category
            FROM document_chunks c
            JOIN uploaded_documents d ON c.document_id = d.id
        ''')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Chat History
def save_chat_message(session_id: str, role: str, content: str,
                      document_id: Optional[str] = None, sources: Optional[List[Dict[str, Any]]] = None):
    conn = get_connection()
    c = conn.cursor()
    sources_str = json.dumps(sources or [])
    c.execute('''
        INSERT INTO chat_messages (session_id, document_id, role, content, sources_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, document_id, role, content, sources_str))
    conn.commit()
    conn.close()

def get_chat_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, session_id, document_id, role, content, sources_json, created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
    ''', (session_id, limit))
    rows = c.fetchall()
    conn.close()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item['sources'] = json.loads(item['sources_json'])
        except Exception:
            item['sources'] = []
        results.append(item)
    return results

def clear_chat_history(session_id: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

# App Settings (for API Key etc.)
def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return row['value']
    return default

def set_setting(key: str, value: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO app_settings (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (key, value))
    conn.commit()
    conn.close()
