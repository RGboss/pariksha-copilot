import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:8000"

def api_call(path, method="GET", data=None, token=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = None
    if data is not None:
        if isinstance(data, dict):
            body = json.dumps(data).encode("utf-8")
        elif isinstance(data, bytes):
            body = data
        elif isinstance(data, str):
            body = data.encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}

print("==================================================")
print("USER AUTHENTICATION & DATA ISOLATION TEST SUITE")
print("==================================================")

import time
rand_id = int(time.time())

# 1. Sign up User A
print("1. Testing Account Creation for User A (Alice)...")
status, user_a_res = api_call("/api/auth/signup", method="POST", data={
    "name": "Alice Sharma",
    "email": f"alice_{rand_id}@examportal.in",
    "password": "AliceSecretPassword123",
    "target_exam": "UPSC CSE 2027"
})
assert status == 200, f"Signup failed: {user_a_res}"
token_a = user_a_res["token"]
user_a = user_a_res["user"]
print(f"   Alice created: ID={user_a['id'][:8]}..., Exam={user_a['target_exam']}, Token={token_a[:10]}...")

# 2. Sign up User B
print("2. Testing Account Creation for User B (Bob)...")
status, user_b_res = api_call("/api/auth/signup", method="POST", data={
    "name": "Bob Verma",
    "email": f"bob_{rand_id}@examportal.in",
    "password": "BobSecretPassword123",
    "target_exam": "SEBI Grade A (IT Stream)"
})
assert status == 200, f"Signup failed: {user_b_res}"
token_b = user_b_res["token"]
user_b = user_b_res["user"]
print(f"   Bob created: ID={user_b['id'][:8]}..., Exam={user_b['target_exam']}, Token={token_b[:10]}...")

# 3. Test duplicate email registration error
print("3. Testing duplicate email prevention...")
status, dup_res = api_call("/api/auth/signup", method="POST", data={
    "name": "Alice Duplicate",
    "email": f"alice_{rand_id}@examportal.in",
    "password": "AnotherPassword123",
    "target_exam": "UPSC CSE 2027"
})
assert status == 400, f"Expected 400 for duplicate email, got {status}: {dup_res}"
print(f"   Correctly rejected duplicate email with 400: '{dup_res.get('detail')}'")

# 4. User A generates a study plan
print("4. User A generates an AI Study Plan...")
status, plan_a = api_call("/api/strategy/generate", method="POST", data={
    "exam_name": "UPSC CSE 2027",
    "daily_hours": 6.0,
    "prep_level": "Beginner"
}, token=token_a)
assert status == 200, f"Plan generation failed: {plan_a}"
print(f"   User A plan saved: Plan ID={plan_a['id'][:8]}..., Length={len(plan_a['strategy_markdown'])} chars.")

# 5. User B checks strategy history (Isolation Check)
print("5. User B requests their strategy history (Data Isolation Check)...")
status, hist_b = api_call("/api/strategy/history", method="GET", token=token_b)
assert status == 200
assert len(hist_b) == 0, f"Expected 0 plans for Bob, but got {len(hist_b)}!"
print("   Verified: Bob sees 0 plans. Alice's plan is completely invisible to Bob!")

# 6. User A imports a workspace PDF
print("6. User A imports a study document into their personal library...")
ws_status, ws_pdfs = api_call("/api/documents/workspace-available", method="GET", token=token_a)
assert ws_status == 200 and ws_pdfs["total"] > 0
sample_pdf = ws_pdfs["available"][0]

import_payload = urllib.parse.urlencode({
    "full_path": sample_pdf["full_path"],
    "category": sample_pdf["suggested_category"]
}).encode()
req = urllib.request.Request(f"{BASE}/api/documents/import-workspace", data=import_payload, headers={
    "Authorization": f"Bearer {token_a}",
    "Content-Type": "application/x-www-form-urlencoded"
}, method="POST")
with urllib.request.urlopen(req) as r:
    doc_a = json.loads(r.read().decode("utf-8"))
print(f"   Alice imported '{doc_a['original_filename']}' (Doc ID: {doc_a['id'][:8]}...).")

# 7. Check Document Isolation: Bob's Library
print("7. Verifying Document Library Isolation for Bob...")
status, docs_b = api_call("/api/documents", method="GET", token=token_b)
assert status == 200
assert docs_b["total"] == 0, f"Expected 0 documents for Bob, but got {docs_b['total']}!"
print(f"   Verified: Bob's document library is 0 files. Alice's PDF is isolated!")

# 8. Check Document Isolation: Bob attempts to fetch Alice's raw PDF
print("8. Verifying Access Control: Bob attempts to stream Alice's PDF...")
raw_status, _ = api_call(f"/api/documents/{doc_a['id']}/raw?token={token_b}", method="GET")
assert raw_status == 404 or raw_status == 401, f"Expected 404 or 401 for unauthorized document access, got {raw_status}!"
print(f"   Verified: Bob receives HTTP {raw_status} when attempting to access Alice's PDF!")

# 9. Test User A RAG Chat & verify message isolation
print("9. Alice sends a chat query...")
status, chat_a = api_call("/api/chat", method="POST", data={
    "mode": "document",
    "document_id": doc_a["id"],
    "query": "What topics does this cover?"
}, token=token_a)
assert status == 200
status, hist_b_chat = api_call("/api/chat/history", method="GET", token=token_b)
assert len(hist_b_chat["messages"]) == 0
print("   Verified: Alice's chat messages are completely isolated from Bob!")

# 10. Test Logout & Token Invalidation
print("10. Testing Logout & Token Invalidation...")
status, _ = api_call("/api/auth/logout", method="POST", token=token_a)
assert status == 200
status, me_after = api_call("/api/auth/me", method="GET", token=token_a)
assert status == 401, f"Expected 401 after logout, got {status}!"
print("   Verified: Alice's token was invalidated upon logout!")

# 11. Test Incorrect Password
print("11. Testing Login with Incorrect Password...")
status, bad_login = api_call("/api/auth/login", method="POST", data={
    "email": f"bob_{rand_id}@examportal.in",
    "password": "WrongPassword999"
})
assert status == 401
print("   Verified: Incorrect password rejected with HTTP 401!")

print("==================================================")
print("ALL 11 AUTHENTICATION & ISOLATION TESTS PASSED 100%!")
print("==================================================")
