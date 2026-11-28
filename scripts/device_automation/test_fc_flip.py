import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('1. Tap card surface at 610, 1050...')
run_adb(['shell', 'input', 'tap', '610', '1050'])
time.sleep(1)

# Screenshot flipped card
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/fc_flipped_real.png'])
run_adb(['pull', '/sdcard/Download/fc_flipped_real.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\fc_flipped_real.png'])

print('2. Tap Next button at 1050, 1390...')
run_adb(['shell', 'input', 'tap', '1050', '1390'])
time.sleep(1)

# Screenshot Card 2
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/fc_card2_real.png'])
run_adb(['pull', '/sdcard/Download/fc_card2_real.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\fc_card2_real.png'])
print('Flashcard flip and advance complete')
