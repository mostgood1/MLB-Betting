@echo off
REM Check the status of the MLB Auto-Tuning system

echo.
echo =========================================
echo   MLB Auto-Tuning System Status
echo =========================================
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

echo [1] SCHEDULED TASK STATUS:
schtasks /query /tn "MLB_AutoTuning" 2>nul && (
    echo   ✓ Auto-tuning task is scheduled
    echo.
    echo   Task Details:
    schtasks /query /tn "MLB_AutoTuning" /fo LIST | findstr "Next Run Time:"
) || (
    echo   ✗ Auto-tuning task is NOT scheduled
    echo   Run 'setup_auto_tuning_schedule.bat' to set it up
)

echo.
echo [2] RECENT OPTIMIZATION STATUS:
C:/Users/mostg/OneDrive/Coding/MLBCompare/.venv/Scripts/python.exe -c "import json; import os; config = json.load(open('data/optimized_config.json')) if os.path.exists('data/optimized_config.json') else {}; print(f'   Config Version: {config.get(\"version\", \"unknown\")}'); print(f'   Last Updated: {config.get(\"last_updated\", \"unknown\")}'); print(f'   Base Lambda: {config.get(\"engine_parameters\", {}).get(\"base_lambda\", \"unknown\")}'); print(f'   Simulation Count: {config.get(\"simulation_parameters\", {}).get(\"default_sim_count\", \"unknown\")}'); print(f'   Auto-optimization: {\"ACTIVE\" if \"auto_optimized\" in config.get(\"version\", \"\") else \"NOT DETECTED\"}')"

echo.
echo [3] RECENT PERFORMANCE:
echo   (Performance check temporarily simplified for batch compatibility)
echo   Run 'test_auto_tuning.bat' for full performance analysis

echo.
echo [4] LOG FILES:
if exist "data\auto_tuning_scheduler.log" (
    echo   ✓ Auto-tuning log: data\auto_tuning_scheduler.log
    echo   Latest entries:
    powershell "Get-Content 'data\auto_tuning_scheduler.log' | Select-Object -Last 3"
) else (
    echo   ✗ No auto-tuning log found
)

echo.
echo =========================================
echo   To manually trigger optimization:
echo   - Run: test_auto_tuning.bat
echo.
echo   To start continuous monitoring:
echo   - Run: start_auto_tuning.bat
echo =========================================
echo.
pause
