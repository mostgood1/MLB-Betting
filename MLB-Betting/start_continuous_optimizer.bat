@echo off
REM Start Continuous MLB Auto-Tuning (Always Running)
REM This keeps the optimizer running in the background

echo.
echo ===============================================
echo   MLB Continuous Auto-Tuning (Always Running)
echo ===============================================
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

echo Starting continuous auto-tuning...
echo.
echo This will run optimization:
echo   - Daily full optimization at 6:00 AM
echo   - Quick performance checks every 4 hours
echo   - End-of-day check at 11:30 PM
echo.
echo Logs: data\continuous_auto_tuning.log
echo.
echo Press Ctrl+C to stop
echo.

"C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" continuous_auto_tuning.py

echo.
echo Continuous auto-tuning stopped.
pause
