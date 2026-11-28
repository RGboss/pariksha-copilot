import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

out, _ = run_adb(['logcat', '-d', '-t', '150', '-s', 'InstallFailed,PackageInstaller,vending,PackageManager'])
print('LOGCAT INSTALL:\n', out)
