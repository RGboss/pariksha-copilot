import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('1. Tap Got It! (+1 Box) button around x=720, y=1220...')
run_adb(['shell', 'input', 'tap', '720', '1220'])
time.sleep(1)

print('2. Navigate to AI Tutor tab at 370, 2600...')
run_adb(['shell', 'input', 'tap', '370', '2600'])
time.sleep(2)

# Screenshot AI Tutor
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/tutor_screen.png'])
run_adb(['pull', '/sdcard/Download/tutor_screen.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\tutor_screen.png'])
print('Tutor screenshot pulled')
