#!/usr/bin/env python3
"""
MLB Data Synchronization Script

This script ensures all system components use the same MLB data by:
1. Synchronizing game IDs across all data files
2. Updating pitcher information everywhere
3. Validating data consistency
4. Generating a comprehensive report
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_synchronizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DataSynchronizer')

class MLBDataSynchronizer:
    def __init__(self):
        """Initialize the MLB Data Synchronization tool"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths - check both root and mlb-clean-deploy directories
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.team_strength_path = os.path.join(self.root_dir, 'team_strength_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        
        # Check for normalized_game_data.json
        utils_path = os.path.join(self.root_dir, 'utils')
        if not os.path.exists(utils_path):
            utils_path = os.path.join(self.root_dir, 'mlb-clean-deploy', 'utils')
            if not os.path.exists(utils_path):
                os.makedirs(utils_path, exist_ok=True)
        self.normalized_game_path = os.path.join(utils_path, 'normalized_game_data.json')
        
        # Team name variations
        self.team_name_variations = self._load_team_variations()
        
        # Track stats
        self.stats = {
            'dates_processed': 0,
            'games_synchronized': 0,
            'pitcher_updates': 0,
            'id_updates': 0,
            'inconsistencies': 0,
            'errors': 0
        }
        
        # Store inconsistencies for reporting
        self.inconsistencies = []
    
    def _load_team_variations(self) -> Dict[str, List[str]]:
        """Load team name variations to handle different formats"""
        # This maps official MLB team names to various formats that might appear in data
        return {
            "Arizona Diamondbacks": ["Arizona", "Diamondbacks", "ARI", "Arizona D-backs", "AZ", "D-backs"],
            "Atlanta Braves": ["Atlanta", "Braves", "ATL"],
            "Baltimore Orioles": ["Baltimore", "Orioles", "BAL"],
            "Boston Red Sox": ["Boston", "Red Sox", "BOS"],
            "Chicago Cubs": ["Chicago Cubs", "Cubs", "CHC", "CHI"],
            "Chicago White Sox": ["Chicago White Sox", "White Sox", "CWS", "CHW"],
            "Cincinnati Reds": ["Cincinnati", "Reds", "CIN"],
            "Cleveland Guardians": ["Cleveland", "Guardians", "CLE", "Cleveland Indians"],
            "Colorado Rockies": ["Colorado", "Rockies", "COL"],
            "Detroit Tigers": ["Detroit", "Tigers", "DET"],
            "Houston Astros": ["Houston", "Astros", "HOU"],
            "Kansas City Royals": ["Kansas City", "Royals", "KC", "KCR"],
            "Los Angeles Angels": ["LA Angels", "Angels", "LAA", "Los Angeles Angels"],
            "Los Angeles Dodgers": ["LA Dodgers", "Dodgers", "LAD", "Los Angeles Dodgers"],
            "Miami Marlins": ["Miami", "Marlins", "MIA"],
            "Milwaukee Brewers": ["Milwaukee", "Brewers", "MIL"],
            "Minnesota Twins": ["Minnesota", "Twins", "MIN"],
            "New York Mets": ["NY Mets", "Mets", "NYM", "New York Mets"],
            "New York Yankees": ["NY Yankees", "Yankees", "NYY", "New York Yankees"],
            "Oakland Athletics": ["Oakland", "Athletics", "OAK", "Oakland A's", "A's"],
            "Philadelphia Phillies": ["Philadelphia", "Phillies", "PHI"],
            "Pittsburgh Pirates": ["Pittsburgh", "Pirates", "PIT"],
            "San Diego Padres": ["San Diego", "Padres", "SD", "SDP"],
            "San Francisco Giants": ["SF Giants", "Giants", "SF", "SFG"],
            "Seattle Mariners": ["Seattle", "Mariners", "SEA"],
            "St. Louis Cardinals": ["St. Louis", "Cardinals", "STL"],
            "Tampa Bay Rays": ["Tampa Bay", "Rays", "TB", "TBR"],
            "Texas Rangers": ["Texas", "Rangers", "TEX"],
            "Toronto Blue Jays": ["Toronto", "Blue Jays", "TOR"],
            "Washington Nationals": ["Washington", "Nationals", "WSH", "WAS"]
        }
    
    def standardize_team_name(self, team_name: str) -> str:
        """Standardize team name to official MLB team name"""
        if not team_name:
            return ""
            
        # Check if it's already an official name
        for official_name in self.team_name_variations.keys():
            if team_name == official_name:
                return official_name
        
        # Try to match with variations
        for official_name, variations in self.team_name_variations.items():
            if any(v.lower() == team_name.lower() for v in variations):
                return official_name
        
        # Last resort: try to find a partial match
        for official_name, variations in self.team_name_variations.items():
            if any(team_name.lower() in v.lower() or v.lower() in team_name.lower() 
                   for v in variations + [official_name]):
                return official_name
        
        # No match found
        logger.warning(f"Could not standardize team name: {team_name}")
        return team_name
    
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
            dir_path = os.path.dirname(filepath)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
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
    
    def build_game_reference(self, date: str) -> Dict[str, Dict]:
        """Build a reference dictionary of games by ID and by matchup"""
        reference = {
            'by_id': {},
            'by_matchup': {}
        }
        
        # Load game scores data
        game_scores = self.load_json_file(self.game_scores_path)
        if not game_scores:
            return reference
            
        # Check if date exists and has games
        if date not in game_scores:
            return reference
            
        # Get games array safely
        games_data = game_scores.get(date, {})
        if not isinstance(games_data, dict):
            return reference
            
        games = games_data.get('games', [])
        if not games or not isinstance(games, list):
            return reference
        
        # Process each game
        for game in games:
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if not game_id or not away_team or not home_team:
                continue
            
            # Standardize team names
            std_away_team = self.standardize_team_name(away_team)
            std_home_team = self.standardize_team_name(home_team)
            
            # Store by ID
            reference['by_id'][game_id] = {
                'away_team': std_away_team,
                'home_team': std_home_team,
                'away_pitcher': game.get('away_pitcher', 'TBD'),
                'home_pitcher': game.get('home_pitcher', 'TBD'),
                'status': game.get('status', ''),
                'is_final': game.get('is_final', False),
                'away_score': game.get('away_score', 0),
                'home_score': game.get('home_score', 0)
            }
            
            # Store by matchup
            matchup_key = f"{std_away_team}@{std_home_team}"
            reference['by_matchup'][matchup_key] = game_id
        
        return reference
    
    def synchronize_historical_predictions(self, date: str, reference: Dict) -> int:
        """Synchronize historical predictions with official game data"""
        historical_predictions = self.load_json_file(self.historical_predictions_path)
        if not historical_predictions:
            return 0
            
        if date not in historical_predictions:
            return 0
        
        updates = 0
        date_predictions = historical_predictions[date]
        if not isinstance(date_predictions, dict):
            return 0
        
        for pred_id, prediction in date_predictions.items():
            if not isinstance(prediction, dict):
                continue
                
            away_team = prediction.get('away_team', '')
            home_team = prediction.get('home_team', '')
            
            if not away_team or not home_team:
                continue
            
            # Standardize team names
            std_away_team = self.standardize_team_name(away_team)
            std_home_team = self.standardize_team_name(home_team)
            
            # Try to find matching game
            matchup_key = f"{std_away_team}@{std_home_team}"
            if matchup_key in reference['by_matchup']:
                official_game_id = reference['by_matchup'][matchup_key]
                current_game_id = str(prediction.get('game_id', ''))
                
                # Update game ID if needed
                if current_game_id != official_game_id:
                    prediction['game_id'] = official_game_id
                    updates += 1
                    self.stats['id_updates'] += 1
                
                # Update pitcher information if available
                if official_game_id in reference['by_id']:
                    game_info = reference['by_id'][official_game_id]
                    
                    current_away_pitcher = prediction.get('away_pitcher', '')
                    official_away_pitcher = game_info['away_pitcher']
                    if official_away_pitcher != 'TBD' and current_away_pitcher != official_away_pitcher:
                        prediction['away_pitcher'] = official_away_pitcher
                        updates += 1
                        self.stats['pitcher_updates'] += 1
                    
                    current_home_pitcher = prediction.get('home_pitcher', '')
                    official_home_pitcher = game_info['home_pitcher']
                    if official_home_pitcher != 'TBD' and current_home_pitcher != official_home_pitcher:
                        prediction['home_pitcher'] = official_home_pitcher
                        updates += 1
                        self.stats['pitcher_updates'] += 1
            else:
                # Record inconsistency
                self.inconsistencies.append({
                    'date': date,
                    'type': 'prediction_no_match',
                    'away_team': away_team,
                    'home_team': home_team,
                    'pred_id': pred_id
                })
                self.stats['inconsistencies'] += 1
        
        if updates > 0:
            self.save_json_file(self.historical_predictions_path, historical_predictions)
            logger.info(f"Updated {updates} entries in historical predictions for {date}")
        
        return updates
    
    def synchronize_betting_lines(self, date: str, reference: Dict) -> int:
        """Synchronize betting lines with official game data"""
        betting_lines = self.load_json_file(self.betting_lines_path)
        if not betting_lines:
            return 0
            
        if date not in betting_lines:
            return 0
        
        updates = 0
        date_lines = betting_lines[date]
        if not isinstance(date_lines, dict):
            return 0
        
        for line_id, line_data in date_lines.items():
            if not isinstance(line_data, dict):
                continue
                
            away_team = line_data.get('away_team', '')
            home_team = line_data.get('home_team', '')
            
            if not away_team or not home_team:
                continue
            
            # Standardize team names
            std_away_team = self.standardize_team_name(away_team)
            std_home_team = self.standardize_team_name(home_team)
            
            # Try to find matching game
            matchup_key = f"{std_away_team}@{std_home_team}"
            if matchup_key in reference['by_matchup']:
                official_game_id = reference['by_matchup'][matchup_key]
                current_game_id = str(line_data.get('game_id', ''))
                
                # Update game ID if needed
                if current_game_id != official_game_id:
                    line_data['game_id'] = official_game_id
                    updates += 1
                    self.stats['id_updates'] += 1
            else:
                # Record inconsistency
                self.inconsistencies.append({
                    'date': date,
                    'type': 'betting_no_match',
                    'away_team': away_team,
                    'home_team': home_team,
                    'line_id': line_id
                })
                self.stats['inconsistencies'] += 1
        
        if updates > 0:
            self.save_json_file(self.betting_lines_path, betting_lines)
            logger.info(f"Updated {updates} entries in betting lines for {date}")
        
        return updates
    
    def synchronize_normalized_games(self, date: str, reference: Dict) -> int:
        """Synchronize normalized game data with official game data"""
        normalized_games = self.load_json_file(self.normalized_game_path)
        if not normalized_games:
            normalized_games = {}
        
        if date not in normalized_games:
            normalized_games[date] = {}
        
        # Ensure date entry is a dictionary
        if not isinstance(normalized_games[date], dict):
            normalized_games[date] = {}
        
        updates = 0
        
        # Update normalized games with reference data
        for game_id, game_info in reference['by_id'].items():
            if game_id not in normalized_games[date]:
                # Create new entry
                normalized_games[date][game_id] = {
                    "game_id": game_id,
                    "date": date,
                    "away_team": game_info['away_team'],
                    "home_team": game_info['home_team'],
                    "status": game_info['status'],
                    "start_time": "",
                    "away_score": game_info['away_score'],
                    "home_score": game_info['home_score'],
                    "away_pitcher": {
                        "id": "",
                        "name": game_info['away_pitcher']
                    },
                    "home_pitcher": {
                        "id": "",
                        "name": game_info['home_pitcher']
                    }
                }
                updates += 1
            else:
                # Get existing entry
                existing = normalized_games[date][game_id]
                if not isinstance(existing, dict):
                    # If existing entry is invalid, recreate it
                    normalized_games[date][game_id] = {
                        "game_id": game_id,
                        "date": date,
                        "away_team": game_info['away_team'],
                        "home_team": game_info['home_team'],
                        "status": game_info['status'],
                        "start_time": "",
                        "away_score": game_info['away_score'],
                        "home_score": game_info['home_score'],
                        "away_pitcher": {
                            "id": "",
                            "name": game_info['away_pitcher']
                        },
                        "home_pitcher": {
                            "id": "",
                            "name": game_info['home_pitcher']
                        }
                    }
                    updates += 1
                    continue
                
                # Ensure pitcher fields are dictionaries
                if not isinstance(existing.get('away_pitcher'), dict):
                    existing['away_pitcher'] = {"id": "", "name": game_info['away_pitcher']}
                    updates += 1
                
                if not isinstance(existing.get('home_pitcher'), dict):
                    existing['home_pitcher'] = {"id": "", "name": game_info['home_pitcher']}
                    updates += 1
                
                # Update pitcher info if needed
                if game_info['away_pitcher'] != 'TBD' and existing['away_pitcher'].get('name', '') != game_info['away_pitcher']:
                    existing['away_pitcher']['name'] = game_info['away_pitcher']
                    updates += 1
                
                if game_info['home_pitcher'] != 'TBD' and existing['home_pitcher'].get('name', '') != game_info['home_pitcher']:
                    existing['home_pitcher']['name'] = game_info['home_pitcher']
                    updates += 1
                
                # Update scores if game is final
                if game_info['is_final']:
                    if existing.get('away_score') != game_info['away_score']:
                        existing['away_score'] = game_info['away_score']
                        updates += 1
                    
                    if existing.get('home_score') != game_info['home_score']:
                        existing['home_score'] = game_info['home_score']
                        updates += 1
                    
                    if existing.get('status') != "Final":
                        existing['status'] = "Final"
                        updates += 1
        
        if updates > 0:
            self.save_json_file(self.normalized_game_path, normalized_games)
            logger.info(f"Updated {updates} entries in normalized games for {date}")
        
        return updates
    
    def process_date(self, date: str) -> bool:
        """Process a single date to synchronize data"""
        try:
            logger.info(f"Processing date: {date}")
            
            # Build reference data
            reference = self.build_game_reference(date)
            
            # Even if no reference games, we still consider this successful
            # as there might just be no games for this date
            if not reference['by_id']:
                logger.warning(f"No reference games found for {date}")
                self.stats['dates_processed'] += 1
                return True
            
            # Synchronize historical predictions
            try:
                pred_updates = self.synchronize_historical_predictions(date, reference)
            except Exception as e:
                logger.error(f"Error synchronizing predictions for {date}: {str(e)}")
                pred_updates = 0
            
            # Synchronize betting lines
            try:
                betting_updates = self.synchronize_betting_lines(date, reference)
            except Exception as e:
                logger.error(f"Error synchronizing betting lines for {date}: {str(e)}")
                betting_updates = 0
            
            # Synchronize normalized game data
            try:
                norm_updates = self.synchronize_normalized_games(date, reference)
            except Exception as e:
                logger.error(f"Error synchronizing normalized games for {date}: {str(e)}")
                norm_updates = 0
            
            total_updates = pred_updates + betting_updates + norm_updates
            if total_updates > 0:
                self.stats['games_synchronized'] += 1
            
            self.stats['dates_processed'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error processing date {date}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def generate_report(self) -> str:
        """Generate a synchronization report"""
        report = f"=== MLB Data Synchronization Report ===\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += f"Dates processed: {self.stats['dates_processed']}\n"
        report += f"Games synchronized: {self.stats['games_synchronized']}\n"
        report += f"Game ID updates: {self.stats['id_updates']}\n"
        report += f"Pitcher updates: {self.stats['pitcher_updates']}\n"
        report += f"Inconsistencies found: {self.stats['inconsistencies']}\n"
        report += f"Errors: {self.stats['errors']}\n\n"
        
        if self.inconsistencies:
            report += "=== Inconsistencies ===\n"
            for issue in self.inconsistencies:
                report += f"Date: {issue['date']}, Type: {issue['type']}, "
                report += f"Teams: {issue['away_team']} @ {issue['home_team']}\n"
        
        report_path = os.path.join(self.root_dir, f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        
        return report
    
    def process_date_range(self, start_date: str = None, end_date: str = None) -> Dict:
        """Process a range of dates for synchronization"""
        date_range = self.get_date_range(start_date, end_date)
        
        logger.info(f"Processing {len(date_range)} dates from {date_range[0]} to {date_range[-1]}")
        
        for date in date_range:
            self.process_date(date)
        
        # Generate report
        self.generate_report()
        
        return self.stats

def main():
    """Main function to run the MLB Data Synchronizer"""
    start_date = None
    end_date = None
    
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    print(f"=== MLB Data Synchronization ===")
    if start_date and end_date:
        print(f"Date range: {start_date} to {end_date}")
    elif start_date:
        print(f"From date: {start_date} to today")
    else:
        print("Processing last 7 days")
        
    synchronizer = MLBDataSynchronizer()
    stats = synchronizer.process_date_range(start_date, end_date)
    
    print("\n=== Synchronization Complete ===")
    print(f"Dates processed: {stats['dates_processed']}")
    print(f"Games synchronized: {stats['games_synchronized']}")
    print(f"Game ID updates: {stats['id_updates']}")
    print(f"Pitcher updates: {stats['pitcher_updates']}")
    print(f"Inconsistencies: {stats['inconsistencies']}")
    print(f"Errors: {stats['errors']}")
    
    print("\nReport generated: sync_report_*.txt")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
