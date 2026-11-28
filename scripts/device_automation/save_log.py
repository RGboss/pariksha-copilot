import subprocess
import os

env = os.environ.copy()
env["JAVA_HOME"] = r"C:\Program Files\Microsoft\jdk-17.0.21.102-hotspot"
env["ANDROID_HOME"] = r"E:\study material\prep_platform\android-sdk"
env["PATH"] = rf"{env['JAVA_HOME']}\bin;{env['ANDROID_HOME']}\platform-tools;{env['PATH']}"

proc = subprocess.run(
    [r"E:\study material\prep_platform\android-app\gradlew.bat", "compileDebugKotlin"],
    cwd=r"E:\study material\prep_platform\android-app",
    env=env,
    capture_output=True,
    text=True
)

with open(r"E:\study material\prep_platform\gradle_out.txt", "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n" + proc.stdout + "\n=== STDERR ===\n" + proc.stderr)

print("Saved output to gradle_out.txt, size:", len(proc.stdout) + len(proc.stderr))
