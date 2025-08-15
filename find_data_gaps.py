#!/usr/bin/env python3
"""
MLB Data Gap Finder

This script identifies specific games that are missing predictions or betting lines.
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_gap_finder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GapFinder')

class MLBDataGapFinder:
    def __init__(self):
        """Initialize the MLB Data Gap Finder"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        
        # Team name variations
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
            return {}
    
    def find_gaps(self, date: str) -> Dict:
        """Find data gaps for a specific date"""
        result = {
            'date': date,
            'games_found': 0,
            'games_with_predictions': 0,
            'games_with_betting_lines': 0,
            'missing_predictions': [],
            'missing_betting_lines': []
        }
        
        # Load data files
        game_scores = self.load_json_file(self.game_scores_path)
        predictions = self.load_json_file(self.historical_predictions_path)
        betting_lines = self.load_json_file(self.betting_lines_path)
        
        # Skip if no games for this date
        if date not in game_scores:
            return result
        
        # Get games for this date
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            return result
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            return result
        
        # Build game information
        game_info = {}
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if game_id and away_team and home_team:
                game_info[game_id] = {
                    'game_id': game_id,
                    'away_team': away_team,
                    'home_team': home_team,
                    'matchup': f"{away_team} @ {home_team}",
                    'has_prediction': False,
                    'has_betting_line': False
                }
        
        result['games_found'] = len(game_info)
        
        # Check for predictions
        date_predictions = predictions.get(date, {})
        if isinstance(date_predictions, dict):
            for pred_id, prediction in date_predictions.items():
                if not isinstance(prediction, dict):
                    continue
                    
                pred_game_id = str(prediction.get('game_id', ''))
                
                if pred_game_id in game_info:
                    game_info[pred_game_id]['has_prediction'] = True
        
        # Check for betting lines
        date_lines = betting_lines.get(date, {})
        if isinstance(date_lines, dict):
            for line_id, line_data in date_lines.items():
                if not isinstance(line_data, dict):
                    continue
                    
                line_game_id = str(line_data.get('game_id', ''))
                
                if line_game_id in game_info:
                    game_info[line_game_id]['has_betting_line'] = True
        
        # Count and record missing items
        for game_id, info in game_info.items():
            if info['has_prediction']:
                result['games_with_predictions'] += 1
            else:
                result['missing_predictions'].append(info)
                
            if info['has_betting_line']:
                result['games_with_betting_lines'] += 1
            else:
                result['missing_betting_lines'].append(info)
        
        return result
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed gap report"""
        report = f"=== MLB Data Gap Report ===\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        total_games = 0
        total_with_predictions = 0
        total_with_betting_lines = 0
        all_missing_predictions = []
        all_missing_betting_lines = []
        
        # Process each date
        for date, result in results.items():
            total_games += result['games_found']
            total_with_predictions += result['games_with_predictions']
            total_with_betting_lines += result['games_with_betting_lines']
            all_missing_predictions.extend(result['missing_predictions'])
            all_missing_betting_lines.extend(result['missing_betting_lines'])
        
        # Generate overall stats
        pred_coverage = 0
        betting_coverage = 0
        if total_games > 0:
            pred_coverage = round(total_with_predictions / total_games * 100, 1)
            betting_coverage = round(total_with_betting_lines / total_games * 100, 1)
            
        report += f"Overall Statistics:\n"
        report += f"Total games: {total_games}\n"
        report += f"Games with predictions: {total_with_predictions} ({pred_coverage}%)\n"
        report += f"Games with betting lines: {total_with_betting_lines} ({betting_coverage}%)\n\n"
        
        # Missing predictions section
        report += f"Missing Predictions ({len(all_missing_predictions)}):\n"
        if all_missing_predictions:
            report += f"{'Date':<12} {'Game ID':<10} {'Matchup':<30}\n"
            report += f"{'-' * 52}\n"
            
            for game in sorted(all_missing_predictions, key=lambda x: x.get('game_id', '')):
                date = next((d for d, r in results.items() if game in r['missing_predictions']), "Unknown")
                report += f"{date:<12} {game['game_id']:<10} {game['matchup']:<30}\n"
        else:
            report += "No missing predictions found. Great job!\n"
        
        report += "\n"
        
        # Missing betting lines section
        report += f"Missing Betting Lines ({len(all_missing_betting_lines)}):\n"
        if all_missing_betting_lines:
            report += f"{'Date':<12} {'Game ID':<10} {'Matchup':<30}\n"
            report += f"{'-' * 52}\n"
            
            for game in sorted(all_missing_betting_lines, key=lambda x: x.get('game_id', '')):
                date = next((d for d, r in results.items() if game in r['missing_betting_lines']), "Unknown")
                report += f"{date:<12} {game['game_id']:<10} {game['matchup']:<30}\n"
        else:
            report += "No missing betting lines found. Great job!\n"
        
        # Write report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.root_dir, f"detailed_gap_report_{timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Detailed gap report written to {report_path}")
        print(f"\nDetailed report written to {os.path.basename(report_path)}")
        
        return report

def main():
    """Main function to find data gaps"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"=== MLB Data Gap Finder ===")
    print(f"Analyzing game data to find gaps in predictions and betting lines")
    print(f"Date: {current_date}")
    
    finder = MLBDataGapFinder()
    
    # Define date range (all of August)
    start_date = "2025-08-07"  # Default to August 7
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    end_date = datetime.now().strftime("%Y-%m-%d")  # Default to today
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    print(f"\nAnalyzing data from {start_date} to {end_date}")
    
    # Generate date range
    from datetime import timedelta
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    date_range = []
    current = start
    while current <= end:
        date_range.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    # Process each date
    results = {}
    for date in date_range:
        print(f"Analyzing {date}...")
        results[date] = finder.find_gaps(date)
    
    # Generate report
    finder.generate_report(results)

if __name__ == "__main__":
    main()
