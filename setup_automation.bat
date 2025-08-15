@echo off
echo.
echo MLB Daily Automation - Scheduler Setup
echo ======================================
echo.
echo This will set up your MLB prediction system to run automatically
echo every morning at 6:00 AM (you can change this later if needed)
echo.
pause

echo Setting up Windows Task Scheduler...
PowerShell -ExecutionPolicy Bypass -File "%~dp0setup_daily_scheduler.ps1"

echo.
echo Setup complete! 
echo Your MLB system will now automatically:
echo   1. Fetch today's games from MLB API
echo   2. Update pitcher stats and team data  
echo   3. Get latest betting lines
echo   4. Update the frontend with fresh data
echo.
echo This happens every morning so your system is always ready!
pause
