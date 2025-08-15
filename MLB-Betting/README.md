# MLB Betting Prediction System

A comprehensive MLB betting prediction system with real-time data integration and enhanced pitcher analysis.

## Known Issues / TODO

- **Post-game Analysis**: Temporarily disabled during cleanup process. Historical analysis functionality for completed games will be restored in a future update.

## Directory Structure

```
MLB-Betting/
├── app.py                                    # Main Flask application
├── comprehensive_tuned_engine.py            # Core prediction engine
├── enhanced_master_predictions_service.py   # Master prediction service
├── enhanced_mlb_fetcher.py                  # Enhanced MLB data fetcher
├── integrated_closing_lines.py              # Betting lines integration
├── live_mlb_data.py                         # Live MLB data fetching
├── team_assets.json                         # Team information and assets
├── team_assets_utils.py                     # Team assets utilities
├── team_name_normalizer.py                  # Team name normalization
├── data/                                    # Data files
│   ├── master_predictions.json             # Cached predictions
│   ├── master_betting_lines.json           # Betting lines data
│   ├── todays_complete_games.json          # Today's enhanced game data
│   └── ...                                 # Other data files
├── templates/                               # HTML templates
│   ├── index.html                          # Main dashboard
│   └── historical.html                     # Historical analysis
├── engines/                                # Prediction engines
│   └── ultra_fast_engine.py               # Fast prediction engine
└── utils/                                  # Utility modules
    ├── automated_closing_lines_fetcher.py  # Automated betting lines
    ├── comprehensive_closing_lines.py      # Closing lines management
    └── ...                                 # Other utilities
```

## Key Features

- **Real-time MLB Data**: Live game data with enhanced pitcher information
- **Betting Lines Integration**: Real-time odds and closing lines
- **Comprehensive Predictions**: Win probabilities, total runs, and betting recommendations
- **Self-contained**: No external dependencies outside this directory
- **Enhanced Pitcher Data**: Real pitcher names instead of "TBD"
- **Live Dashboard**: Web interface for real-time betting analysis

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open browser to `http://localhost:5000`

3. View today's games with predictions and betting recommendations

## API Endpoints

- `/api/today-games` - Get today's games with enhanced data
- `/api/prediction/<away_team>/<home_team>` - Get prediction for specific game
- `/api/live-status` - Get live system status
- `/` - Main dashboard interface

## Data Sources

- **MLB API**: Official game data and pitcher information
- **OddsAPI**: Real-time betting lines and odds
- **Enhanced Data**: Processed and enriched game information
