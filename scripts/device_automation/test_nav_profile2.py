import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('Tap Profile tab at 1074, 2597...')
run_adb(['shell', 'input', 'tap', '1074', '2597'])
time.sleep(2)

# Screenshot Profile
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/profile_screen2.png'])
run_adb(['pull', '/sdcard/Download/profile_screen2.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\profile_screen2.png'])
print('Profile screenshot 2 pulled')
