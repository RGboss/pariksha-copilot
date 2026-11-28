import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

run_adb(['shell', 'uiautomator', 'dump', '/sdcard/Download/ui_profile.xml'])
run_adb(['pull', '/sdcard/Download/ui_profile.xml', r'E:\study material\prep_platform\ui_profile_poco.xml'])

import xml.etree.ElementTree as ET
try:
    tree = ET.parse(r'E:\study material\prep_platform\ui_profile_poco.xml')
    root = tree.getroot()
    for elem in root.iter('node'):
        text = elem.attrib.get('text')
        content_desc = elem.attrib.get('content-desc')
        bounds = elem.attrib.get('bounds')
        if any(k in (text or '').lower() or k in (content_desc or '').lower() for k in ['endpoint', 'sync', 'model', 'save', 'key']):
            print(f'ITEM: TEXT: "{text}" | DESC: "{content_desc}" | BOUNDS: {bounds}')
except Exception as e:
    print('Error parsing XML:', e)
