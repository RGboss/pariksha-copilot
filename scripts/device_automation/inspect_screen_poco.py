import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

time.sleep(1)
out, _ = run_adb(['shell', 'dumpsys', 'window', 'displays'])
for line in out.splitlines():
    if any(k in line.lower() for k in ['mcurrentfocus', 'mfocusedapp', 'packageinstaller', 'miui']):
        print('WINDOW:', line.strip())

# Take a screenshot to inspect
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/screen_poco.png'])
run_adb(['pull', '/sdcard/Download/screen_poco.png', 'E:\\study material\\prep_platform\\screen_poco.png'])
print('Screenshot pulled')
