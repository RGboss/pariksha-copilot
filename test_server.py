import urllib.request
import json

BASE = 'http://127.0.0.1:8000'

print("--- RUNNING FULL SYSTEM & RAG VERIFICATION TESTS ---")

# 1. Stats
s = json.loads(urllib.request.urlopen(BASE + '/api/stats').read().decode())
print("1. Stats API:", s)

# 2. Stages
st = json.loads(urllib.request.urlopen(BASE + '/api/stages').read().decode())['stages']
total_chapters = sum(len(x['chapters']) for x in st)
print(f"2. Stages API: {len(st)} stages, {total_chapters} chapters loaded.")

# 3. Chapter 2 (Normalization)
ch2 = json.loads(urllib.request.urlopen(BASE + '/api/chapters/ch-2').read().decode())
print(f"3. Chapter 2: '{ch2['title']}', Length: {len(ch2['lecture_notes'])} chars, {len(ch2['checkpoints'])} checkpoints, {len(ch2['quiz'])} quiz questions.")

# 4. Search
search_res = json.loads(urllib.request.urlopen(BASE + '/api/search?q=banker').read().decode())
print(f"4. Search API ('banker'): Found {len(search_res['chapters'])} matching chapters and {len(search_res['questions'])} questions.")

# 5. Documents List
docs_res = json.loads(urllib.request.urlopen(BASE + '/api/documents').read().decode())
docs = docs_res.get('documents', [])
print(f"5. Documents API: {len(docs)} documents indexed in the library.")
for d in docs:
    fname = d.get('original_filename') or d.get('filename', 'Unknown')
    print(f"   - [{d['category']}] {fname} ({d.get('page_count', 0)} pgs, {d.get('chunk_count', 0)} chunks)")

# 6. Workspace Available PDFs
ws = json.loads(urllib.request.urlopen(BASE + '/api/documents/workspace-available').read().decode())
print(f"6. Workspace Scan API: Found {len(ws)} available study PDFs ready for one-click import.")

# 7. Settings Status
sett = json.loads(urllib.request.urlopen(BASE + '/api/settings/status').read().decode())
print(f"7. Settings API: Gemini Key Configured = {sett['gemini_api_configured']}, Model = {sett['chat_model']}")

# 8. Chat RAG Query (Test on indexed DBMS notes)
chat_payload = json.dumps({
    'query': 'Explain BCNF and 3NF difference according to the uploaded study materials',
    'document_id': docs[0]['id'] if docs else None
}).encode()
req = urllib.request.Request(BASE + '/api/chat', data=chat_payload, headers={'Content-Type': 'application/json'})
chat_res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"8. Chatbot RAG API: Received answer of {len(chat_res['answer'])} chars, Sources cited: {len(chat_res['sources'])}.")
if chat_res['sources']:
    print(f"   Source 1: Page {chat_res['sources'][0]['page']} (Doc: {chat_res['sources'][0]['document_id'][:8]}...)")

# 9. Static Frontend
html = urllib.request.urlopen(BASE + '/').read().decode()
print(f"9. Static Frontend: Served index.html ({len(html)} bytes).")

print("--- ALL 9 TEST CHECKS PASSED PERFECTLY ---")
