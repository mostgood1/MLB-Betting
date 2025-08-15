#!/usr/bin/env python3
"""
MLB Data Backfill Script

This script fills gaps in the MLB data by:
1. Generating missing predictions
2. Linking betting lines to game IDs
3. Ensuring data consistency across all files
"""

import json
import os
import sys
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backfill.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DataBackfill')

class MLBDataBackfill:
    def __init__(self):
        """Initialize the MLB Data Backfill tool"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.team_strength_path = os.path.join(self.root_dir, 'team_strength_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        
        # Check for normalized_game_data.json
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
            'predictions_generated': 0,
            'betting_lines_linked': 0,
            'errors': 0
        }
        
        # Current date
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        # Team name variations to handle different formats
        self.team_name_variations = self._load_team_variations()
    
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
            "Oakland Athletics": ["Oakland", "Athletics", "OAK", "Oakland A's", "A's", "Athletics"],
            "Philadelphia Phillies": ["Philadelphia", "Phillies", "PHI"],
            "Pittsburgh Pirates": ["Pittsburgh", "Pirates", "PIT"],
            "San Diego Padres": ["San Diego", "Padres", "SD", "SDP"],
            "San Francisco Giants": ["SF Giants", "Giants", "SF", "SFG"],
            "Seattle Mariners": ["Seattle", "Mariners", "SEA"],
            "St. Louis Cardinals": ["St. Louis", "Cardinals", "STL"],
            "Tampa Bay Rays": ["Tampa Bay", "Rays", "TB", "TBR"],
            "Texas Rangers": ["Texas", "Rangers", "TEX"],
            "Toronto Blue Jays": ["Toronto", "Blue Jays", "TOR"],
            "Washington Nationals": ["Washington", "Nationals", "WSH", "WAS", "WSN"]
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
    
    def get_date_range(self, start_date: str, end_date: str = None) -> List[str]:
        """Generate a list of dates between start_date and end_date (inclusive)"""
        if not end_date:
            end_date = self.today
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_list = []
        current = start
        
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return date_list
    
    def generate_missing_predictions(self, date: str) -> int:
        """Generate missing predictions for a specific date"""
        game_scores = self.load_json_file(self.game_scores_path)
        historical_predictions = self.load_json_file(self.historical_predictions_path)
        team_strength = self.load_json_file(self.team_strength_path)
        
        if not game_scores or date not in game_scores:
            return 0
        
        # Initialize historical predictions for this date if needed
        if date not in historical_predictions:
            historical_predictions[date] = {}
        
        # Get games data safely
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            return 0
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            return 0
        
        # Get existing predictions
        existing_predictions = historical_predictions.get(date, {})
        if not isinstance(existing_predictions, dict):
            existing_predictions = {}
            historical_predictions[date] = existing_predictions
        
        # Process each game
        predictions_added = 0
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if not game_id or not away_team or not home_team:
                continue
            
            # Standardize team names
            std_away_team = self.standardize_team_name(away_team)
            std_home_team = self.standardize_team_name(home_team)
            
            # Create a matchup key for checking
            matchup_key = f"{std_away_team}@{std_home_team}"
            
            # Check if prediction already exists for this game
            prediction_exists = False
            for pred_id, prediction in existing_predictions.items():
                if not isinstance(prediction, dict):
                    continue
                    
                pred_away = prediction.get('away_team', '')
                pred_home = prediction.get('home_team', '')
                
                # Standardize names for comparison
                std_pred_away = self.standardize_team_name(pred_away)
                std_pred_home = self.standardize_team_name(pred_home)
                
                if std_away_team == std_pred_away and std_home_team == std_pred_home:
                    # Update existing prediction with correct game ID
                    prediction['game_id'] = game_id
                    prediction_exists = True
                    predictions_added += 1
                    break
            
            if not prediction_exists:
                # Generate a new prediction
                away_strength = 0.5
                home_strength = 0.5
                
                # Try to get team strengths if available
                try:
                    if std_away_team in team_strength and isinstance(team_strength[std_away_team], dict):
                        away_strength = team_strength[std_away_team].get('overall_rating', 0.5)
                except (TypeError, AttributeError):
                    pass
                    
                try:
                    if std_home_team in team_strength and isinstance(team_strength[std_home_team], dict):
                        home_strength = team_strength[std_home_team].get('overall_rating', 0.5)
                except (TypeError, AttributeError):
                    pass
                
                # Add home field advantage
                home_strength += 0.05
                
                # Calculate win probabilities
                total_strength = away_strength + home_strength
                away_win_pct = away_strength / total_strength
                home_win_pct = home_strength / total_strength
                
                # Generate a prediction ID
                pred_id = f"backfill_{date}_{game_id}"
                
                # Create prediction
                prediction = {
                    "game_id": game_id,
                    "away_team": std_away_team,
                    "home_team": std_home_team,
                    "away_win_pct": round(away_win_pct, 3),
                    "home_win_pct": round(home_win_pct, 3),
                    "away_pitcher": game.get('away_pitcher', 'TBD'),
                    "home_pitcher": game.get('home_pitcher', 'TBD'),
                    "prediction_time": datetime.now().isoformat(),
                    "model_version": "backfill-1.0",
                    "source": "backfill"
                }
                
                # Add to historical predictions
                existing_predictions[pred_id] = prediction
                predictions_added += 1
        
        # Save updated predictions
        if predictions_added > 0:
            self.save_json_file(self.historical_predictions_path, historical_predictions)
            logger.info(f"Added {predictions_added} predictions for {date}")
        
        self.stats['predictions_generated'] += predictions_added
        return predictions_added
    
    def link_betting_lines(self, date: str) -> int:
        """Link betting lines to game IDs for a specific date"""
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
                # Standardize team names
                std_away_team = self.standardize_team_name(away_team)
                std_home_team = self.standardize_team_name(home_team)
                
                key = f"{std_away_team}@{std_home_team}"
                game_id_by_matchup[key] = game_id
        
        # Update betting lines with correct game IDs
        links_updated = 0
        date_lines = betting_lines.get(date, {})
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
            if matchup_key in game_id_by_matchup:
                official_game_id = game_id_by_matchup[matchup_key]
                current_game_id = str(line_data.get('game_id', ''))
                
                # Update game ID if needed
                if current_game_id != official_game_id:
                    line_data['game_id'] = official_game_id
                    links_updated += 1
        
        # Save updated betting lines
        if links_updated > 0:
            self.save_json_file(self.betting_lines_path, betting_lines)
            logger.info(f"Updated {links_updated} betting lines for {date}")
        
        self.stats['betting_lines_linked'] += links_updated
        return links_updated
    
    def process_date(self, date: str) -> bool:
        """Process a single date to backfill data"""
        try:
            logger.info(f"Processing date: {date}")
            
            # First, generate missing predictions
            predictions = self.generate_missing_predictions(date)
            
            # Then link betting lines to game IDs
            betting_links = self.link_betting_lines(date)
            
            self.stats['dates_processed'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error processing date {date}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def generate_report(self) -> str:
        """Generate a backfill report"""
        report = f"=== MLB Data Backfill Report ===\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += f"Dates processed: {self.stats['dates_processed']}\n"
        report += f"Predictions generated: {self.stats['predictions_generated']}\n"
        report += f"Betting lines linked: {self.stats['betting_lines_linked']}\n"
        report += f"Errors: {self.stats['errors']}\n"
        
        report_path = os.path.join(self.root_dir, f"backfill_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Also save as JSON for programmatic use
        json_report_path = os.path.join(self.root_dir, f"backfill_report_{datetime.now().strftime('%Y-%m-%d')}.json")
        with open(json_report_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        return report
    
    def process_date_range(self, start_date: str, end_date: str = None) -> Dict:
        """Process a range of dates for backfilling data"""
        date_range = self.get_date_range(start_date, end_date)
        
        logger.info(f"Processing {len(date_range)} dates from {date_range[0]} to {date_range[-1]}")
        
        for date in date_range:
            self.process_date(date)
        
        # Generate report
        self.generate_report()
        
        return self.stats

def main():
    """Main function to run the MLB Data Backfill"""
    start_date = "2025-08-07"
    end_date = None  # Today by default
    
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    print(f"=== MLB Data Backfill ===")
    if start_date and end_date:
        print(f"Date range: {start_date} to {end_date}")
    elif start_date:
        print(f"From date: {start_date} to today")
    else:
        print("Using default date range: Aug 7 to today")
        
    backfill = MLBDataBackfill()
    stats = backfill.process_date_range(start_date, end_date)
    
    print("\n=== Backfill Complete ===")
    print(f"Dates processed: {stats['dates_processed']}")
    print(f"Predictions generated: {stats['predictions_generated']}")
    print(f"Betting lines linked: {stats['betting_lines_linked']}")
    print(f"Errors: {stats['errors']}")
    
    print("\nReport generated: backfill_report_*.txt")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
