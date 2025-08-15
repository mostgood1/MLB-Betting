@echo off
REM ================================================================
REM MLB NEW DAY AUTOMATION - Complete Daily Prep System
REM ================================================================
REM This script runs the complete daily automation to prepare the
REM MLB prediction system for each new day with fresh data and
REM 5000-simulation locked predictions.
REM
REM Recommended to run this script daily at 6:00 AM before betting
REM lines are finalized.
REM ================================================================

echo.
echo ================================================================
echo           MLB NEW DAY AUTOMATION SYSTEM
echo ================================================================
echo.
echo This comprehensive automation will:
echo   1. 🏗️  Pull fresh games from MLB API
echo   2. ⚾  Fetch projected starters from MLB API
echo   3. 📊  Update pitcher stats and team strengths  
echo   4. 💰  Update betting lines from OddsAPI
echo   5. 🎰  Run 5000 simulations for each game
echo   6. 🔒  Hard-code locked-in predictions
echo   7. 🎯  Generate betting recommendations
echo   8. 🖥️  Update frontend with today's games
echo.
echo Estimated time: 3-5 minutes
echo.

REM Change to the MLB project directory
cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not available or not in PATH
    echo Please ensure Python is installed and accessible
    pause
    exit /b 1
)

echo 🚀 Starting New Day Automation...
echo.

REM Run the daily new day automation script
python daily_new_day_automation.py

REM Check if the automation was successful
if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo ✅ NEW DAY AUTOMATION COMPLETED SUCCESSFULLY!
    echo ================================================================
    echo.
    echo Your MLB prediction system is now ready with:
    echo   ✅ Fresh game data from MLB API
    echo   ✅ Updated pitcher stats and team strengths
    echo   ✅ Latest betting lines from OddsAPI
    echo   ✅ 5000-simulation locked predictions
    echo   ✅ Enhanced betting recommendations
    echo   ✅ Frontend updated with today's games
    echo.
    echo 🎯 System ready for optimal betting performance!
    echo 🚀 All predictions locked in with 5000-simulation confidence
    echo.
) else (
    echo.
    echo ================================================================
    echo ⚠️ NEW DAY AUTOMATION ENCOUNTERED ISSUES
    echo ================================================================
    echo.
    echo Some steps may have failed. Check the log file:
    echo   daily_new_day_automation.log
    echo.
    echo The system may still be partially functional.
    echo.
)

echo 📄 Check detailed log: daily_new_day_automation.log
echo 🔧 For manual runs: python daily_new_day_automation.py
echo.
pause
