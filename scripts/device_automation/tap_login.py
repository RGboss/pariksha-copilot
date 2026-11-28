import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('Tapping Quick Demo Login at 639, 1852...')
run_adb(['shell', 'input', 'tap', '639', '1852'])
time.sleep(2)

# Dump UI on Study Desk
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/desk_poco.png'])
run_adb(['pull', '/sdcard/Download/desk_poco.png', 'E:\\study material\\prep_platform\\desk_poco.png'])
run_adb(['pull', '/sdcard/Download/desk_poco.png', 'C:\\Users\\rahul\\.gemini\\antigravity\\brain\\6ac72448-ba83-412e-bea0-991bfee488d3\\desk_poco.png'])
print('Pulled Study Desk screenshot')
