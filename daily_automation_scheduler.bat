@echo off
REM ================================================================
REM MLB Enhanced Daily Automation - Scheduler Friendly
REM Run this script daily to ensure accurate pitcher data
REM ================================================================

REM Change to the script directory
cd /d "%~dp0"

REM Log the start time
echo [%DATE% %TIME%] Starting MLB Enhanced Daily Automation >> daily_automation_scheduler.log

REM Run the enhanced daily automation (no pause for scheduler)
python daily_enhanced_automation.py >> daily_automation_scheduler.log 2>&1

REM Log completion
if %ERRORLEVEL% EQU 0 (
    echo [%DATE% %TIME%] Daily automation completed successfully >> daily_automation_scheduler.log
) else (
    echo [%DATE% %TIME%] Daily automation failed with error level %ERRORLEVEL% >> daily_automation_scheduler.log
)

REM Exit with the same error level for scheduler monitoring
exit /b %ERRORLEVEL%
