@echo off
echo ================================================================
echo === MLB Data Complete Integration Workflow                   ===
echo === 1. Run backfill to fix predictions                       ===
echo === 2. Fetch betting lines from OddsAPI                      ===
echo === 3. Validate data completeness                            ===
echo ================================================================
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
echo === Step 2: Running focused fixes ===
echo.

REM Run focused fix script to address specific issues
python focused_fix.py

echo.
echo === Step 2.5: Fetching Enhanced Game Data with Real Pitchers ===
echo.

REM Change to the enhanced data directory
cd "%~dp0mlb-clean-deploy"

REM Run our enhanced data fetcher for accurate pitcher information
echo Fetching enhanced game data with real starting pitchers...
python update_todays_data.py

REM Return to root directory
cd "%~dp0"

echo.
echo === Step 3: Fetching betting lines from OddsAPI ===
echo.

REM Check if api_keys.json exists
if exist "api_keys.json" (
    echo API keys file found.
) else if exist "mlb-clean-deploy\api_keys.json" (
    echo API keys file found in mlb-clean-deploy folder.
) else (
    echo WARNING: api_keys.json not found!
    echo.
    echo Please create an api_keys.json file with your OddsAPI key
    echo using the api_keys_template.json file as a reference.
    echo.
    echo Skipping betting lines fetch...
    goto SKIP_ODDS
)

REM Run the fetcher script with provided dates
if not "%end_date%"=="" (
    python fetch_odds_api.py %start_date% %end_date%
) else (
    python fetch_odds_api.py %start_date%
)

:SKIP_ODDS

echo.
echo === Step 4: Validating results ===
echo.

REM Run the validation script with provided dates
if not "%end_date%"=="" (
    python validate_backfill.py %start_date% %end_date%
) else (
    python validate_backfill.py %start_date%
)

REM Validate the enhanced pitcher data integration
cd "%~dp0mlb-clean-deploy"
echo Validating enhanced pitcher data integration...
python test_direct_integration.py
cd "%~dp0"

echo.
echo === Step 5: Generating detailed gap report ===
echo.

REM Run the gap finder to check for any remaining issues
if not "%end_date%"=="" (
    python find_data_gaps.py %start_date% %end_date%
) else (
    python find_data_gaps.py %start_date%
)

echo.
echo === Complete Workflow Finished ===
echo.
echo Check the following files for details:
echo - backfill.log: Backfill process logs
echo - odds_api_fetch.log: OddsAPI fetch logs
echo - backfill_validation_*.txt: Validation results
echo - detailed_gap_report_*.txt: Detailed gap analysis
echo - oddsapi_report_*.txt: OddsAPI fetch results

pause
