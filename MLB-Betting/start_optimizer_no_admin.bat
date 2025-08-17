@echo off
REM Admin-Free Auto-Tuning Setup
REM Creates a desktop shortcut for always-running optimization

echo.
echo =============================================
echo   Admin-Free Always-Running Auto-Tuning
echo =============================================
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

echo OPTION 1: Start Continuous Background Process
echo -------------------------------------------
echo This runs continuously in the background without admin privileges.
echo.
echo Starting in 5 seconds... (Ctrl+C to cancel)
timeout /t 5 /nobreak >nul

echo.
echo Starting continuous auto-tuning...
echo - Will run daily optimization at 6:00 AM
echo - Quick checks every 4 hours
echo - Logs saved to: data\continuous_auto_tuning.log
echo.
echo KEEP THIS WINDOW OPEN for always-running optimization
echo Press Ctrl+C to stop
echo.

"C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" continuous_auto_tuning.py
