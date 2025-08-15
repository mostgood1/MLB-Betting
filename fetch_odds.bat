@echo off
echo === MLB Betting Lines Fetcher (OddsAPI) ===
echo This script will fetch betting lines for MLB games from OddsAPI
echo and update the historical_betting_lines_cache.json file

REM Default date is 2025-08-09 (since Aug 7-8 already have lines)
set start_date=2025-08-09
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
echo Checking for API key...

REM Check if api_keys.json exists
if exist "api_keys.json" (
    echo API keys file found.
) else if exist "mlb-clean-deploy\api_keys.json" (
    echo API keys file found in mlb-clean-deploy folder.
) else (
    echo ERROR: api_keys.json not found!
    echo.
    echo Please create an api_keys.json file with your OddsAPI key:
    echo {
    echo   "odds_api": "your_api_key_here"
    echo }
    echo.
    pause
    exit /b 1
)

echo.
echo Fetching betting lines...
echo.

REM Run the fetcher script with provided dates
if not "%end_date%"=="" (
    python fetch_odds_api.py %start_date% %end_date%
) else (
    python fetch_odds_api.py %start_date%
)

echo.
echo Process complete! Check odds_api_fetch.log for details

pause
