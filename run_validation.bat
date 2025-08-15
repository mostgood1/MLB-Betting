@echo off
echo === MLB Backfill Validation ===
echo This script will check if the backfill process fixed data gaps

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
echo Running validation...
echo.

REM Run the validation script with provided dates
if not "%end_date%"=="" (
    python validate_backfill.py %start_date% %end_date%
) else (
    python validate_backfill.py %start_date%
)

echo.
echo Validation complete! Check backfill_validation.log for details

pause
