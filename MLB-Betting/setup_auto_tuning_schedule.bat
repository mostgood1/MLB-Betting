@echo off
REM Create Windows Task Scheduler job for MLB Auto-Tuning
REM This will run the auto-tuning system daily at 6:00 AM

echo.
echo ===============================================
echo   Setting up MLB Auto-Tuning Windows Service
echo ===============================================
echo.

echo Creating scheduled task for daily auto-tuning...
echo.

REM Delete existing task if it exists
schtasks /delete /tn "MLB_AutoTuning" /f >nul 2>&1

REM Create new scheduled task
schtasks /create /tn "MLB_AutoTuning" ^
    /tr "\"C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe\" \"C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting\auto_tuning_scheduler.py\" once" ^
    /sc daily ^
    /st 06:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Auto-tuning scheduled successfully!
    echo.
    echo Task Details:
    echo   - Task Name: MLB_AutoTuning
    echo   - Schedule: Daily at 6:00 AM
    echo   - Action: Run auto-tuning optimization
    echo   - User: %USERNAME%
    echo.
    echo You can manage this task in Windows Task Scheduler:
    echo   - Press Win+R, type "taskschd.msc", press Enter
    echo   - Look for "MLB_AutoTuning" in the Task Scheduler Library
    echo.
    echo To test the task manually, run:
    echo   schtasks /run /tn "MLB_AutoTuning"
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo Please run this script as Administrator.
    echo.
)

echo.
echo Current scheduled tasks related to MLB:
schtasks /query /tn "MLB_*" 2>nul || echo   No MLB tasks found.
echo.
pause
