@echo off
set "JAVA_HOME=E:\study material\prep_platform\jdk-17\jdk-17.0.13+11"
set "ANDROID_HOME=E:\study material\prep_platform\android-sdk"
set "STUDIO_JDK=E:\study material\prep_platform\jdk-17\jdk-17.0.13+11"
set "PATH=%JAVA_HOME%\bin;%ANDROID_HOME%\platform-tools;%PATH%"

echo Starting Android Studio for Pariksha Copilot...
start "" "E:\study material\prep_platform\android-studio\android-studio\bin\studio64.exe" "E:\study material\prep_platform\android-app"
