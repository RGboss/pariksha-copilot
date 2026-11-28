import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('1. Tap flashcard to flip and reveal answer (center at 610, 800)...')
run_adb(['shell', 'input', 'tap', '610', '800'])
time.sleep(1)

# Screenshot flipped card
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/fc_flipped.png'])
run_adb(['pull', '/sdcard/Download/fc_flipped.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\fc_flipped.png'])

print('2. Tap Next button (center at 870, 1020)...')
run_adb(['shell', 'input', 'tap', '870', '1020'])
time.sleep(1)

# Screenshot next card
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/fc_card2.png'])
run_adb(['pull', '/sdcard/Download/fc_card2.png', r'C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\fc_card2.png'])
print('Step 1 and 2 done')
