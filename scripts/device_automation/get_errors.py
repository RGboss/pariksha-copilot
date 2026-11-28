import subprocess
import os

env = os.environ.copy()
env["JAVA_HOME"] = r"C:\Program Files\Microsoft\jdk-17.0.21.102-hotspot"
env["ANDROID_HOME"] = r"E:\study material\prep_platform\android-sdk"
env["PATH"] = rf"{env['JAVA_HOME']}\bin;{env['ANDROID_HOME']}\platform-tools;{env['PATH']}"

proc = subprocess.run(
    [r"E:\study material\prep_platform\android-app\gradlew.bat", "compileDebugKotlin", "--info"],
    cwd=r"E:\study material\prep_platform\android-app",
    env=env,
    capture_output=True,
    text=True
)

for line in proc.stdout.splitlines():
    if ".kt:" in line or "e: " in line or "error:" in line.lower():
        print(line)
