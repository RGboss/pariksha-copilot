import os
import uvicorn
import webbrowser
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def open_browser(port: int = 8082):
    time.sleep(1.2)
    try:
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception:
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8082"))
    print("=" * 60)
    print("  Starting Government Exam Prep Platform Server")
    print(f"  Serving at: http://127.0.0.1:{port}")
    print("  Vector DB: ChromaDB (Persistent)")
    print("  Relational DB: SQLite + SQLAlchemy")
    print("=" * 60)
    
    # Launch default web browser in separate thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    uvicorn.run("backend.server:app", host="0.0.0.0", port=port, log_level="info", app_dir=BASE_DIR)
