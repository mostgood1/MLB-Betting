@echo off
REM Auto-Tuning Scheduler for MLB Prediction Engine
REM This batch file starts the automated daily tuning system

echo.
echo ============================================
echo    MLB Prediction Engine Auto-Tuner
echo ============================================
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

REM Check if we're in the correct directory
if not exist "auto_tuning_scheduler.py" (
    echo ERROR: Cannot find auto_tuning_scheduler.py
    echo Please run this from the MLB-Betting directory
    pause
    exit /b 1
)

echo Starting auto-tuning scheduler...
echo - Daily optimization at 6:00 AM
echo - Performance checks at 12:00 PM and 11:00 PM
echo - Logs saved to: data\auto_tuning_scheduler.log
echo.
echo Press Ctrl+C to stop the scheduler
echo.

REM Check if virtual environment Python exists
if not exist "C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run this from the correct directory or check virtual environment setup
    pause
    exit /b 1
)

REM Start the Python scheduler with virtual environment
"C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" auto_tuning_scheduler.py

echo.
echo Auto-tuning scheduler stopped.
pause
