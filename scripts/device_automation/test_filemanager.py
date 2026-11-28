import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

# Find activities for File Manager or Downloads
out, _ = run_adb(['shell', 'pm', 'dump', 'com.mi.android.globalFileexplorer', '|', 'grep', '-A', '2', 'android.intent.action.MAIN'])
print('FILE EXPLORER MAIN:\n', out[:500])

# Launch File Manager
out, err = run_adb(['shell', 'monkey', '-p', 'com.mi.android.globalFileexplorer', '-c', 'android.intent.category.LAUNCHER', '1'])
print('LAUNCH FILE EXPLORER:\n', out, err)

time.sleep(2)
out, _ = run_adb(['shell', 'dumpsys', 'window', '|', 'grep', '-E', '"mCurrentFocus|mFocusedApp"'])
print('FOCUSED APP:\n', out)
