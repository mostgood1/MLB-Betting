@echo off
echo Starting MLB Compare System (Fixed Version)...
cd "%~dp0\mlb-clean-deploy"
if exist "..\\.venv\Scripts\python.exe" (
  echo Using virtual environment python
  ..\\.venv\Scripts\python.exe complete_web_app_fixed.py
) else (
  echo Using system python
  python complete_web_app_fixed.py
)
