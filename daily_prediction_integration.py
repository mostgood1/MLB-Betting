#!/usr/bin/env python3
"""
Daily Prediction Integration Hook
==============================
Automatically integrates new daily predictions into the unified cache
while preserving our archaeological discoveries.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def integrate_daily_predictions(date_str=None):
    """Integrate daily predictions into unified cache"""
    
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Integrating predictions for {date_str}")
    
    root_dir = Path(__file__).parent
    betting_dir = root_dir / 'MLB-Betting'
    
    # Load unified cache
    unified_cache_path = root_dir / 'unified_predictions_cache.json'
    
    if unified_cache_path.exists():
        with open(unified_cache_path, 'r') as f:
            unified_data = json.load(f)
    else:
        unified_data = {}
    
    # Check for new predictions from various sources
    sources_to_check = [
        betting_dir / 'data' / 'daily_predictions_cache.json',
        betting_dir / 'data' / 'master_predictions.json',
        root_dir / 'game_scores_cache.json'
    ]
    
    new_predictions = []
    
    # Check daily predictions cache
    daily_cache_path = betting_dir / 'data' / 'daily_predictions_cache.json'
    if daily_cache_path.exists():
        with open(daily_cache_path, 'r') as f:
            daily_data = json.load(f)
        
        if date_str in daily_data:
            daily_games = daily_data[date_str].get('games', [])
            for game in daily_games:
                if game.get('predicted_away_score') is not None:
                    game['prediction_source'] = 'daily_predictions'
                    game['integration_timestamp'] = datetime.now().isoformat()
                    new_predictions.append(game)
    
    # Integrate new predictions while preserving premium data
    if new_predictions:
        if date_str not in unified_data:
            unified_data[date_str] = {'games': []}
        
        # Check for existing games (don't overwrite premium data)
        existing_games = unified_data[date_str]['games']
        
        for new_game in new_predictions:
            # Check if this game already exists
            found_existing = False
            for existing in existing_games:
                if (existing.get('away_team') == new_game.get('away_team') and 
                    existing.get('home_team') == new_game.get('home_team')):
                    
                    # Only update if existing is not premium quality
                    if existing.get('quality_level') != 'premium':
                        existing.update(new_game)
                        print(f"  Updated: {new_game.get('away_team')} @ {new_game.get('home_team')}")
                    else:
                        print(f"  Preserved premium: {existing.get('away_team')} @ {existing.get('home_team')}")
                    found_existing = True
                    break
            
            if not found_existing:
                unified_data[date_str]['games'].append(new_game)
                print(f"  Added: {new_game.get('away_team')} @ {new_game.get('home_team')}")
        
        # Save updated unified cache
        with open(unified_cache_path, 'w') as f:
            json.dump(unified_data, f, indent=2)
        
        # Sync to betting app
        betting_unified_path = betting_dir / 'unified_predictions_cache.json'
        with open(betting_unified_path, 'w') as f:
            json.dump(unified_data, f, indent=2)
        
        print(f"Integrated {len(new_predictions)} new predictions for {date_str}")
    
    return len(new_predictions)

def create_prediction_monitoring():
    """Monitor for new prediction files and integrate automatically"""
    
    root_dir = Path(__file__).parent
    betting_dir = root_dir / 'MLB-Betting'
    
    # Check if there are any new prediction files to process
    prediction_sources = [
        betting_dir / 'data' / 'master_predictions.json',
        betting_dir / 'data' / 'daily_predictions_cache.json'
    ]
    
    for source in prediction_sources:
        if source.exists():
            stat = source.stat()
            # If modified in last hour, process it
            if (datetime.now().timestamp() - stat.st_mtime) < 3600:
                print(f"New predictions detected in {source.name}")
                # Process this source
                today = datetime.now().strftime('%Y-%m-%d')
                integrate_daily_predictions(today)

if __name__ == "__main__":
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    integrated_count = integrate_daily_predictions(today)
    
    if integrated_count > 0:
        print(f"Successfully integrated {integrated_count} predictions!")
    else:
        print("No new predictions to integrate")
    
    # Also check for monitoring
    create_prediction_monitoring()
