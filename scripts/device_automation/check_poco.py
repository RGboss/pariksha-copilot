import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

out, err = run_adb(['shell', 'pm', 'list', 'packages', 'pariksha'])
print('PM LIST PACKAGES PARIKSHA:', out, err)

# Check device model and Android version
out, _ = run_adb(['shell', 'getprop', 'ro.product.model'])
print('MODEL:', out.strip())

out, _ = run_adb(['shell', 'getprop', 'ro.build.version.release'])
print('ANDROID VERSION:', out.strip())

out, _ = run_adb(['shell', 'getprop', 'ro.mi.os.version.incremental'])
print('HYPEROS BUILD:', out.strip())

# Check files in /sdcard/Download
out, _ = run_adb(['shell', 'ls', '-la', '/sdcard/Download'])
print('/sdcard/Download:\n', out)
