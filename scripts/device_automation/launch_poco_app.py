import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('Launching com.pariksha.copilot...')
out, err = run_adb(['shell', 'am', 'start', '-n', 'com.pariksha.copilot/.MainActivity'])
print('LAUNCH:', out, err)

time.sleep(3)

# Check top activity
out, _ = run_adb(['shell', 'dumpsys', 'window', '|', 'grep', '-E', '"mCurrentFocus|mFocusedApp"'])
print('FOCUSED APP:\n', out)

# Capture screenshot
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/pariksha_poco_running.png'])
run_adb(['pull', '/sdcard/Download/pariksha_poco_running.png', 'E:\\study material\\prep_platform\\pariksha_poco_running.png'])
print('Pulled screenshot')
