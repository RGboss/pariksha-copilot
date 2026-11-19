import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting IT Officer Exam Prep Platform Server")
    print("  Serving at: http://127.0.0.1:8000")
    print("  Database: SQLite (E:/study material/prep_platform/data/study_portal.db)")
    print("=" * 60)
    
    # Launch default web browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, log_level="info")
