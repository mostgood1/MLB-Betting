@echo off
echo ======================================
echo MLB Team Comparator - Revamped System
echo ======================================
echo.

REM Set the working directory to where the script is located
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and try again
    pause
    exit /b 1
)

echo Step 1: Activating Python virtual environment...
call .venv\Scripts\activate.bat 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Virtual environment not found, attempting to continue without it...
)

echo Step 2: Normalizing MLB data...
python mlb-clean-deploy\normalize_data.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Data normalization failed
    pause
    exit /b 1
)

echo Step 3: Generating data validation report...
python mlb-clean-deploy\generate_data_report.py
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Data validation report generation failed
    echo Continuing with the web app launch anyway...
)

echo Step 4: Starting the web application...
echo.
echo The web application will start on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python mlb-clean-deploy\complete_web_app_revamped.py

pause
