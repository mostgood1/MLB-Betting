@echo off
echo === MLB Data Backfill Script ===
echo This script will fill in missing predictions and link betting lines to game IDs

REM Default date is 2025-08-07
set start_date=2025-08-07
set end_date=

REM Check if a custom start date was provided
if not "%1"=="" (
    set start_date=%1
)

REM Check if end date was provided
if not "%2"=="" (
    set end_date=%2
)

echo.
echo Start Date: %start_date%
if not "%end_date%"=="" (
    echo End Date: %end_date%
) else (
    echo End Date: today
)

echo.
echo Running backfill process...
echo.

REM Run the backfill script with provided dates
if not "%end_date%"=="" (
    python backfill_data.py %start_date% %end_date%
) else (
    python backfill_data.py %start_date%
)

echo.
echo Process complete! Check backfill.log for details

pause
