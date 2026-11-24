import urllib.request
import zipfile
import os
import sys

URL = "https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.12/android-studio-2024.2.1.12-windows.zip"
BASE_DIR = r"E:\study material\prep_platform"
DEST_DIR = os.path.join(BASE_DIR, "android-studio")
ZIP_PATH = os.path.join(BASE_DIR, "android-studio.zip")

print(f"Starting Android Studio IDE download from {URL}...")
os.makedirs(DEST_DIR, exist_ok=True)

def reporthook(blocknum, blocksize, totalsize):
    read = blocknum * blocksize
    if totalsize > 0 and blocknum % 2000 == 0:
        percent = read * 100 / totalsize
        print(f"Downloaded {read / (1024*1024):.1f} MB of {totalsize / (1024*1024):.1f} MB ({percent:.1f}%)")

urllib.request.urlretrieve(URL, ZIP_PATH, reporthook)
print("Android Studio download complete. Extracting to", DEST_DIR)

with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(DEST_DIR)

print(f"Android Studio extracted successfully to {DEST_DIR}!")

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

# Create convenient launcher script
launcher_bat = os.path.join(BASE_DIR, "launch_android_studio.bat")
with open(launcher_bat, "w") as f:
    f.write(f"""@echo off
set "JAVA_HOME={BASE_DIR}\\jdk-17\\jdk-17.0.13+11"
set "ANDROID_HOME={BASE_DIR}\\android-sdk"
set "STUDIO_JDK={BASE_DIR}\\jdk-17\\jdk-17.0.13+11"
set "PATH=%JAVA_HOME%\\bin;%ANDROID_HOME%\\platform-tools;%PATH%"

echo Starting Android Studio for Pariksha Copilot...
start "" "{DEST_DIR}\\android-studio\\bin\\studio64.exe" "{BASE_DIR}\\android-app"
""")

print("Created launch_android_studio.bat successfully!")
