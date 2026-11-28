import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

# Check current top activity on POCO
out, err = run_adb(['shell', 'dumpsys', 'window', '|', 'grep', '-E', '"mCurrentFocus|mFocusedApp"'])
print('FOCUSED APP:\n', out)

# Try launching package installer intent via am start
# On modern Android, installing from file URI requires FileProvider or content URI, or package installer activity:
# action: android.intent.action.VIEW
# data: content or file
# type: application/vnd.android.package-archive
out, err = run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'file:///sdcard/Download/pariksha_copilot.apk', '-t', 'application/vnd.android.package-archive'])
print('AM START RESULT:\n', out, err)
