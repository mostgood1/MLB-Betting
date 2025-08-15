@echo off
REM Daily MLB Prediction Integration Scheduler
REM Runs daily at 9 AM and 9 PM to catch new predictions

echo Running daily prediction integration...
cd /d "C:\Users\mostg\OneDrive\Coding\MLBCompare"
python daily_prediction_integration.py

REM Also run data consolidation
python data_preservation\daily_consolidation.py

echo Integration complete!
pause
