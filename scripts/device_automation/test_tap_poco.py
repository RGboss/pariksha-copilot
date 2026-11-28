import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

# Tap "Browse" tab at (912, 2594)
out, err = run_adb(['shell', 'input', 'tap', '912', '2594'])
print('TAP RESULT:\nSTDOUT:', out, '\nSTDERR:', err)
