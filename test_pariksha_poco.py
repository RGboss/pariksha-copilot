import subprocess
import time
import os

DEVICE = '192.168.29.14:46333'
BRAIN_DIR = r"C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3"

def adb(cmd):
    full = ['adb', '-s', DEVICE] + cmd
    return subprocess.run(full, capture_output=True, text=True)

def tap(x, y, desc=""):
    print(f"Tap: ({x}, {y}) - {desc}")
    adb(['shell', 'input', 'tap', str(x), str(y)])
    time.sleep(1.2)

def swipe(x1, y1, x2, y2, duration=300):
    adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])
    time.sleep(1.0)

def key(code):
    adb(['shell', 'input', 'keyevent', str(code)])
    time.sleep(0.5)

def text(t):
    adb(['shell', 'input', 'text', t.replace(' ', '%s')])
    time.sleep(0.8)

def capture(name):
    dev_path = f"/sdcard/Download/{name}.png"
    local_path = os.path.join(BRAIN_DIR, f"{name}.png")
    adb(['shell', 'screencap', '-p', dev_path])
    adb(['pull', dev_path, local_path])
    print(f"Captured screenshot: {local_path}")
    return local_path

print("=== STARTING PARIKSHA COPILOT TEST SUITE ON POCO X6 PRO ===")
subprocess.run(['adb', 'connect', DEVICE])

# 1. Wake device and ensure app is foreground
adb(['shell', 'svc power stayon true'])
adb(['shell', 'input keyevent 224'])
adb(['shell', 'am start -n com.pariksha.copilot/.MainActivity'])
time.sleep(2)

# --- TEST 1: STUDY DESK & ADD CUSTOM TASK ---
print("\n--- TEST 1: Study Desk & Add Task Dialog ---")
# Tap '+ Add' button at (786, 750)
tap(786, 750, "Open Add Task Dialog")
capture("test1_add_task_dialog")

# Enter Task Title: click title field (approx 540, 1150)
tap(540, 1150, "Focus Task Title input")
text("Revise%sDistributed%sTransactions")
key(66) # Enter
time.sleep(0.5)

# Select Subject: 'DBMS' is preselected or click it
tap(350, 1370, "Select Subject chip")
# Enter Duration
tap(540, 1530, "Focus Duration input")
text("45%smins")
key(66)
capture("test1_task_filled")

# Tap 'Add Task' button at bottom of dialog (around 750, 1750)
tap(750, 1750, "Confirm Add Task")
time.sleep(1)
capture("test1_desk_after_add")

# Tap on a task checkbox to toggle (e.g. at 105, 930)
tap(105, 930, "Toggle Task Checkbox")
time.sleep(1)
capture("test1_task_toggled")

# --- TEST 2: CBT MOCK EXAM SIMULATOR ---
print("\n--- TEST 2: CBT Mock Exam Simulator ---")
# Tap Mock CBT tab in bottom navigation (around 540, 2600)
tap(540, 2600, "Navigate to Mock CBT Tab")
time.sleep(1.5)
capture("test2_cbt_library")

# Tap 'Start Mock Exam' on the first test: DBMS & Normalization CBT Mock (approx 850, 1020)
tap(850, 1020, "Start DBMS Mock Test")
time.sleep(1.5)
capture("test2_quiz_q1")

# Select Option B: 'Candidate Key' (approx 540, 1120)
tap(540, 1120, "Select Option B for Q1")
time.sleep(0.8)
capture("test2_quiz_q1_selected")

# Tap 'Next' (approx 890, 2580)
tap(890, 2580, "Next Question -> Q2")
time.sleep(1)
capture("test2_quiz_q2")

# Q2: Select Option B: 'Isolation' (approx 540, 1120)
tap(540, 1120, "Select Option B for Q2")
time.sleep(0.8)
# Tap 'Next' -> Q3
tap(890, 2580, "Next Question -> Q3")
time.sleep(1)

# Q3: Select Option B: 'Non-prime attributes...' (approx 540, 1200)
tap(540, 1200, "Select Option B for Q3")
time.sleep(0.8)
# Tap 'Next' -> Q4
tap(890, 2580, "Next Question -> Q4")
time.sleep(1)

# Q4: Select Option B: 'Left deep tree' (approx 540, 1120)
tap(540, 1120, "Select Option B for Q4")
time.sleep(0.8)
# Tap 'Next' -> Q5
tap(890, 2580, "Next Question -> Q5")
time.sleep(1)
capture("test2_quiz_q5")

# Q5: Select Option B: 'Recoverable' (approx 540, 1120)
tap(540, 1120, "Select Option B for Q5")
time.sleep(0.8)

# Submit Quiz: tap 'Submit Test' button (approx 890, 2580)
tap(890, 2580, "Submit CBT Exam")
time.sleep(2)
capture("test2_quiz_score_report")

# Scroll down to inspect Answer Key & Explanations
swipe(540, 2000, 540, 700, 400)
time.sleep(1)
capture("test2_quiz_rationales")

# --- TEST 3: FLASHCARDS INTERACTION ---
print("\n--- TEST 3: Leitner Flashcards ---")
# Tap Flashcards tab (approx 740, 2600)
tap(740, 2600, "Navigate to Flashcards Tab")
time.sleep(1.5)
capture("test3_flashcards_screen")

# Tap card to flip (approx 540, 950)
tap(540, 950, "Flip Flashcard")
time.sleep(1)
capture("test3_card_flipped")

# Tap 'Next' card (approx 870, 1370)
tap(870, 1370, "Next Flashcard")
time.sleep(1)
capture("test3_card2")

# --- TEST 4: AI TUTOR TAB & OFFLINE TUTOR ---
print("\n--- TEST 4: AI Faculty Tutor ---")
# Tap AI Tutor tab (approx 320, 2600)
tap(320, 2600, "Navigate to AI Tutor Tab")
time.sleep(1.5)
capture("test4_tutor_screen")

# Tap suggested chip or send message
tap(540, 2400, "Tap Quick Prompt Chip")
time.sleep(2)
capture("test4_tutor_response")

# --- TEST 5: PROFILE & SYSTEM STATE ---
print("\n--- TEST 5: Profile & System Settings ---")
# Tap Profile tab (approx 930, 2600)
tap(930, 2600, "Navigate to Profile Tab")
time.sleep(1.5)
capture("test5_profile_screen")

print("=== ALL REGRESSIVE TESTS COMPLETED SUCCESSFULLY ===")
