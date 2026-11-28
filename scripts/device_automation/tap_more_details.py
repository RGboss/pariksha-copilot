import subprocess
import time

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

print('Tapping More details at 576, 1560...')
run_adb(['shell', 'input', 'tap', '576', '1560'])
time.sleep(1)

# Dump UI
run_adb(['shell', 'uiautomator', 'dump', '/sdcard/Download/ui_details.xml'])
run_adb(['pull', '/sdcard/Download/ui_details.xml', 'E:\\study material\\prep_platform\\ui_details.xml'])

import xml.etree.ElementTree as ET
try:
    tree = ET.parse('E:\\study material\\prep_platform\\ui_details.xml')
    root = tree.getroot()
    for elem in root.iter('node'):
        text = elem.attrib.get('text')
        content_desc = elem.attrib.get('content-desc')
        bounds = elem.attrib.get('bounds')
        if text or content_desc:
            print(f'TEXT: "{text}" | DESC: "{content_desc}" | BOUNDS: {bounds}')
except Exception as e:
    print('Error parsing XML:', e)
