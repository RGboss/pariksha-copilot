import xml.etree.ElementTree as ET

tree = ET.parse('E:\\study material\\prep_platform\\ui_details.xml')
root = tree.getroot()
for elem in root.iter('node'):
    if 'Install without scanning' in elem.attrib.get('text', ''):
        print('FOUND NODE:', elem.attrib)
    for k, v in elem.attrib.items():
        if 'Install' in v:
            print('ATTR:', k, v, elem.attrib.get('bounds'))
