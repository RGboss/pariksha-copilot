import subprocess
import ctypes
import time
import sys

# Prevent Windows PC sleep: ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED = 0x80000001 | 0x00000002 = 0x80000003
try:
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
    print("PC keep-awake activated via SetThreadExecutionState.")
except Exception as e:
    print(f"PC keep-awake warning: {e}")

# Android keep-awake
devices = ['192.168.29.14:46333', '192.168.29.94:5555']
for dev in devices:
    try:
        subprocess.run(['adb', 'connect', dev], capture_output=True)
        # stay on while plugged/charging
        subprocess.run(['adb', '-s', dev, 'shell', 'svc', 'power', 'stayon', 'true'], capture_output=True)
        # screen timeout max (24 hours = 86400000 ms)
        subprocess.run(['adb', '-s', dev, 'shell', 'settings', 'put', 'system', 'screen_off_timeout', '86400000'], capture_output=True)
        # wake screen if sleeping
        subprocess.run(['adb', '-s', dev, 'shell', 'input', 'keyevent', '224'], capture_output=True)
        print(f"Android device {dev} stayon set to true (timeout 24h, screen awake).")
    except Exception as e:
        print(f"Device {dev} keep-awake warning: {e}")
