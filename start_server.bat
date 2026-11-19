@echo off
title IT Officer Prep Platform Web Server
cd /d "%~dp0"
echo ================================================================
echo   Launching IT Officer Exam Prep Server (FastAPI + SQLite)
echo   Targeting: SEBI Grade A, SBI SCO, IBPS SO
echo ================================================================
echo.
python run_server.py
pause
