@echo off
REM Enhanced Daily MLB Automation - Complete Workflow
REM This batch file runs the complete enhanced daily automation

echo ================================================
echo    Enhanced Daily MLB Automation System
echo ================================================
echo Starting comprehensive daily data refresh...
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare"

echo [1/1] Running Enhanced Daily Automation...
python daily_enhanced_automation_clean.py

echo.
echo ================================================
echo           Daily Automation Complete
echo ================================================
echo.
echo Check the logs for details:
echo - daily_enhanced_automation_[date].log
echo.
echo Press any key to exit...
pause >nul
