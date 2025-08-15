@echo off
echo ===================================================
echo        MLB API Data Integration System
echo ===================================================
echo.
echo This script will:
echo 1. Fetch data from MLB API as the source of truth
echo 2. Remove duplicate game entries
echo 3. Synchronize game IDs across all system files
echo 4. Update pitcher information everywhere
echo 5. Ensure data consistency
echo.

REM Get current date in YYYY-MM-DD format
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set mm=%%a
    set dd=%%b
    set yyyy=%%c
)
if %mm% LSS 10 set mm=0%mm%
if %dd% LSS 10 set dd=0%dd%
set TODAY=%yyyy%-%mm%-%dd%

REM Default to processing data from Aug 7, 2025 to today
set START_DATE=2025-08-07
set END_DATE=%TODAY%

REM Parse command-line arguments for custom date range
if not "%~1"=="" (
    set START_DATE=%~1
)
if not "%~2"=="" (
    set END_DATE=%~2
)

echo Processing dates from %START_DATE% to %END_DATE%
echo.
echo Step 1: Fetching data from MLB API...
cd /d %~dp0
python mlb_api_integration.py %START_DATE% %END_DATE%
if errorlevel 1 (
    echo ERROR: MLB API integration failed!
    goto :error
)

echo.
echo Step 2: Removing duplicate entries...
python deduplicate_date_range.py %START_DATE% %END_DATE%
if errorlevel 1 (
    echo ERROR: Deduplication failed!
    goto :error
)

echo.
echo Step 3: Synchronizing data across all files...
python synchronize_mlb_data.py %START_DATE% %END_DATE%
if errorlevel 1 (
    echo ERROR: Data synchronization failed!
    goto :error
)

echo.
echo ===================================================
echo         Integration completed successfully!
echo ===================================================
echo.
echo All MLB data has been integrated with the MLB API as
echo the source of truth. Game IDs and pitcher information
echo are now consistent across all system files.
echo.
echo Please check the log files and sync report for details.
echo.
goto :end

:error
echo.
echo ===================================================
echo              ERROR: Process failed!
echo ===================================================
echo.
echo Please check the log files for details.
echo.

:end
pause
