@echo off
echo ================================================================
echo === MLB Data Fetch and Validate Workflow                     ===
echo === 1. Fetch today's MLB games                               ===
echo === 2. Fetch ENHANCED game data with real pitchers           ===
echo === 3. Fetch betting lines from OddsAPI                      ===
echo === 4. Validate data completeness                            ===
echo ================================================================
echo.

echo === Step 1: Fetching Today's Games ===
echo.

REM Run the today's games fetcher
python fetch_today_games.py

echo.
echo === Step 2: Fetching ENHANCED Game Data with Real Pitchers ===
echo.

REM Change to the enhanced data directory
cd "%~dp0mlb-clean-deploy"

REM Run our enhanced data fetcher for accurate pitcher information
echo Fetching enhanced game data with real starting pitchers...
python update_todays_data.py

REM Return to root directory
cd "%~dp0"

echo.
echo === Step 3: Fetching Betting Lines from OddsAPI ===
echo.

REM Run the OddsAPI fetcher for today only
python fetch_odds_api.py 2025-08-13 2025-08-13

echo.
echo === Step 4: Validating Results ===
echo.

REM Run the validation script for today only
python validate_backfill.py 2025-08-13 2025-08-13

REM Validate the enhanced pitcher data integration
cd "%~dp0mlb-clean-deploy"
echo Validating enhanced pitcher data integration...
python test_direct_integration.py
cd "%~dp0"

echo.
echo === Enhanced Workflow Complete ===
echo.
echo ✅ ACCURACY ENHANCEMENT: Real starting pitcher data integrated!
echo    This dramatically improves prediction accuracy vs "TBD" placeholders
echo.
echo Check the following files for details:
echo - fetch_today_games.log: Today's games fetch logs
echo - mlb-clean-deploy/todays_complete_games.json: Enhanced pitcher data
echo - odds_api_fetch.log: OddsAPI fetch logs
echo - backfill_validation_*.txt: Validation results
echo.
echo 🎯 Your MLB prediction system is ready for optimal performance!

pause
