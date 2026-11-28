import subprocess
import os

env = os.environ.copy()
env["JAVA_HOME"] = r"C:\Program Files\Microsoft\jdk-17.0.21.102-hotspot"
env["ANDROID_HOME"] = r"E:\study material\prep_platform\android-sdk"
env["PATH"] = rf"{env['JAVA_HOME']}\bin;{env['ANDROID_HOME']}\platform-tools;{env['PATH']}"

print("Building assembleDebug...")
proc = subprocess.run(
    [r"E:\study material\prep_platform\android-app\gradlew.bat", "assembleDebug", "--stacktrace"],
    cwd=r"E:\study material\prep_platform\android-app",
    env=env,
    capture_output=True,
    text=True
)

print("EXIT CODE:", proc.returncode)
print("STDOUT:\n", proc.stdout[-2500:] if len(proc.stdout) > 2500 else proc.stdout)
if proc.returncode != 0:
    print("STDERR:\n", proc.stderr[-2500:] if len(proc.stderr) > 2500 else proc.stderr)
