import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('1. Tap Update Endpoint at 311, 2294...')
run_adb(['shell', 'input', 'tap', '311', '2294'])
time.sleep(1)

print('2. Return to Study Desk tab at 144, 2600...')
run_adb(['shell', 'input', 'tap', '144', '2600'])
time.sleep(2)

# Screenshot Study Desk
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/study_desk_final.png'])
run_adb(['pull', '/sdcard/Download/study_desk_final.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\study_desk_final.png'])
print('Study Desk final screenshot pulled')
