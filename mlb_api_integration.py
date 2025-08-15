#!/usr/bin/env python3
"""
MLB API Data Integration Script

This script fetches data from the MLB API for a date range and ensures:
1. All games have official MLB Game IDs
2. All games have starting pitcher information
3. Data consistency across all system files
"""

import json
import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mlb_api_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MLBApiIntegration')

class MLBApiIntegration:
    def __init__(self):
        """Initialize the MLB API Integration tool"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        
        # Try to find normalized_game_data.json
        self.normalized_game_path = os.path.join(self.root_dir, 'utils', 'normalized_game_data.json')
        if not os.path.exists(self.normalized_game_path):
            self.normalized_game_path = os.path.join(self.root_dir, 'mlb-clean-deploy', 'utils', 'normalized_game_data.json')
            if not os.path.exists(self.normalized_game_path):
                # Create the directory if needed
                os.makedirs(os.path.dirname(self.normalized_game_path), exist_ok=True)
        
        self.api_keys_path = os.path.join(self.root_dir, 'mlb-clean-deploy', 'api_keys.json')
        
        # MLB API settings
        self.mlb_api_base = "https://statsapi.mlb.com/api/v1"
        self.api_key = self._load_api_key()
        
        # Track stats
        self.stats = {
            'dates_processed': 0,
            'games_fetched': 0,
            'games_updated': 0,
            'pitchers_updated': 0,
            'errors': 0
        }
        
        # Current date
        self.today = datetime.now().strftime('%Y-%m-%d')
    
    def _load_api_key(self) -> str:
        """Load MLB API key if available"""
        if os.path.exists(self.api_keys_path):
            try:
                with open(self.api_keys_path, 'r') as f:
                    keys = json.load(f)
                    return keys.get('mlb_api', '')
            except Exception as e:
                logger.error(f"Error loading API key: {str(e)}")
        return ''
    
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
            os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Create parent directory if it doesn't exist
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {filepath}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def get_date_range(self, start_date: str, end_date: str) -> List[str]:
        """Generate a list of dates between start_date and end_date (inclusive)"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_list = []
        current = start
        
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return date_list
    
    def fetch_mlb_api_data(self, date: str) -> List[Dict]:
        """Fetch game data from MLB API for a specific date"""
        try:
            # Format date for MLB API (MM/DD/YYYY)
            api_date = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
            
            # Construct API URL
            url = f"{self.mlb_api_base}/schedule"
            params = {
                "sportId": 1,  # MLB
                "date": api_date,
                "hydrate": "team,linescore,probablePitcher,person,stats"
            }
            
            # Add API key if available
            if self.api_key:
                params["apikey"] = self.api_key
            
            # Make API request
            logger.info(f"Fetching MLB API data for {date}")
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"MLB API error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            # Extract games from response
            games = []
            for date_data in data.get('dates', []):
                games.extend(date_data.get('games', []))
            
            self.stats['games_fetched'] += len(games)
            logger.info(f"Found {len(games)} games for {date}")
            
            return games
        
        except Exception as e:
            logger.error(f"Error fetching MLB API data for {date}: {str(e)}")
            self.stats['errors'] += 1
            return []
    
    def extract_pitcher_info(self, game_data: Dict, team_type: str) -> Dict:
        """Extract pitcher information for a team from game data"""
        pitcher_info = {
            "id": "",
            "name": "TBD"
        }
        
        try:
            team_data = game_data.get(f"{team_type}Team", {})
            probable_pitcher = team_data.get("probablePitcher", {})
            
            if probable_pitcher:
                pitcher_info["id"] = str(probable_pitcher.get("id", ""))
                pitcher_info["name"] = probable_pitcher.get("fullName", "TBD")
            
            return pitcher_info
        
        except Exception as e:
            logger.error(f"Error extracting pitcher info: {str(e)}")
            return pitcher_info
    
    def convert_to_normalized_format(self, game: Dict, date: str) -> Dict:
        """Convert MLB API game data to our normalized format"""
        game_id = str(game.get('gamePk', ''))
        
        # Extract team names
        away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', '')
        home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', '')
        
        # Extract game status
        status = game.get('status', {}).get('detailedState', '')
        
        # Extract game time
        game_date_str = game.get('gameDate', '')
        game_time = game_date_str
        
        # Extract scores
        away_score = game.get('teams', {}).get('away', {}).get('score', 0)
        home_score = game.get('teams', {}).get('home', {}).get('score', 0)
        
        # Extract pitcher information
        away_pitcher = self.extract_pitcher_info(game.get('teams', {}), 'away')
        home_pitcher = self.extract_pitcher_info(game.get('teams', {}), 'home')
        
        # Create normalized game object
        normalized_game = {
            "game_id": game_id,
            "date": date,
            "away_team": away_team,
            "home_team": home_team,
            "status": status,
            "start_time": game_time,
            "away_score": away_score,
            "home_score": home_score,
            "away_pitcher": away_pitcher,
            "home_pitcher": home_pitcher
        }
        
        return normalized_game
    
    def convert_to_game_scores_format(self, game: Dict, date: str) -> Dict:
        """Convert MLB API game data to game_scores_cache.json format"""
        game_pk = game.get('gamePk', '')
        
        # Extract team information
        away_team = game.get('teams', {}).get('away', {}).get('team', {})
        away_team_name = away_team.get('name', '')
        away_team_id = away_team.get('id', '')
        
        home_team = game.get('teams', {}).get('home', {}).get('team', {})
        home_team_name = home_team.get('name', '')
        home_team_id = home_team.get('id', '')
        
        # Extract game status
        status = game.get('status', {}).get('detailedState', '')
        status_code = game.get('status', {}).get('abstractGameCode', '')
        
        # Extract game time
        game_date_str = game.get('gameDate', '')
        
        # Extract scores
        away_score = game.get('teams', {}).get('away', {}).get('score', 0)
        home_score = game.get('teams', {}).get('home', {}).get('score', 0)
        total_score = away_score + home_score
        
        # Determine winning team
        winning_team = home_team_name if home_score > away_score else away_team_name
        if away_score == home_score:
            winning_team = ""
        score_differential = abs(home_score - away_score)
        
        # Extract pitcher information
        away_pitcher_name = "TBD"
        away_pitcher_data = game.get('teams', {}).get('away', {}).get('probablePitcher', {})
        if away_pitcher_data:
            away_pitcher_name = away_pitcher_data.get('fullName', 'TBD')
        
        home_pitcher_name = "TBD"
        home_pitcher_data = game.get('teams', {}).get('home', {}).get('probablePitcher', {})
        if home_pitcher_data:
            home_pitcher_name = home_pitcher_data.get('fullName', 'TBD')
        
        # Create game scores object
        game_scores_data = {
            "game_pk": game_pk,
            "away_team": away_team_name,
            "away_team_id": away_team_id,
            "home_team": home_team_name,
            "home_team_id": home_team_id,
            "status": status,
            "status_code": status_code,
            "game_time": game_date_str,
            "away_pitcher": away_pitcher_name,
            "home_pitcher": home_pitcher_name,
            "game_date": game_date_str,
            "is_final": status == "Final",
            "away_score": away_score,
            "home_score": home_score,
            "total_score": total_score,
            "winning_team": winning_team if total_score > 0 else "",
            "score_differential": score_differential,
            "data_source": "MLB API"
        }
        
        return game_scores_data
    
    def update_game_data_for_date(self, date: str) -> bool:
        """Update game data for a specific date using MLB API"""
        try:
            # Fetch MLB API data for the date
            mlb_games = self.fetch_mlb_api_data(date)
            
            if not mlb_games:
                logger.warning(f"No games found in MLB API for {date}")
                return False
            
            # Load existing data
            game_scores = self.load_json_file(self.game_scores_path)
            normalized_games = self.load_json_file(self.normalized_game_path)
            
            # Prepare new data
            if date not in game_scores:
                game_scores[date] = {"games": []}
            
            if date not in normalized_games:
                normalized_games[date] = {}
            
            # Convert MLB API data to our formats
            game_scores_games = []
            normalized_date_games = {}
            
            for mlb_game in mlb_games:
                game_scores_format = self.convert_to_game_scores_format(mlb_game, date)
                normalized_format = self.convert_to_normalized_format(mlb_game, date)
                
                game_id = str(mlb_game.get('gamePk', ''))
                
                if not game_id.isdigit():
                    logger.warning(f"Skipping game with invalid ID: {game_id}")
                    continue
                
                game_scores_games.append(game_scores_format)
                normalized_date_games[game_id] = normalized_format
                
                self.stats['games_updated'] += 1
                
                # Check if we updated pitcher info
                if (game_scores_format.get('away_pitcher', 'TBD') != 'TBD' or 
                    game_scores_format.get('home_pitcher', 'TBD') != 'TBD'):
                    self.stats['pitchers_updated'] += 1
            
            # Update game_scores_cache.json
            game_scores[date]['games'] = game_scores_games
            game_scores[date]['total_games'] = len(game_scores_games)
            game_scores[date]['completed_games'] = sum(1 for g in game_scores_games if g.get('is_final', False))
            
            # Update normalized_game_data.json
            normalized_games[date] = normalized_date_games
            
            # Save updated data
            self.save_json_file(self.game_scores_path, game_scores)
            self.save_json_file(self.normalized_game_path, normalized_games)
            
            logger.info(f"Updated {len(game_scores_games)} games for {date}")
            self.stats['dates_processed'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating game data for {date}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def update_date_range(self, start_date: str, end_date: str) -> Dict:
        """Update game data for a range of dates"""
        date_range = self.get_date_range(start_date, end_date)
        
        logger.info(f"Processing {len(date_range)} dates from {start_date} to {end_date}")
        
        for date in date_range:
            logger.info(f"Processing date: {date}")
            self.update_game_data_for_date(date)
        
        return self.stats

def main():
    """Main function to run the MLB API Integration"""
    if len(sys.argv) != 3:
        print("Usage: python mlb_api_integration.py <start_date> <end_date>")
        print("Example: python mlb_api_integration.py 2025-08-07 2025-08-13")
        return False
    
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    
    try:
        # Validate date format
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return False
    
    print(f"=== MLB API Integration: {start_date} to {end_date} ===")
    integrator = MLBApiIntegration()
    stats = integrator.update_date_range(start_date, end_date)
    
    print("\n=== Integration Complete ===")
    print(f"Dates processed: {stats['dates_processed']}")
    print(f"Games fetched from API: {stats['games_fetched']}")
    print(f"Games updated: {stats['games_updated']}")
    print(f"Games with pitcher info: {stats['pitchers_updated']}")
    print(f"Errors: {stats['errors']}")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
