import urllib.request
import zipfile
import os

URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
SDK_DIR = r"E:\study material\prep_platform\android-sdk"
ZIP_PATH = r"E:\study material\prep_platform\cmdline-tools.zip"
TARGET_DIR = os.path.join(SDK_DIR, "cmdline-tools", "latest")

print(f"Downloading Android command line tools from {URL}...")
os.makedirs(TARGET_DIR, exist_ok=True)

def reporthook(blocknum, blocksize, totalsize):
    read = blocknum * blocksize
    if totalsize > 0 and blocknum % 500 == 0:
        percent = read * 100 / totalsize
        print(f"Downloaded {read / (1024*1024):.1f} MB of {totalsize / (1024*1024):.1f} MB ({percent:.1f}%)")

urllib.request.urlretrieve(URL, ZIP_PATH, reporthook)
print("Download complete. Extracting...")

temp_extract = os.path.join(SDK_DIR, "temp_extract")
with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(temp_extract)

# The zip contains a 'cmdline-tools' folder. Move its contents to 'latest'
import shutil
src_folder = os.path.join(temp_extract, "cmdline-tools")
for item in os.listdir(src_folder):
    s = os.path.join(src_folder, item)
    d = os.path.join(TARGET_DIR, item)
    if os.path.exists(d):
        if os.path.isdir(d):
            shutil.rmtree(d)
        else:
            os.remove(d)
    shutil.move(s, d)

shutil.rmtree(temp_extract)
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

# Pre-accept Android SDK licenses
licenses_dir = os.path.join(SDK_DIR, "licenses")
os.makedirs(licenses_dir, exist_ok=True)
with open(os.path.join(licenses_dir, "android-sdk-license"), "w") as f:
    f.write("24333f8a63b6825ea9c5514f83c2829b004d1fee\n")
    f.write("d56f5187479451eabf01fb78af6dfcb131a6481e\n")
    f.write("84831b9409646a918e30573bab4c9c91346d8abd\n")
    f.write("8933bad161af4178b1185d1a37fbf41ea5269c55\n")

with open(os.path.join(licenses_dir, "android-sdk-preview-license"), "w") as f:
    f.write("84831b9409646a918e30573bab4c9c91346d8abd\n")

print("Android SDK command-line tools installed and licenses pre-accepted successfully!")
