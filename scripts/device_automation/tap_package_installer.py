import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

# Tap "Package installer" at (895, 2351)
print('Tapping Package installer...')
run_adb(['shell', 'input', 'tap', '895', '2351'])
time.sleep(1)

# Tap "Always" or "Once" at (404, 2513) or (815, 2513)
print('Tapping Always at 815, 2513...')
run_adb(['shell', 'input', 'tap', '815', '2513'])
time.sleep(2)

# Dump UI to see what prompt appears (Do you want to install this app? / Install button)
run_adb(['shell', 'uiautomator', 'dump', '/sdcard/Download/ui_install2.xml'])
run_adb(['pull', '/sdcard/Download/ui_install2.xml', 'E:\\study material\\prep_platform\\ui_install2_poco.xml'])

import xml.etree.ElementTree as ET
try:
    tree = ET.parse('E:\\study material\\prep_platform\\ui_install2_poco.xml')
    root = tree.getroot()
    for elem in root.iter('node'):
        text = elem.attrib.get('text')
        content_desc = elem.attrib.get('content-desc')
        bounds = elem.attrib.get('bounds')
        resource_id = elem.attrib.get('resource-id')
        if text or content_desc:
            print(f'TEXT: "{text}" | ID: {resource_id} | BOUNDS: {bounds}')
except Exception as e:
    print('Error parsing XML:', e)

# Also capture screenshot
run_adb(['shell', 'screencap', '-p', '/sdcard/Download/screen_install2.png'])
run_adb(['pull', '/sdcard/Download/screen_install2.png', 'E:\\study material\\prep_platform\\screen_install2.png'])
