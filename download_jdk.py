import urllib.request
import zipfile
import os
import sys

URL = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13+11/OpenJDK17U-jdk_x64_windows_hotspot_17.0.13_11.zip"
DEST_DIR = r"E:\study material\prep_platform\jdk-17"
ZIP_PATH = r"E:\study material\prep_platform\jdk17.zip"

print(f"Downloading OpenJDK 17 from {URL}...")
os.makedirs(DEST_DIR, exist_ok=True)

def reporthook(blocknum, blocksize, totalsize):
    read = blocknum * blocksize
    if totalsize > 0:
        percent = read * 100 / totalsize
        if blocknum % 500 == 0:
            print(f"Downloaded {read / (1024*1024):.1f} MB of {totalsize / (1024*1024):.1f} MB ({percent:.1f}%)")

urllib.request.urlretrieve(URL, ZIP_PATH, reporthook)
print("Download complete. Extracting...")

with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(DEST_DIR)

print(f"Extracted to {DEST_DIR} successfully!")
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)
