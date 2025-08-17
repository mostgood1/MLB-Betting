@echo off
REM Test the auto-tuning system once
REM This runs a single optimization cycle for testing

echo.
echo ==========================================
echo   Testing Auto-Tuning System (One Time)
echo ==========================================
echo.

cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

echo Testing auto-tuning system...
echo This will analyze recent performance and apply optimizations if appropriate.
echo.

REM Check if virtual environment Python exists
if not exist "C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please check virtual environment setup
    pause
    exit /b 1
)

"C:\Users\mostg\OneDrive\Coding\MLBCompare\.venv\Scripts\python.exe" auto_tuning_scheduler.py once

echo.
echo Test complete. Check the output above for results.
echo.
pause
