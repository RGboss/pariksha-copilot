import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

apk_path = r"E:\study material\prep_platform\release\pariksha-copilot.apk"
print('1. Pushing updated APK to POCO...')
out, err = run_adb(['push', apk_path, '/sdcard/Download/pariksha_copilot.apk'])
print('PUSH:', out, err)

print('2. Launching File Manager to trigger update...')
run_adb(['shell', 'monkey', '-p', 'com.mi.android.globalFileexplorer', '-c', 'android.intent.category.LAUNCHER', '1'])
time.sleep(2)

# Tap Browse -> Download -> pariksha_copilot.apk
print('Navigating File Manager...')
run_adb(['shell', 'input', 'tap', '912', '2594']) # Browse tab
time.sleep(1)
run_adb(['shell', 'input', 'tap', '302', '1894']) # Download folder
time.sleep(1)
run_adb(['shell', 'input', 'tap', '405', '2208']) # pariksha_copilot.apk
time.sleep(2)

# In Package installer, tap "Update" button (usually at same position as Install: 994, 1521 or similar)
print('Tapping Update/Install at 994, 1521...')
run_adb(['shell', 'input', 'tap', '994', '1521'])
time.sleep(2)

# If Play Protect dialog appears, tap "Install without scanning" at 600, 1600 or Scan app
run_adb(['shell', 'input', 'tap', '600', '1600'])
time.sleep(3)

# Dump UI to see current state
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/screen_after_update.png'])
run_adb(['pull', '/sdcard/Download/screen_after_update.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\screen_after_update.png'])
print('Update flow completed')
