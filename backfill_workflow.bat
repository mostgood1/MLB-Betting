@echo off
echo ===================================================
echo === MLB Data Backfill and Validation Workflow ===
echo ===================================================
echo This workflow will:
echo 1. Run the backfill process to fix data gaps
echo 2. Validate that all data gaps were fixed
echo.

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

echo Start Date: %start_date%
if not "%end_date%"=="" (
    echo End Date: %end_date%
) else (
    echo End Date: today
)

echo.
echo === Step 1: Running backfill process ===
echo.

REM Run the backfill script with provided dates
if not "%end_date%"=="" (
    python backfill_data.py %start_date% %end_date%
) else (
    python backfill_data.py %start_date%
)

echo.
echo === Step 2: Validating results ===
echo.

REM Run the validation script with provided dates
if not "%end_date%"=="" (
    python validate_backfill.py %start_date% %end_date%
) else (
    python validate_backfill.py %start_date%
)

echo.
echo === Workflow Complete ===
echo.
echo Check the following files for details:
echo - backfill.log: Detailed backfill logs
echo - backfill_validation.log: Detailed validation logs
echo - backfill_report_*.txt: Summary of backfill results
echo - backfill_validation_*.txt: Summary of validation results

pause
