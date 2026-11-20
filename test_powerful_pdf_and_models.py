import os
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_features():
    print("=== STARTING MULTI-MODEL, TOKEN OPTIMIZATION & PYMUPDF PDF ANALYSIS TESTS ===")

    # 1. Test /api/models
    print("\n[1] Testing GET /api/models")
    res = requests.get(f"{BASE_URL}/api/models")
    assert res.status_code == 200, f"Failed /api/models: {res.text}"
    data = res.json()
    models = data["models"]
    model_ids = [m["id"] for m in models]
    print(f"-> Supported models found: {model_ids}")
    assert "gemini-2.5-flash" in model_ids
    assert "gemini-2.5-pro" in model_ids
    assert "gemini-1.5-flash" in model_ids
    assert "offline-curriculum" in model_ids
    print("-> All candidate models & offline curriculum available.")

    # 2. Register user & test preferred_model preference
    unique_id = uuid.uuid4().hex[:6]
    email = f"officer.{unique_id}@portal.in"
    reg = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={
            "name": "Officer Test",
            "email": email,
            "password": "Password123!",
            "target_exam": "UPSC Civil Services 2027"
        }
    )
    assert reg.status_code == 200, f"Signup failed: {reg.text}"
    token = reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n[2] Updating user preferred model to 'gemini-2.5-pro'")
    up_res = requests.put(
        f"{BASE_URL}/api/user",
        headers=headers,
        json={"preferred_model": "gemini-2.5-pro"}
    )
    assert up_res.status_code == 200
    assert up_res.json()["preferred_model"] == "gemini-2.5-pro"
    print("-> User preferred model updated to gemini-2.5-pro.")

    # 3. Test PyMuPDF PDF extraction and rich metadata storage
    print("\n[3] Testing PyMuPDF Extraction & Data Storage on PDF Upload")
    test_pdf = r"E:\study material\banking\GK\budgetspeech.pdf"
    assert os.path.exists(test_pdf), f"PDF missing: {test_pdf}"

    with open(test_pdf, "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/api/documents/upload",
            headers=headers,
            files={"file": ("Union_Budget_Speech.pdf", f, "application/pdf")},
            data={"category": "Study Material"}
        )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    doc = upload_res.json()
    print(f"-> Document ID: {doc['id']}")
    print(f"-> Page Count: {doc['page_count']}")
    print(f"-> Chunks Created: {doc['chunk_count']}")
    print(f"-> Extracted Chars: {doc['extracted_chars']:,}")
    print(f"-> SHA-256 File Hash: {doc.get('file_hash')}")
    print(f"-> Table of Contents Items: {len(doc.get('toc', []))}")
    assert doc["page_count"] > 0
    assert doc["chunk_count"] > 0
    assert doc["extracted_chars"] > 0
    assert doc.get("file_hash") is not None
    print("-> PyMuPDF structural extraction & powerful SQLite metadata verified!")

    # 4. Test Token Optimization & Chat with specific models
    print("\n[4] Testing RAG Chat with 'gemini-2.5-flash'")
    chat_flash = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "mode": "document",
            "document_id": doc["id"],
            "query": "What are the earliest historical events mentioned?",
            "model": "gemini-2.5-flash"
        }
    )
    assert chat_flash.status_code == 200
    res_flash = chat_flash.json()
    print(f"-> Response Model: {res_flash.get('model')}")
    print(f"-> Token Usage: {res_flash.get('token_usage')}")
    assert "token_usage" in res_flash

    print("\n[5] Testing RAG Chat with 'offline-curriculum' (Zero Quota Mode)")
    chat_offline = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "mode": "document",
            "document_id": doc["id"],
            "query": "Give me historical facts from page 1",
            "model": "offline-curriculum"
        }
    )
    assert chat_offline.status_code == 200
    res_offline = chat_offline.json()
    print(f"-> Response Model: {res_offline.get('model')}")
    print(f"-> Offline Token Usage: {res_offline.get('token_usage')}")
    assert res_offline["token_usage"]["total_tokens"] == 0
    print("-> 100% Free / Zero Cloud Tokens verified for offline mode!")

    # 5. Test General Mentor Chat with model selection
    print("\n[6] Testing General Mentor Chat with 'gemini-1.5-flash'")
    chat_gen = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "mode": "general",
            "query": "How should I structure my GS paper 1 revision in the last 30 days?",
            "model": "gemini-1.5-flash"
        }
    )
    assert chat_gen.status_code == 200
    res_gen = chat_gen.json()
    print(f"-> General Mentor Model: {res_gen.get('model')}")
    print(f"-> General Mentor Tokens: {res_gen.get('token_usage')}")
    assert "token_usage" in res_gen

    # 6. Test Strategy Generation with Model selection
    print("\n[7] Testing Strategy Generation with 'offline-curriculum'")
    strat_res = requests.post(
        f"{BASE_URL}/api/strategy/generate",
        headers=headers,
        json={
            "exam_name": "UPSC Civil Services 2027",
            "daily_hours": 6.0,
            "prep_level": "Advanced",
            "model": "offline-curriculum"
        }
    )
    assert strat_res.status_code == 200
    strat_data = strat_res.json()
    assert "16-Week Preparation Roadmap" in strat_data["strategy_markdown"]
    print("-> Strategy generated successfully with model parameter!")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_features()
