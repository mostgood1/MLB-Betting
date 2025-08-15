@echo off
REM Daily MLB Dashboard Update Automation
REM ===================================
REM This batch file updates the MLB dashboard statistics daily
REM Can be scheduled with Windows Task Scheduler

echo Starting daily MLB dashboard update...
echo Time: %date% %time%

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare"

REM Run the daily dashboard updater
python daily_dashboard_updater.py

if %errorlevel% == 0 (
    echo SUCCESS: Daily dashboard update completed successfully
) else (
    echo ERROR: Daily dashboard update failed with code %errorlevel%
)

echo Automation completed at %time%
pause
