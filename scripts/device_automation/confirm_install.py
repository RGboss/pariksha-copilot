import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('Tapping Install button at 994, 1521...')
run_adb(['shell', 'input', 'tap', '994', '1521'])

for i in range(10):
    time.sleep(2)
    out, _ = run_adb(['shell', 'pm', 'list', 'packages', 'pariksha'])
    print(f'Check {i}: {out.strip()}')
    if 'com.pariksha.copilot' in out:
        print('SUCCESS: com.pariksha.copilot is INSTALLED!')
        break

# Capture UI/screenshot after install
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/screen_after_install.png'])
run_adb(['pull', '/sdcard/Download/screen_after_install.png', 'E:\\study material\\prep_platform\\screen_after_install.png'])
