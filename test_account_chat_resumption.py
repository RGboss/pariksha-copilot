import os
import sys
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=== STARTING ACCOUNT CREATION, FILE UPLOAD & CHAT RESUMPTION TESTS ===")
    
    # 1. Create a brand new user account
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"ananya.ias.{unique_suffix}@portal.in"
    test_password = "Password@2026"
    test_name = "Ananya Sharma"
    test_exam = "UPSC Civil Services 2027"

    print(f"\n[1] Registering new aspirant account: {test_email}")
    reg_res = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={
            "name": test_name,
            "email": test_email,
            "password": test_password,
            "target_exam": test_exam
        }
    )
    assert reg_res.status_code == 200, f"Signup failed: {reg_res.text}"
    reg_data = reg_res.json()
    token = reg_data["token"]
    user_id = reg_data["user"]["id"]
    print(f"-> Registered successfully! User ID: {user_id}, Name: {reg_data['user']['name']}")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify Session Auth (/api/auth/me)
    print("\n[2] Verifying session profile (/api/auth/me)")
    me_res = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert me_res.status_code == 200, f"Profile fetch failed: {me_res.text}"
    me_data = me_res.json()
    assert me_data["user"]["email"] == test_email
    assert me_data["user"]["target_exam"] == test_exam
    print("-> Session profile validated.")

    # 3. Create and upload a study material PDF
    print("\n[3] Creating and uploading sample study PDF to vault")
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    sample_pdf_path = f"E:\\study material\\prep_platform\\temp_test_{unique_suffix}.pdf"
    
    # Let's generate a real small PDF with text using reportlab or PyPDF
    # Or import an existing study PDF from E:\study material
    source_pdf = r"E:\study material\banking\GK\100 history questions.pdf"
    assert os.path.exists(source_pdf), f"Source study PDF missing: {source_pdf}"

    with open(source_pdf, "rb") as f:
        files = {"file": ("DBMS_Foundations_Test.pdf", f, "application/pdf")}
        data = {
            "category": "Study Material",
            "custom_category": ""
        }
        up_res = requests.post(f"{BASE_URL}/api/documents/upload", headers=headers, files=files, data=data)
    
    assert up_res.status_code == 200, f"Upload failed: {up_res.text}"
    doc_data = up_res.json()
    doc_id = doc_data["id"]
    print(f"-> Upload successful! Document ID: {doc_id}")
    print(f"-> Document Title: {doc_data['filename']}")
    print(f"-> Category: {doc_data['category']}")
    print(f"-> Auto-Summary snippet: {doc_data['summary'][:120]}...")

    # 4. Verify Document is listed in user vault
    print("\n[4] Querying user document library")
    docs_res = requests.get(f"{BASE_URL}/api/documents", headers=headers)
    assert docs_res.status_code == 200
    docs_list = docs_res.json().get("documents", [])
    found_doc = next((d for d in docs_list if d["id"] == doc_id), None)
    assert found_doc is not None, "Uploaded document not found in user library"
    print(f"-> Verified: Document present in library with {len(docs_list)} total user files.")

    # 5. Send Question 1 to RAG Document Chat
    print("\n[5] Sending first doubt to document chat: 'What are the main ACID properties in DBMS?'")
    chat_res1 = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "mode": "document",
            "document_id": doc_id,
            "category": "Study Material",
            "query": "What are the main ACID properties in database management systems?"
        }
    )
    assert chat_res1.status_code == 200, f"Chat failed: {chat_res1.text}"
    chat_data1 = chat_res1.json()
    print(f"-> AI Response received! Answer length: {len(chat_data1['answer'])} chars")
    print(f"-> Answer preview: {chat_data1['answer'][:180]}...")
    if chat_data1.get("sources"):
        print(f"-> Sources cited: {chat_data1['sources']}")

    # 6. Send Question 2 to RAG Document Chat
    print("\n[6] Sending follow-up doubt: 'Explain 3NF vs BCNF differences simply'")
    chat_res2 = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "mode": "document",
            "document_id": doc_id,
            "category": "Study Material",
            "query": "Explain the difference between Third Normal Form (3NF) and Boyce-Codd Normal Form (BCNF) simply."
        }
    )
    assert chat_res2.status_code == 200, f"Chat 2 failed: {chat_res2.text}"
    chat_data2 = chat_res2.json()
    print(f"-> AI Response 2 received! Answer preview: {chat_data2['answer'][:180]}...")

    # 7. Check Chat History & Verify Resumption
    print("\n[7] Querying Chat History for this document (/api/chat/history?document_id=...)")
    hist_res = requests.get(
        f"{BASE_URL}/api/chat/history?document_id={doc_id}",
        headers=headers
    )
    assert hist_res.status_code == 200, f"History fetch failed: {hist_res.text}"
    history_messages = hist_res.json().get("messages", [])
    print(f"-> Found {len(history_messages)} saved messages in history for this document.")
    assert len(history_messages) == 4, f"Expected 4 messages (2 user + 2 assistant), got {len(history_messages)}"
    
    assert history_messages[0]["role"] == "user"
    assert "ACID properties" in history_messages[0]["content"]
    assert history_messages[1]["role"] == "assistant"
    assert history_messages[2]["role"] == "user"
    assert "3NF" in history_messages[2]["content"] and "BCNF" in history_messages[2]["content"]
    assert history_messages[3]["role"] == "assistant"
    print("-> All messages and roles in document chat history match perfectly!")

    # 8. Test General Mentor Chat & History
    print("\n[8] Testing General Mentor Chat (not tied to specific document)")
    gen_chat = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "mode": "general",
            "document_id": None,
            "category": None,
            "query": "How many hours of daily revision do top rankers recommend for UPSC Mains answer writing?"
        }
    )
    assert gen_chat.status_code == 200
    gen_data = gen_chat.json()
    print(f"-> Mentor Answer preview: {gen_data['answer'][:180]}...")

    # Check General Chat History
    gen_hist = requests.get(f"{BASE_URL}/api/chat/history", headers=headers)
    assert gen_hist.status_code == 200
    gen_messages = gen_hist.json().get("messages", [])
    print(f"-> General chat history has {len(gen_messages)} messages.")
    assert len(gen_messages) >= 2
    assert any("UPSC Mains" in m["content"] for m in gen_messages if m["role"] == "user")
    print("-> General chat history stored and retrieved successfully.")

    # 9. Verify Multi-User Isolation (User B cannot see User A's history or docs)
    print("\n[9] Verifying strict isolation with a second user account")
    user_b_email = f"vikram.{unique_suffix}@portal.in"
    reg_b = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={"name": "Vikram Rathore", "email": user_b_email, "password": "Password@2026", "target_exam": "SSC CGL"}
    )
    assert reg_b.status_code == 200
    token_b = reg_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B should see 0 documents
    docs_b = requests.get(f"{BASE_URL}/api/documents", headers=headers_b).json().get("documents", [])
    assert len(docs_b) == 0, f"User B should have 0 docs, got {len(docs_b)}"

    # User B should see 0 chat history for User A's doc
    hist_b = requests.get(f"{BASE_URL}/api/chat/history?document_id={doc_id}", headers=headers_b).json().get("messages", [])
    assert len(hist_b) == 0, f"User B should see 0 messages for doc {doc_id}, got {len(hist_b)}"

    # User B cannot access User A's raw PDF file
    raw_b = requests.get(f"{BASE_URL}/api/documents/{doc_id}/raw", headers=headers_b)
    assert raw_b.status_code == 404, f"User B should receive 404 when requesting User A's file, got {raw_b.status_code}"
    print("-> Strict multi-user data isolation verified! User B cannot see User A's docs, chat, or files.")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
