#!/usr/bin/env python3
"""
MLB Data Backfill Validator

This script validates that the backfill process fixed data gaps by:
1. Checking that all games have predictions
2. Verifying betting lines are properly linked to game IDs
3. Generating a validation report
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
        logging.FileHandler('backfill_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ValidationTool')

class BackfillValidator:
    def __init__(self):
        """Initialize the Backfill Validator"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        
        # Track stats
        self.stats = {
            'dates_analyzed': 0,
            'games_found': 0,
            'games_with_predictions': 0,
            'games_with_betting_lines': 0,
            'prediction_coverage': 0.0,
            'betting_line_coverage': 0.0
        }
        
        # Current date
        self.today = datetime.now().strftime('%Y-%m-%d')
    
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
    
    def analyze_date(self, date: str) -> Dict:
        """Analyze data for a specific date"""
        result = {
            'date': date,
            'games_found': 0,
            'games_with_predictions': 0,
            'games_with_betting_lines': 0,
            'prediction_coverage': 0.0,
            'betting_line_coverage': 0.0
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
        
        # Count games
        game_ids = set()
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            if game_id:
                game_ids.add(game_id)
        
        result['games_found'] = len(game_ids)
        self.stats['games_found'] += len(game_ids)
        
        # If no games, skip further analysis
        if not game_ids:
            return result
        
        # Check for predictions
        games_with_predictions = set()
        date_predictions = predictions.get(date, {})
        if isinstance(date_predictions, dict):
            for pred_id, prediction in date_predictions.items():
                if not isinstance(prediction, dict):
                    continue
                    
                pred_game_id = str(prediction.get('game_id', ''))
                if pred_game_id in game_ids:
                    games_with_predictions.add(pred_game_id)
        
        result['games_with_predictions'] = len(games_with_predictions)
        self.stats['games_with_predictions'] += len(games_with_predictions)
        
        # Check for betting lines
        games_with_betting_lines = set()
        date_lines = betting_lines.get(date, {})
        if isinstance(date_lines, dict):
            for line_id, line_data in date_lines.items():
                if not isinstance(line_data, dict):
                    continue
                    
                line_game_id = str(line_data.get('game_id', ''))
                if line_game_id in game_ids:
                    games_with_betting_lines.add(line_game_id)
        
        result['games_with_betting_lines'] = len(games_with_betting_lines)
        self.stats['games_with_betting_lines'] += len(games_with_betting_lines)
        
        # Calculate coverage percentages
        if game_ids:
            result['prediction_coverage'] = round(len(games_with_predictions) / len(game_ids) * 100, 1)
            result['betting_line_coverage'] = round(len(games_with_betting_lines) / len(game_ids) * 100, 1)
        
        return result
    
    def analyze_date_range(self, start_date: str, end_date: str = None) -> Dict:
        """Analyze data for a range of dates"""
        date_range = self.get_date_range(start_date, end_date)
        
        logger.info(f"Analyzing {len(date_range)} dates from {date_range[0]} to {date_range[-1]}")
        
        date_results = []
        
        for date in date_range:
            result = self.analyze_date(date)
            date_results.append(result)
            self.stats['dates_analyzed'] += 1
        
        # Calculate overall coverage
        if self.stats['games_found'] > 0:
            self.stats['prediction_coverage'] = round(self.stats['games_with_predictions'] / self.stats['games_found'] * 100, 1)
            self.stats['betting_line_coverage'] = round(self.stats['games_with_betting_lines'] / self.stats['games_found'] * 100, 1)
        
        # Generate report
        self.generate_report(date_results)
        
        return self.stats
    
    def generate_report(self, date_results: List[Dict]) -> None:
        """Generate a validation report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.root_dir, f"backfill_validation_{timestamp}.txt")
        
        with open(report_path, 'w') as f:
            f.write(f"=== MLB Data Backfill Validation Report ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Overall Statistics:\n")
            f.write(f"Dates analyzed: {self.stats['dates_analyzed']}\n")
            f.write(f"Total games: {self.stats['games_found']}\n")
            f.write(f"Games with predictions: {self.stats['games_with_predictions']} ({self.stats['prediction_coverage']}%)\n")
            f.write(f"Games with betting lines: {self.stats['games_with_betting_lines']} ({self.stats['betting_line_coverage']}%)\n\n")
            
            f.write(f"Date-by-Date Analysis:\n")
            f.write(f"{'Date':<12} {'Games':<7} {'Predictions':<12} {'Coverage':<10} {'Betting':<9} {'Coverage':<10}\n")
            f.write(f"{'-'*60}\n")
            
            for result in date_results:
                date = result['date']
                games = result['games_found']
                preds = result['games_with_predictions']
                pred_cov = result['prediction_coverage']
                bets = result['games_with_betting_lines']
                bet_cov = result['betting_line_coverage']
                
                f.write(f"{date:<12} {games:<7} {preds:<12} {pred_cov:<10.1f}% {bets:<9} {bet_cov:<10.1f}%\n")
        
        # Also save as JSON for programmatic use
        json_report = {
            'timestamp': datetime.now().isoformat(),
            'overall': self.stats,
            'dates': date_results
        }
        
        json_report_path = os.path.join(self.root_dir, f"backfill_validation_{timestamp}.json")
        with open(json_report_path, 'w') as f:
            json.dump(json_report, f, indent=2)
        
        logger.info(f"Validation report written to {report_path}")
        logger.info(f"JSON report written to {json_report_path}")
        
        print(f"\nReport written to {os.path.basename(report_path)}")
        
def main():
    """Main function to run the validation"""
    start_date = "2025-08-07"
    end_date = None  # Today by default
    
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    print(f"=== MLB Backfill Validation ===")
    if start_date and end_date:
        print(f"Date range: {start_date} to {end_date}")
    elif start_date:
        print(f"From date: {start_date} to today")
    else:
        print("Using default date range: Aug 7 to today")
        
    validator = BackfillValidator()
    stats = validator.analyze_date_range(start_date, end_date)
    
    print("\n=== Validation Complete ===")
    print(f"Dates analyzed: {stats['dates_analyzed']}")
    print(f"Total games: {stats['games_found']}")
    print(f"Games with predictions: {stats['games_with_predictions']} ({stats['prediction_coverage']}%)")
    print(f"Games with betting lines: {stats['games_with_betting_lines']} ({stats['betting_line_coverage']}%)")
    
    return stats['prediction_coverage'] == 100.0 and stats['betting_line_coverage'] == 100.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
