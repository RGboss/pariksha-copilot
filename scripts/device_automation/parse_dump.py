import xml.etree.ElementTree as ET
import sys

xml_file = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\rahul\.gemini\antigravity\brain\6ac72448-ba83-412e-bea0-991bfee488d3\current_view.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

for node in root.iter():
    t = node.attrib.get('text', '')
    d = node.attrib.get('content-desc', '')
    b = node.attrib.get('bounds', '')
    c = node.attrib.get('class', '')
    if t or d:
        print(f"[{b}] text='{t}' desc='{d}'")
