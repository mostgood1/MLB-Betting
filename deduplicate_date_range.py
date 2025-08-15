#!/usr/bin/env python3
"""
MLB Data Deduplication Script

This script ensures data consistency across all system files by:
1. Removing duplicate game entries
2. Ensuring consistent game IDs
3. Synchronizing game data across different cache files
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deduplicate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Deduplicator')

class MLBDataDeduplicator:
    def __init__(self):
        """Initialize the MLB Data Deduplication tool"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.team_strength_path = os.path.join(self.root_dir, 'team_strength_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        
        # Look for normalized_game_data.json in different possible locations
        utils_dir = os.path.join(self.root_dir, 'utils')
        if os.path.exists(utils_dir):
            self.normalized_game_path = os.path.join(utils_dir, 'normalized_game_data.json')
        else:
            utils_dir = os.path.join(self.root_dir, 'mlb-clean-deploy', 'utils')
            if not os.path.exists(utils_dir):
                os.makedirs(utils_dir, exist_ok=True)
            self.normalized_game_path = os.path.join(utils_dir, 'normalized_game_data.json')
        
        # Track stats
        self.stats = {
            'dates_processed': 0,
            'duplicates_removed': 0,
            'games_synchronized': 0,
            'inconsistencies_fixed': 0,
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
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {filepath}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def get_date_range(self, start_date: str = None, end_date: str = None) -> List[str]:
        """Generate a list of dates between start_date and end_date (inclusive)"""
        if not start_date:
            # Default to 7 days ago
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        if not end_date:
            # Default to today
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_list = []
        current = start
        
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return date_list
    
    def deduplicate_game_scores(self, date: str) -> int:
        """Remove duplicate games from game_scores_cache.json for a specific date"""
        game_scores = self.load_json_file(self.game_scores_path)
        
        if not game_scores:
            logger.warning(f"No game scores data found")
            return 0
            
        if date not in game_scores:
            logger.warning(f"No game scores data found for {date}")
            return 0
            
        # Check if date entry is a dictionary and has games
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            logger.warning(f"Invalid data format for {date}")
            return 0
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            logger.warning(f"No games found for {date}")
            return 0
        
        # Track games by ID to find duplicates
        games_by_id = {}
        duplicates = 0
        
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            
            if not game_id:
                continue
                
            if game_id in games_by_id:
                # Found a duplicate
                duplicates += 1
                
                # Keep the more complete record (the one with pitcher info)
                if (game.get('away_pitcher', 'TBD') != 'TBD' or 
                    game.get('home_pitcher', 'TBD') != 'TBD'):
                    games_by_id[game_id] = game
            else:
                games_by_id[game_id] = game
        
        if duplicates > 0:
            # Update the game list with deduplicated games
            game_scores[date]['games'] = list(games_by_id.values())
            game_scores[date]['total_games'] = len(games_by_id)
            game_scores[date]['completed_games'] = sum(1 for g in games_by_id.values() if g.get('is_final', False))
            
            self.save_json_file(self.game_scores_path, game_scores)
            logger.info(f"Removed {duplicates} duplicate games for {date}")
        
        return duplicates
    
    def synchronize_historical_predictions(self, date: str) -> int:
        """Ensure historical_predictions_cache.json has consistent game IDs"""
        game_scores = self.load_json_file(self.game_scores_path)
        historical_predictions = self.load_json_file(self.historical_predictions_path)
        
        if not game_scores or date not in game_scores:
            return 0
            
        if not historical_predictions or date not in historical_predictions:
            return 0
        
        # Get games data safely
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            return 0
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            return 0
        
        # Build a mapping of games by teams
        game_id_by_matchup = {}
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if game_id and away_team and home_team:
                key = f"{away_team}@{home_team}"
                game_id_by_matchup[key] = game_id
        
        # Update historical predictions with correct game IDs
        updates = 0
        date_preds = historical_predictions.get(date, {})
        if not isinstance(date_preds, dict):
            return 0
            
        for pred_id, pred in date_preds.items():
            if not isinstance(pred, dict):
                continue
                
            away_team = pred.get('away_team', '')
            home_team = pred.get('home_team', '')
            key = f"{away_team}@{home_team}"
            
            if key in game_id_by_matchup:
                official_game_id = game_id_by_matchup[key]
                current_game_id = str(pred.get('game_id', ''))
                
                if current_game_id != official_game_id:
                    pred['game_id'] = official_game_id
                    updates += 1
        
        if updates > 0:
            self.save_json_file(self.historical_predictions_path, historical_predictions)
            logger.info(f"Updated {updates} game IDs in historical predictions for {date}")
        
        return updates
    
    def synchronize_betting_lines(self, date: str) -> int:
        """Ensure historical_betting_lines_cache.json has consistent game IDs"""
        game_scores = self.load_json_file(self.game_scores_path)
        betting_lines = self.load_json_file(self.betting_lines_path)
        
        if not game_scores or date not in game_scores:
            return 0
            
        if not betting_lines or date not in betting_lines:
            return 0
        
        # Get games data safely
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            return 0
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            return 0
        
        # Build a mapping of games by teams
        game_id_by_matchup = {}
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if game_id and away_team and home_team:
                key = f"{away_team}@{home_team}"
                game_id_by_matchup[key] = game_id
        
        # Update betting lines with correct game IDs
        updates = 0
        date_lines = betting_lines.get(date, {})
        if not isinstance(date_lines, dict):
            return 0
            
        for line_id, line_data in date_lines.items():
            if not isinstance(line_data, dict):
                continue
                
            away_team = line_data.get('away_team', '')
            home_team = line_data.get('home_team', '')
            key = f"{away_team}@{home_team}"
            
            if key in game_id_by_matchup:
                official_game_id = game_id_by_matchup[key]
                current_game_id = str(line_data.get('game_id', ''))
                
                if current_game_id != official_game_id:
                    line_data['game_id'] = official_game_id
                    updates += 1
        
        if updates > 0:
            self.save_json_file(self.betting_lines_path, betting_lines)
            logger.info(f"Updated {updates} game IDs in betting lines for {date}")
        
        return updates
    
    def update_normalized_games(self, date: str) -> int:
        """Update normalized_game_data.json with consistent game information"""
        game_scores = self.load_json_file(self.game_scores_path)
        normalized_games = self.load_json_file(self.normalized_game_path)
        
        if not game_scores:
            return 0
            
        if date not in game_scores:
            return 0
        
        # Get games data safely
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            return 0
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            return 0
        
        if not normalized_games:
            normalized_games = {}
        
        if date not in normalized_games:
            normalized_games[date] = {}
        
        updates = 0
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            if not game_id:
                continue
            
            # Create normalized game format
            normalized_game = {
                "game_id": game_id,
                "date": date,
                "away_team": game.get('away_team', ''),
                "home_team": game.get('home_team', ''),
                "status": game.get('status', ''),
                "start_time": game.get('game_time', ''),
                "away_score": game.get('away_score', 0),
                "home_score": game.get('home_score', 0),
                "away_pitcher": {
                    "id": "",
                    "name": game.get('away_pitcher', 'TBD')
                },
                "home_pitcher": {
                    "id": "",
                    "name": game.get('home_pitcher', 'TBD')
                }
            }
            
            # Update or add to normalized games
            normalized_games[date][game_id] = normalized_game
            updates += 1
        
        if updates > 0:
            self.save_json_file(self.normalized_game_path, normalized_games)
            logger.info(f"Updated {updates} games in normalized data for {date}")
        
        return updates
    
    def process_date(self, date: str) -> bool:
        """Process a single date to deduplicate and synchronize data"""
        try:
            logger.info(f"Processing date: {date}")
            
            # Step 1: Remove duplicates from game_scores_cache.json
            duplicates = self.deduplicate_game_scores(date)
            self.stats['duplicates_removed'] += duplicates
            
            # Step 2: Synchronize historical_predictions_cache.json
            pred_updates = self.synchronize_historical_predictions(date)
            self.stats['games_synchronized'] += pred_updates
            
            # Step 3: Synchronize historical_betting_lines_cache.json
            betting_updates = self.synchronize_betting_lines(date)
            self.stats['games_synchronized'] += betting_updates
            
            # Step 4: Update normalized_game_data.json
            norm_updates = self.update_normalized_games(date)
            self.stats['inconsistencies_fixed'] += norm_updates
            
            self.stats['dates_processed'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error processing date {date}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def process_date_range(self, start_date: str = None, end_date: str = None) -> Dict:
        """Process a range of dates for deduplication and synchronization"""
        date_range = self.get_date_range(start_date, end_date)
        
        logger.info(f"Processing {len(date_range)} dates from {start_date} to {end_date}")
        
        for date in date_range:
            self.process_date(date)
        
        return self.stats

def main():
    """Main function to run the MLB Data Deduplicator"""
    start_date = None
    end_date = None
    
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    deduplicator = MLBDataDeduplicator()
    stats = deduplicator.process_date_range(start_date, end_date)
    
    print("\n=== Deduplication Complete ===")
    print(f"Dates processed: {stats['dates_processed']}")
    print(f"Duplicates removed: {stats['duplicates_removed']}")
    print(f"Games synchronized: {stats['games_synchronized']}")
    print(f"Inconsistencies fixed: {stats['inconsistencies_fixed']}")
    print(f"Errors: {stats['errors']}")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
