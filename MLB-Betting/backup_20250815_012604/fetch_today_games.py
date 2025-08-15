#!/usr/bin/env python3
"""
MLB Games Fetcher for Current Day

This script fetches today's MLB games from the MLB Stats API
and adds them to the game_scores_cache.json file.
"""

import json
import os
import sys
import logging
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_today_games.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TodayGamesFetcher')

class MLBGamesFetcher:
    def __init__(self):
        """Initialize the MLB Games Fetcher"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        
        # MLB Stats API endpoints
        self.mlb_api_url = "https://statsapi.mlb.com/api/v1/schedule"
        
        # Track stats
        self.stats = {
            'games_found': 0,
            'games_added': 0,
            'api_calls': 0,
            'errors': 0
        }
    
    def load_json_file(self, filepath: str) -> dict:
        """Load a JSON file with error handling"""
        if not os.path.exists(filepath):
            logger.warning(f"File not found - {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            self.stats['errors'] += 1
            return {}
    
    def save_json_file(self, filepath: str, data: dict) -> bool:
        """Save data to a JSON file with error handling"""
        try:
            # Create a backup first
            if os.path.exists(filepath):
                backup_path = f"{filepath}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(filepath, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                logger.info(f"Created backup at {backup_path}")
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {filepath}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def fetch_todays_games(self) -> List[Dict]:
        """Fetch today's MLB games from the MLB Stats API"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Prepare parameters
        params = {
            'sportId': 1,  # MLB
            'date': today,
            'hydrate': 'team,linescore,probablePitcher'
        }
        
        try:
            logger.info(f"Fetching games for {today}")
            response = requests.get(self.mlb_api_url, params=params)
            self.stats['api_calls'] += 1
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return []
            
            # Get games data
            response_data = response.json()
            dates = response_data.get('dates', [])
            
            if not dates:
                logger.warning(f"No games scheduled for {today}")
                return []
            
            games_data = []
            for date in dates:
                games = date.get('games', [])
                games_data.extend(games)
            
            self.stats['games_found'] = len(games_data)
            logger.info(f"Found {len(games_data)} games for {today}")
            
            # Convert to our format
            formatted_games = []
            for game in games_data:
                game_id = game.get('gamePk')
                
                # Get teams
                away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', '')
                home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', '')
                
                # Get game time
                game_datetime = game.get('gameDate', '')
                
                # Get pitchers
                away_pitcher = "TBD"
                home_pitcher = "TBD"
                
                away_pitcher_data = game.get('teams', {}).get('away', {}).get('probablePitcher', {})
                if away_pitcher_data:
                    away_pitcher = away_pitcher_data.get('fullName', 'TBD')
                
                home_pitcher_data = game.get('teams', {}).get('home', {}).get('probablePitcher', {})
                if home_pitcher_data:
                    home_pitcher = home_pitcher_data.get('fullName', 'TBD')
                
                # Create formatted game
                formatted_game = {
                    'game_pk': game_id,
                    'away_team': away_team,
                    'home_team': home_team,
                    'away_pitcher': away_pitcher,
                    'home_pitcher': home_pitcher,
                    'status': game.get('status', {}).get('detailedState', ''),
                    'game_time': game_datetime,
                    'game_date': game_datetime
                }
                
                formatted_games.append(formatted_game)
            
            return formatted_games
            
        except Exception as e:
            logger.error(f"Error fetching games: {str(e)}")
            self.stats['errors'] += 1
            return []
    
    def update_game_scores(self, games: List[Dict]) -> int:
        """Update game_scores_cache.json with today's games"""
        if not games:
            logger.warning("No games to update")
            return 0
        
        # Load current game scores
        game_scores = self.load_json_file(self.game_scores_path)
        
        # Ensure game_scores is a dictionary (fix for legacy data)
        if not isinstance(game_scores, dict):
            logger.warning(f"Game scores data is {type(game_scores)}, converting to dict")
            game_scores = {}
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if today already exists
        if today in game_scores:
            logger.info(f"Updating existing entry for {today}")
            # Handle both list and dict formats
            if isinstance(game_scores[today], list):
                # Convert list format to dict format
                game_scores[today] = {
                    'games': games,
                    'last_update': datetime.now().isoformat()
                }
            else:
                # Already dict format, update normally
                game_scores[today]['games'] = games
                game_scores[today]['last_update'] = datetime.now().isoformat()
        else:
            logger.info(f"Creating new entry for {today}")
            game_scores[today] = {
                'games': games,
                'last_update': datetime.now().isoformat()
            }
        
        # Save updated game scores
        if self.save_json_file(self.game_scores_path, game_scores):
            self.stats['games_added'] = len(games)
            logger.info(f"Added/updated {len(games)} games for {today}")
        
        return len(games)
    
    def fetch_and_update(self) -> Dict:
        """Fetch today's games and update the game_scores_cache.json file"""
        # Fetch games
        games = self.fetch_todays_games()
        
        # Update game scores
        self.update_game_scores(games)
        
        return self.stats

def main():
    """Main function to fetch today's MLB games"""
    print(f"=== MLB Today's Games Fetcher ===")
    print(f"Fetching today's MLB games and updating game_scores_cache.json")
    
    fetcher = MLBGamesFetcher()
    stats = fetcher.fetch_and_update()
    
    print("\n=== Fetch Complete ===")
    print(f"Games found: {stats['games_found']}")
    print(f"Games added/updated: {stats['games_added']}")
    print(f"API calls made: {stats['api_calls']}")
    print(f"Errors: {stats['errors']}")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
