import subprocess
import time
import os

DEVICE = '192.168.29.14:46333'
BRAIN_DIR = r"C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3"

def adb(cmd):
    return subprocess.run(['adb', '-s', DEVICE] + cmd, capture_output=True, text=True)

def tap(x, y, desc=""):
    print(f"Tap ({x}, {y}): {desc}")
    adb(['shell', 'input', 'tap', str(x), str(y)])
    time.sleep(1.0)

def capture(name):
    dev_path = f"/sdcard/Download/{name}.png"
    local_path = os.path.join(BRAIN_DIR, f"{name}.png")
    adb(['shell', 'screencap', '-p', dev_path])
    adb(['pull', dev_path, local_path])
    print(f"Captured: {local_path}")
    return local_path

subprocess.run(['adb', 'connect', DEVICE])

# Q1: Tap Option B
tap(450, 953, "Q1: Select Option B")
capture("cbt_q1_selected")

# Next Question
tap(995, 2387, "Next Question -> Q2")
time.sleep(1)

# Q2: Tap Option B
tap(450, 953, "Q2: Select Option B")
tap(995, 2387, "Next Question -> Q3")
time.sleep(1)

# Q3: Tap Option B
tap(450, 953, "Q3: Select Option B")
tap(995, 2387, "Next Question -> Q4")
time.sleep(1)

# Q4: Tap Option B
tap(450, 953, "Q4: Select Option B")
tap(995, 2387, "Next Question -> Q5")
time.sleep(1)
capture("cbt_q5_reached")

# Q5: Tap Option B
tap(450, 953, "Q5: Select Option B")
time.sleep(0.5)

# Submit Exam: tap Submit button at (1100, 216)
tap(1100, 216, "Submit Exam")
time.sleep(2)
capture("cbt_score_card")

# Scroll down to see detailed answer key & explanations
adb(['shell', 'input', 'swipe', '540', '1800', '540', '500', '400'])
time.sleep(1)
capture("cbt_answer_key_explanations")

print("CBT Exam Flow Completed!")
