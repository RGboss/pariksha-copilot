import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

# Try launching google packageinstaller or miui packageinstaller with action VIEW
out, err = run_adb(['shell', 'am', 'start', '-n', 'com.google.android.packageinstaller/com.android.packageinstaller.PackageInstallerActivity', '-d', 'file:///sdcard/Download/pariksha_copilot.apk', '-t', 'application/vnd.android.package-archive'])
print('GOOGLE PACKAGEINSTALLER START:\n', out, err)

# Or com.miui.global.packageinstaller
out, err = run_adb(['shell', 'am', 'start', '-n', 'com.miui.global.packageinstaller/com.android.packageinstaller.PackageInstallerActivity', '-d', 'file:///sdcard/Download/pariksha_copilot.apk', '-t', 'application/vnd.android.package-archive'])
print('MIUI PACKAGEINSTALLER START:\n', out, err)

time.sleep(2)
out, _ = run_adb(['shell', 'dumpsys', 'window', '|', 'grep', '-E', '"mCurrentFocus|mFocusedApp"'])
print('FOCUSED APP:\n', out)
