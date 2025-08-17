@echo off
echo.
echo =================================
echo   Testing Auto-Tuning (Simple)
echo =================================
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

echo Running auto-optimization test...
"C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" auto_tuning_scheduler.py once

echo.
echo Test complete!
pause
