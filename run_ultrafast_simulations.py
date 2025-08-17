#!/usr/bin/env python3
"""
Standalone script to run Ultra-Fast Simulations for a given date.
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add MLB-Betting directory to path to import engine
mlb_betting_path = Path(__file__).parent / 'MLB-Betting'
sys.path.append(str(mlb_betting_path))

try:
    from engines.ultra_fast_engine import FastPredictionEngine
except ImportError:
    # Alternative path if the above doesn't work
    sys.path.append(str(Path(__file__).parent / 'MLB-Betting' / 'engines'))
    from ultra_fast_engine import FastPredictionEngine

def run_simulations_for_date(date_str):
    """
    Runs simulations for all games on a given date and updates the unified cache.
    """
    print(f"Running Ultra-Fast Simulations for {date_str}")
    
    # Initialize the engine
    engine = FastPredictionEngine()
    
    # Define paths
    root_dir = Path(__file__).parent
    games_cache_path = root_dir / 'game_scores_cache.json'
    unified_cache_path = root_dir / 'unified_predictions_cache.json'
    
    # Load games for the specified date
    if not games_cache_path.exists():
        print(f"ERROR: Games cache not found at {games_cache_path}")
        return

    with open(games_cache_path, 'r') as f:
        games_cache = json.load(f)
    
    # Check if date exists in cache (cache is organized by date)
    if date_str not in games_cache:
        print(f"No games found for {date_str} in cache.")
        print(f"Available dates: {list(games_cache.keys())}")
        return
        
    games_today = games_cache[date_str].get('games', [])
    
    if not games_today:
        print(f"No games found for {date_str} in cache.")
        return
        
    print(f"Found {len(games_today)} games to simulate.")

    # Load or initialize unified cache
    if unified_cache_path.exists():
        with open(unified_cache_path, 'r') as f:
            unified_cache = json.load(f)
    else:
        unified_cache = {"predictions_by_date": {}}

    if date_str not in unified_cache["predictions_by_date"]:
        unified_cache["predictions_by_date"][date_str] = {"games": {}}

    # Run simulation for each game
    for game in games_today:
        away_team = game['away_team']
        home_team = game['home_team']
        game_key = f"{away_team} @ {home_team}"
        
        print(f"  - Simulating: {game_key}")
        
        prediction = engine.get_fast_prediction(
            away_team=away_team, 
            home_team=home_team, 
            game_date=date_str,
            away_pitcher=game.get('away_pitcher'),
            home_pitcher=game.get('home_pitcher')
        )
        
        # Add prediction to the cache for the correct date
        unified_cache["predictions_by_date"][date_str]["games"][game_key] = prediction

    # Save the updated cache
    with open(unified_cache_path, 'w') as f:
        json.dump(unified_cache, f, indent=4)
        
    print(f"Successfully ran simulations and updated unified cache for {len(games_today)} games.")

if __name__ == "__main__":
    # Default to today if no date is provided
    target_date = datetime.now().strftime('%Y-%m-%d')
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        
    run_simulations_for_date(target_date)
