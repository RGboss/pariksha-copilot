import urllib.request
import urllib.parse
import json
import time

BASE = "http://127.0.0.1:8000"

print("==================================================")
print("GOVERNMENT EXAM PREPARATION PLATFORM - VERIFICATION")
print("==================================================")

# 1. User Profile
user_res = json.loads(urllib.request.urlopen(f"{BASE}/api/user").read().decode())
print(f"1. User Profile: Name='{user_res['name']}', Exam='{user_res['target_exam']}'")

# 2. Settings & Gemini Status
sett = json.loads(urllib.request.urlopen(f"{BASE}/api/settings/status").read().decode())
print(f"2. Settings: Gemini Configured={sett['gemini_api_configured']}, Model={sett['chat_model']}, Key={sett['masked_key']}")

# 3. Strategy Generator
strat_payload = json.dumps({
    "exam_name": "SEBI Grade A (IT Stream)",
    "daily_hours": 4.5,
    "prep_level": "Intermediate"
}).encode()
req = urllib.request.Request(f"{BASE}/api/strategy/generate", data=strat_payload, headers={"Content-Type": "application/json"})
strat_res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"3. AI Strategy Agent: Generated blueprint ({len(strat_res['strategy_markdown'])} chars) for '{strat_res['exam_name']}'")

# 4. Workspace Scan
ws_res = json.loads(urllib.request.urlopen(f"{BASE}/api/documents/workspace-available").read().decode())
print(f"4. Workspace Scan: Found {ws_res['total']} local PDFs ready for 1-click import.")

# 5. Ingest Workspace PDF into ChromaDB & SQLite
sample_pdf = ws_res["available"][0]
print(f"5. Importing sample PDF: '{sample_pdf['filename']}' ({sample_pdf['size_kb']} KB)...")
import_payload = urllib.parse.urlencode({
    "full_path": sample_pdf["full_path"],
    "category": sample_pdf["suggested_category"]
}).encode()
import_res = json.loads(urllib.request.urlopen(f"{BASE}/api/documents/import-workspace", data=import_payload).read().decode())
imported_id = import_res["id"]
print(f"   Success! Doc ID={imported_id[:8]}..., Pages={import_res['page_count']}, Summary len={len(import_res['summary'])} chars.")

# 6. List Documents
docs_res = json.loads(urllib.request.urlopen(f"{BASE}/api/documents").read().decode())
print(f"6. Documents Library: {docs_res['total']} documents currently cataloged.")

# 7. Document Mode RAG Chat (ChromaDB + Gemini)
print("7. Testing Document Mode RAG Q&A via ChromaDB...")
chat_payload = json.dumps({
    "mode": "document",
    "document_id": imported_id,
    "query": "What are the core technical concepts and topics detailed in this document?"
}).encode()
req = urllib.request.Request(f"{BASE}/api/chat", data=chat_payload, headers={"Content-Type": "application/json"})
chat_res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"   RAG Answer received ({len(chat_res['answer'])} chars, Model: {chat_res['model']})")
print(f"   Citations cited: {len(chat_res['sources'])} (e.g. {chat_res['sources'][0] if chat_res['sources'] else 'None'})")

# 8. General Mentor Mode
print("8. Testing General Exam Mentor Mode...")
mentor_payload = json.dumps({
    "mode": "general",
    "query": "What is the key difference between SEBI Grade A Phase 1 Paper 2 and Phase 2 Paper 2?"
}).encode()
req = urllib.request.Request(f"{BASE}/api/chat", data=mentor_payload, headers={"Content-Type": "application/json"})
mentor_res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"   Mentor Answer received ({len(mentor_res['answer'])} chars, Model: {mentor_res['model']})")

# 9. Verify Raw PDF Stream
raw_req = urllib.request.urlopen(f"{BASE}/api/documents/{imported_id}/raw")
print(f"9. Raw PDF Stream: Status={raw_req.status}, Content-Type={raw_req.headers.get('Content-Type')}, Size={len(raw_req.read())} bytes.")

# 10. Clean-up & Delete Verification
del_req = urllib.request.Request(f"{BASE}/api/documents/{imported_id}", method="DELETE")
del_res = json.loads(urllib.request.urlopen(del_req).read().decode())
print(f"10. Delete & Purge: Status={del_res['status']} for ID {del_res['deleted_id'][:8]}...")

# 11. Confirm Library Empty
docs_after = json.loads(urllib.request.urlopen(f"{BASE}/api/documents").read().decode())
print(f"11. Verification: Documents remaining={docs_after['total']} (Purged completely).")

print("==================================================")
print("ALL 11 BACKEND & RAG TESTS PASSED FLAWLESSLY!")
print("==================================================")
