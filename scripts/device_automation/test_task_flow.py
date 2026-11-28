import subprocess
import time

DEVICE = '192.168.29.14:46333'
def adb(cmd):
    return subprocess.run(['adb', '-s', DEVICE] + cmd, capture_output=True, text=True)

subprocess.run(['adb', 'connect', DEVICE])

# 1. Open Add Task dialog
print("1. Opening Add Task Dialog...")
adb(['shell', 'input', 'tap', '960', '583'])
time.sleep(1.0)

# 2. Type task description
print("2. Entering task text...")
adb(['shell', 'input', 'tap', '300', '1180'])
time.sleep(0.5)
adb(['shell', 'input', 'text', 'Revise%sDistributed%sTransactions'])
time.sleep(0.5)

# 3. Dismiss soft keyboard cleanly with BACK keyevent
print("3. Dismissing keyboard...")
adb(['shell', 'input', 'keyevent', '4'])
time.sleep(0.8)

# 4. Tap 'Add Task' button at (951, 1758)
print("4. Tapping Add Task button at 951, 1758...")
adb(['shell', 'input', 'tap', '951', '1758'])
time.sleep(1.5)

# 5. Check Study Desk
print("5. Dumping UI to verify new task...")
adb(['shell', 'uiautomator', 'dump', '/sdcard/Download/desk_verified.xml'])
adb(['pull', '/sdcard/Download/desk_verified.xml', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\desk_verified.xml'])
print("Done!")
