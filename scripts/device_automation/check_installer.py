import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

out, _ = run_adb(['shell', 'pm', 'list', 'packages', '|', 'grep', 'packageinstaller'])
print('PACKAGE INSTALLER PKGS:\n', out)

out, _ = run_adb(['shell', 'settings', 'get', 'global', 'install_non_market_apps'])
print('install_non_market_apps:', out.strip())

out, _ = run_adb(['shell', 'settings', 'get', 'secure', 'install_non_market_apps'])
print('secure install_non_market_apps:', out.strip())
