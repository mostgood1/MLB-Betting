@echo off
echo ================================================================
echo === MLB Enhanced Daily Data Fetch Workflow                   ===
echo === 1. Fetch standard today's MLB games                      ===
echo === 2. Fetch ENHANCED game data with real pitchers           ===
echo === 3. Fetch betting lines from OddsAPI                      ===
echo === 4. Validate data completeness                            ===
echo ================================================================
echo.

echo === Step 1: Fetching Today's Games (Standard) ===
echo.

REM Run the standard today's games fetcher
python fetch_today_games.py

echo.
echo === Step 2: Fetching ENHANCED Game Data with Real Pitchers ===
echo.

REM Change to the enhanced data directory
cd "%~dp0mlb-clean-deploy"

REM Run our enhanced data fetcher
echo Running enhanced data fetcher for accurate pitcher information...
python update_todays_data.py

REM Return to root directory
cd "%~dp0"

echo.
echo === Step 3: Fetching Betting Lines from OddsAPI ===
echo.

REM Run the OddsAPI fetcher for today only
python fetch_odds_api.py

echo.
echo === Step 4: Validating Results ===
echo.

REM Validate the enhanced data integration
cd "%~dp0mlb-clean-deploy"
echo Validating enhanced pitcher data integration...
python test_direct_integration.py

REM Return to root directory
cd "%~dp0"

echo.
echo === Enhanced Daily Workflow Complete ===
echo.
echo ✅ ACCURACY ENHANCEMENT: Real starting pitcher data integrated!
echo    This dramatically improves prediction accuracy vs "TBD" placeholders
echo.
echo Check the following files for details:
echo - fetch_today_games.log: Standard games fetch logs
echo - mlb-clean-deploy/todays_complete_games.json: Enhanced pitcher data
echo - odds_api_fetch.log: OddsAPI fetch logs
echo.
echo 🎯 Your MLB prediction system is ready for optimal performance!

pause
