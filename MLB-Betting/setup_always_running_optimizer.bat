@echo off
REM Setup Windows Task Scheduler for Always-Running Auto-Tuning
REM Creates multiple scheduled tasks for continuous optimization

echo.
echo ========================================================
echo   Setting Up Always-Running Auto-Tuning (Task Scheduler)
echo ========================================================
echo.

echo Creating multiple scheduled tasks for continuous optimization...
echo.

REM Delete existing tasks if they exist
schtasks /delete /tn "MLB_DailyOptimization" /f >nul 2>&1
schtasks /delete /tn "MLB_QuickCheck_Morning" /f >nul 2>&1
schtasks /delete /tn "MLB_QuickCheck_Afternoon" /f >nul 2>&1
schtasks /delete /tn "MLB_QuickCheck_Evening" /f >nul 2>&1
schtasks /delete /tn "MLB_QuickCheck_Night" /f >nul 2>&1

set PYTHON_EXE="C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe"
set SCRIPT_PATH="C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting\auto_tuning_scheduler.py"

echo [1/5] Creating daily full optimization task (6:00 AM)...
schtasks /create /tn "MLB_DailyOptimization" ^
    /tr "%PYTHON_EXE% %SCRIPT_PATH% once" ^
    /sc daily ^
    /st 06:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

echo [2/5] Creating morning quick check (10:00 AM)...
schtasks /create /tn "MLB_QuickCheck_Morning" ^
    /tr "%PYTHON_EXE% %SCRIPT_PATH% check" ^
    /sc daily ^
    /st 10:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

echo [3/5] Creating afternoon quick check (2:00 PM)...
schtasks /create /tn "MLB_QuickCheck_Afternoon" ^
    /tr "%PYTHON_EXE% %SCRIPT_PATH% check" ^
    /sc daily ^
    /st 14:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

echo [4/5] Creating evening quick check (6:00 PM)...
schtasks /create /tn "MLB_QuickCheck_Evening" ^
    /tr "%PYTHON_EXE% %SCRIPT_PATH% check" ^
    /sc daily ^
    /st 18:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

echo [5/5] Creating night quick check (11:00 PM)...
schtasks /create /tn "MLB_QuickCheck_Night" ^
    /tr "%PYTHON_EXE% %SCRIPT_PATH% check" ^
    /sc daily ^
    /st 23:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

echo.
echo ✅ SUCCESS: Always-running auto-tuning configured!
echo.
echo Scheduled Tasks Created:
echo   - 06:00 AM: Daily full optimization
echo   - 10:00 AM: Quick performance check
echo   - 02:00 PM: Quick performance check  
echo   - 06:00 PM: Quick performance check
echo   - 11:00 PM: Quick performance check
echo.
echo Your system will now automatically optimize 5 times per day!
echo.
echo To view/manage tasks:
echo   - Press Win+R, type "taskschd.msc", press Enter
echo   - Look for tasks starting with "MLB_"
echo.
echo To manually trigger optimization:
echo   schtasks /run /tn "MLB_DailyOptimization"
echo.

echo Current MLB scheduled tasks:
schtasks /query /tn "MLB_*" 2>nul || echo   No MLB tasks found.
echo.
pause
