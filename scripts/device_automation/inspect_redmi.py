import subprocess
import requests

subprocess.run(['adb', 'connect', '192.168.29.94:5555'])
res = subprocess.run(['adb', '-s', '192.168.29.94:5555', 'shell', 'whoami'], capture_output=True, text=True)
print('WHOAMI:', res.stdout.strip())

res = subprocess.run(['adb', '-s', '192.168.29.94:5555', 'shell', 'ps -ef'], capture_output=True, text=True)
for line in res.stdout.splitlines():
    if any(k in line.lower() for k in ['nginx', 'uvicorn', 'python', 'main', 'node', 'copilot']):
        print('PROC:', line)

try:
    r = requests.get('http://192.168.29.94:8082', timeout=3)
    print('PORT 8082 HTTP STATUS:', r.status_code, 'Content length:', len(r.text))
except Exception as e:
    print('PORT 8082 ERROR:', e)

try:
    r = requests.get('http://192.168.29.94', timeout=3)
    print('PORT 80 HTTP STATUS:', r.status_code)
except Exception as e:
    print('PORT 80 ERROR:', e)
