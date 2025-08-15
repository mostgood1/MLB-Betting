@echo off
echo === MLB Today's Games Fetcher ===
echo This script will fetch today's MLB games and update game_scores_cache.json

echo.
echo Fetching games...
echo.

REM Run the fetcher script
python fetch_today_games.py

echo.
echo Process complete! Check fetch_today_games.log for details

pause
