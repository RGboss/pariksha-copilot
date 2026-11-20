import os
import uvicorn
import webbrowser
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def open_browser():
    time.sleep(1.2)
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting Government Exam Prep Platform Server")
    print("  Serving at: http://127.0.0.1:8000")
    print("  Vector DB: ChromaDB (Persistent)")
    print("  Relational DB: SQLite + SQLAlchemy")
    print("=" * 60)
    
    # Launch default web browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, log_level="info", app_dir=BASE_DIR)
