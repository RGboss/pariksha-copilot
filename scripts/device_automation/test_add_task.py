import subprocess
import time
import os

DEVICE = '192.168.29.14:46333'
BRAIN_DIR = r"C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3"

def adb(cmd):
    return subprocess.run(['adb', '-s', DEVICE] + cmd, capture_output=True, text=True)

# 1. Tap Add Task button (+ icon)
adb(['shell', 'input', 'tap', '960', '804'])
time.sleep(1.2)

# 2. Tap Task Description field
adb(['shell', 'input', 'tap', '500', '930'])
time.sleep(0.5)

# 3. Enter task text
adb(['shell', 'input', 'text', 'Revise%sDistributed%sTransactions'])
time.sleep(0.5)

# 4. Hide software keyboard so dialog buttons are fully visible
adb(['shell', 'input', 'keyevent', '111'])
time.sleep(0.5)

# 5. Capture dialog with text filled
dev_path = "/sdcard/Download/dialog_ready.png"
local_path = os.path.join(BRAIN_DIR, "dialog_ready.png")
adb(['shell', 'screencap', '-p', dev_path])
adb(['pull', dev_path, local_path])

# 6. Tap 'Add Task' button at (780, 1470)
adb(['shell', 'input', 'tap', '780', '1470'])
time.sleep(1.5)

# 7. Capture Study Desk after adding task
dev_path2 = "/sdcard/Download/desk_after_real_add.png"
local_path2 = os.path.join(BRAIN_DIR, "desk_after_real_add.png")
adb(['shell', 'screencap', '-p', dev_path2])
adb(['pull', dev_path2, local_path2])

print("Task addition flow executed!")
