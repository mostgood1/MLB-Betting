@echo off
echo === MLB Data Gap Finder ===
echo This script will find specific games with missing predictions or betting lines

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
echo Finding data gaps...
echo.

REM Run the gap finder script with provided dates
if not "%end_date%"=="" (
    python find_data_gaps.py %start_date% %end_date%
) else (
    python find_data_gaps.py %start_date%
)

echo.
echo Process complete! Check data_gap_finder.log for details

pause
