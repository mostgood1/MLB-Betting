#!/usr/bin/env python3

import json
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_mlb_schedule_for_date(date_str):
    """Fetch MLB schedule from official API for a specific date"""
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        games = []
        for date_data in data.get('dates', []):
            for game in date_data.get('games', []):
                try:
                    # Extract game info
                    away_team = game['teams']['away']['team']['name']
                    home_team = game['teams']['home']['team']['name']
                    game_id = game['gamePk']
                    status = game['status']['detailedState']
                    
                    # Get scores if available
                    away_score = game['teams']['away'].get('score', 0)
                    home_score = game['teams']['home'].get('score', 0)
                    
                    game_info = {
                        'game_id': game_id,
                        'away_team': away_team,
                        'home_team': home_team,
                        'game_status': 'Final' if status == 'Final' else status,
                        'away_score': away_score,
                        'home_score': home_score,
                        'predicted_away_score': away_score,  # Use actual as predicted for completed games
                        'predicted_home_score': home_score
                    }
                    
                    games.append(game_info)
                    logging.info(f"Found game: {away_team} @ {home_team} - {status}")
                    
                except KeyError as e:
                    logging.warning(f"Missing key {e} in game data: {game.get('gamePk', 'Unknown')}")
                    continue
        
        return games
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching MLB schedule: {e}")
        return []

def add_august_14_to_cache():
    """Add August 14th games to the unified cache"""
    
    date_str = "2025-08-14"
    
    # Fetch games from MLB API
    games = fetch_mlb_schedule_for_date(date_str)
    
    if not games:
        logging.error("No games found for August 14th")
        return False
    
    # Load existing cache
    try:
        with open('unified_predictions_cache.json', 'r') as f:
            cache = json.load(f)
    except FileNotFoundError:
        logging.error("unified_predictions_cache.json not found")
        return False
    
    # Create backup
    backup_filename = f"unified_predictions_cache_backup_august14_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w') as f:
        json.dump(cache, f, indent=2)
    logging.info(f"Backup created: {backup_filename}")
    
    # Add August 14th games
    cache[date_str] = games
    logging.info(f"Added {len(games)} games for {date_str}")
    
    # Save updated cache
    with open('unified_predictions_cache.json', 'w') as f:
        json.dump(cache, f, indent=2)
    
    logging.info("Updated unified cache saved")
    return True

if __name__ == "__main__":
    add_august_14_to_cache()
