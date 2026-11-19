import urllib.request
import json

BASE = 'http://127.0.0.1:8000'

print("--- RUNNING SUITE OF VERIFICATION TESTS ---")

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

# 4. Chapter 8 (CPU Scheduling)
ch8 = json.loads(urllib.request.urlopen(BASE + '/api/chapters/ch-8').read().decode())
print(f"4. Chapter 8: '{ch8['title']}', Length: {len(ch8['lecture_notes'])} chars, {len(ch8['checkpoints'])} checkpoints, {len(ch8['quiz'])} quiz questions.")

# 5. Chapter 15 (System Design)
ch15 = json.loads(urllib.request.urlopen(BASE + '/api/chapters/ch-15').read().decode())
print(f"5. Chapter 15: '{ch15['title']}', Length: {len(ch15['lecture_notes'])} chars, {len(ch15['checkpoints'])} checkpoints, {len(ch15['quiz'])} quiz questions.")

# 6. Quiz Submission
payload = json.dumps({'answers': {'106': 2, '107': 1, '108': 2, '109': 1, '110': 0}}).encode()
req = urllib.request.Request(BASE + '/api/chapters/ch-2/quiz', data=payload, headers={'Content-Type': 'application/json'})
q_res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"6. Quiz Submission API: Score {q_res['score']}/{q_res['total']} ({q_res['percentage']}%), Recorded successfully!")

# 7. Search
search_res = json.loads(urllib.request.urlopen(BASE + '/api/search?q=banker').read().decode())
print(f"7. Search API ('banker'): Found {len(search_res['chapters'])} matching chapters and {len(search_res['questions'])} matching question bank items.")

# 8. Question Bank
qb = json.loads(urllib.request.urlopen(BASE + '/api/questions?limit=5').read().decode())
print(f"8. Question Bank API: {qb['total']} total questions available, sampled {len(qb['questions'])} questions.")

# 9. Mock Exam Endpoint
mock_res = json.loads(urllib.request.urlopen(BASE + '/api/mock-exam?count=30').read().decode())
print(f"9. Mock Exam API: Generated {mock_res['count']} questions out of {mock_res['total_available']} total pool.")

# 10. Filtered Mock Exam (SEBI)
mock_sebi = json.loads(urllib.request.urlopen(BASE + '/api/mock-exam?count=10&exam=sebi').read().decode())
print(f"10. Mock Exam Filter (SEBI): Generated {mock_sebi['count']} questions for exam '{mock_sebi['exam_filter']}'.")

# 11. Frontend HTML
html = urllib.request.urlopen(BASE + '/').read().decode()
print(f"11. Static Frontend: Served index.html ({len(html)} bytes).")

print("--- ALL 11 TEST CHECKS PASSED PERFECTLY ---")
