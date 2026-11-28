import subprocess
import os

apk_path = r"E:\study material\prep_platform\android-app\app\build\outputs\apk\debug\app-debug.apk"
print('Local APK exists:', os.path.exists(apk_path), 'Size:', os.path.getsize(apk_path))

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

print('Pushing APK to /sdcard/Download/pariksha_copilot.apk...')
out, err = run_adb(['push', apk_path, '/sdcard/Download/pariksha_copilot.apk'])
print('PUSH:', out, err)

print('Copying to /data/local/tmp/pariksha_copilot.apk...')
run_adb(['shell', 'cp', '/sdcard/Download/pariksha_copilot.apk', '/data/local/tmp/pariksha_copilot.apk'])
run_adb(['shell', 'chmod', '777', '/data/local/tmp/pariksha_copilot.apk'])

print('Attempting pm install...')
out, err = run_adb(['shell', 'pm', 'install', '-r', '-g', '/data/local/tmp/pariksha_copilot.apk'])
print('PM INSTALL RESULT:\nSTDOUT:', out, '\nSTDERR:', err)
