import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('Tap Setup Key button around x=900, y=175...')
run_adb(['shell', 'input', 'tap', '900', '175'])
time.sleep(2)

# Screenshot Settings/Profile
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/profile_screen.png'])
run_adb(['pull', '/sdcard/Download/profile_screen.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\profile_screen.png'])
print('Profile screenshot pulled')
