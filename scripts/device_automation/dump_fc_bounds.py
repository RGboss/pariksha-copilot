import subprocess

def run_adb(cmd_list):
    full_cmd = ['adb', '-s', '192.168.29.14:46333'] + cmd_list
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

subprocess.run(['adb', 'connect', '192.168.29.14:46333'])

run_adb(['shell', 'uiautomator', 'dump', '/sdcard/Download/ui_fc.xml'])
run_adb(['pull', '/sdcard/Download/ui_fc.xml', r'E:\study material\prep_platform\ui_fc_poco.xml'])

import xml.etree.ElementTree as ET
try:
    tree = ET.parse(r'E:\study material\prep_platform\ui_fc_poco.xml')
    root = tree.getroot()
    for elem in root.iter('node'):
        text = elem.attrib.get('text')
        content_desc = elem.attrib.get('content-desc')
        bounds = elem.attrib.get('bounds')
        if text or content_desc:
            print(f'TEXT: "{text}" | DESC: "{content_desc}" | BOUNDS: {bounds}')
except Exception as e:
    print('Error parsing XML:', e)
