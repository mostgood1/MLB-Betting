#!/usr/bin/env python3
"""
MLB Data Inspector Script

This script analyzes data from August 7, 2025 to today (August 13, 2025) 
and identifies any gaps or inconsistencies in the MLB game data.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any

class MLBDataInspector:
    def __init__(self):
        """Initialize the MLB Data Inspector tool"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.team_strength_path = os.path.join(self.root_dir, 'team_strength_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        
        # Check for normalized_game_data.json in different possible locations
        utils_dir = os.path.join(self.root_dir, 'utils')
        if os.path.exists(utils_dir):
            self.normalized_game_path = os.path.join(utils_dir, 'normalized_game_data.json')
        else:
            utils_dir = os.path.join(self.root_dir, 'mlb-clean-deploy', 'utils')
            self.normalized_game_path = os.path.join(utils_dir, 'normalized_game_data.json')
        
        # Track stats
        self.stats = {
            'dates_analyzed': 0,
            'total_games': 0,
            'games_with_ids': 0,
            'games_with_pitchers': 0,
            'games_with_betting': 0,
            'games_with_predictions': 0,
            'duplicates': 0
        }
        
        # Track issues
        self.issues = []
        
        # Track games by date
        self.games_by_date = {}
        
        # Today's date
        self.today = datetime.now().strftime('%Y-%m-%d')
    
    def load_json_file(self, filepath: str) -> dict:
        """Load a JSON file with error handling"""
        if not os.path.exists(filepath):
            print(f"Warning: File not found - {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {str(e)}")
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
    
    def analyze_game_scores(self, date: str) -> Dict:
        """Analyze game_scores_cache.json for a specific date"""
        result = {
            'total': 0,
            'with_game_id': 0,
            'with_pitchers': 0,
            'duplicates': 0,
            'games': []
        }
        
        game_scores = self.load_json_file(self.game_scores_path)
        if not game_scores or date not in game_scores:
            return result
        
        # Get games data safely
        date_entry = game_scores.get(date, {})
        if not isinstance(date_entry, dict):
            return result
            
        games = date_entry.get('games', [])
        if not games or not isinstance(games, list):
            return result
        
        # Track games by ID to find duplicates
        games_by_id = {}
        
        for game in games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if not away_team or not home_team:
                continue
                
            result['total'] += 1
            
            # Check for game ID
            if game_id:
                result['with_game_id'] += 1
                
                # Check for duplicates
                if game_id in games_by_id:
                    result['duplicates'] += 1
                    self.issues.append({
                        'date': date,
                        'type': 'duplicate_game',
                        'game_id': game_id,
                        'away_team': away_team,
                        'home_team': home_team
                    })
                else:
                    games_by_id[game_id] = game
            else:
                self.issues.append({
                    'date': date,
                    'type': 'missing_game_id',
                    'away_team': away_team,
                    'home_team': home_team
                })
            
            # Check for pitcher information
            away_pitcher = game.get('away_pitcher', 'TBD')
            home_pitcher = game.get('home_pitcher', 'TBD')
            if away_pitcher != 'TBD' or home_pitcher != 'TBD':
                result['with_pitchers'] += 1
            else:
                self.issues.append({
                    'date': date,
                    'type': 'missing_pitchers',
                    'game_id': game_id,
                    'away_team': away_team,
                    'home_team': home_team
                })
            
            # Add to games list
            matchup = f"{away_team} @ {home_team}"
            result['games'].append({
                'id': game_id,
                'matchup': matchup,
                'away_pitcher': away_pitcher,
                'home_pitcher': home_pitcher
            })
        
        # Store games by date
        self.games_by_date[date] = result
        
        # Update stats
        self.stats['total_games'] += result['total']
        self.stats['games_with_ids'] += result['with_game_id']
        self.stats['games_with_pitchers'] += result['with_pitchers']
        self.stats['duplicates'] += result['duplicates']
        
        return result
    
    def analyze_historical_predictions(self, date: str) -> Dict:
        """Analyze historical_predictions_cache.json for a specific date"""
        result = {
            'total': 0,
            'with_game_id': 0,
            'missing_games': []
        }
        
        historical_predictions = self.load_json_file(self.historical_predictions_path)
        if not historical_predictions or date not in historical_predictions:
            return result
        
        date_predictions = historical_predictions.get(date, {})
        if not isinstance(date_predictions, dict):
            return result
        
        # Check for games from game_scores that are missing from predictions
        if date in self.games_by_date:
            game_scores_games = {g['matchup']: g['id'] for g in self.games_by_date[date]['games']}
            
            for pred_id, prediction in date_predictions.items():
                if not isinstance(prediction, dict):
                    continue
                    
                away_team = prediction.get('away_team', '')
                home_team = prediction.get('home_team', '')
                matchup = f"{away_team} @ {home_team}"
                
                result['total'] += 1
                
                # Check for game ID
                game_id = prediction.get('game_id', '')
                if game_id:
                    result['with_game_id'] += 1
                
                # Check if this prediction matches a game from game_scores
                if matchup in game_scores_games:
                    # Check if game IDs match
                    scores_game_id = game_scores_games[matchup]
                    if scores_game_id != game_id:
                        self.issues.append({
                            'date': date,
                            'type': 'mismatched_game_id',
                            'matchup': matchup,
                            'scores_id': scores_game_id,
                            'predictions_id': game_id
                        })
                    
                    # Remove from game_scores_games to track what's left
                    del game_scores_games[matchup]
                
            # Any remaining games in game_scores_games are missing from predictions
            for matchup, game_id in game_scores_games.items():
                result['missing_games'].append({
                    'matchup': matchup,
                    'game_id': game_id
                })
                
                self.issues.append({
                    'date': date,
                    'type': 'missing_prediction',
                    'matchup': matchup,
                    'game_id': game_id
                })
        
        # Update stats
        self.stats['games_with_predictions'] += result['with_game_id']
        
        return result
    
    def analyze_betting_lines(self, date: str) -> Dict:
        """Analyze historical_betting_lines_cache.json for a specific date"""
        result = {
            'total': 0,
            'with_game_id': 0,
            'missing_games': []
        }
        
        betting_lines = self.load_json_file(self.betting_lines_path)
        if not betting_lines or date not in betting_lines:
            return result
        
        date_lines = betting_lines.get(date, {})
        if not isinstance(date_lines, dict):
            return result
        
        # Check for games from game_scores that are missing from betting lines
        if date in self.games_by_date:
            game_scores_games = {g['matchup']: g['id'] for g in self.games_by_date[date]['games']}
            
            for line_id, line_data in date_lines.items():
                if not isinstance(line_data, dict):
                    continue
                    
                away_team = line_data.get('away_team', '')
                home_team = line_data.get('home_team', '')
                matchup = f"{away_team} @ {home_team}"
                
                result['total'] += 1
                
                # Check for game ID
                game_id = line_data.get('game_id', '')
                if game_id:
                    result['with_game_id'] += 1
                
                # Check if this line matches a game from game_scores
                if matchup in game_scores_games:
                    # Check if game IDs match
                    scores_game_id = game_scores_games[matchup]
                    if scores_game_id != game_id:
                        self.issues.append({
                            'date': date,
                            'type': 'mismatched_betting_id',
                            'matchup': matchup,
                            'scores_id': scores_game_id,
                            'betting_id': game_id
                        })
                    
                    # Remove from game_scores_games to track what's left
                    if matchup in game_scores_games:
                        del game_scores_games[matchup]
                
            # Any remaining games in game_scores_games are missing from betting lines
            for matchup, game_id in game_scores_games.items():
                result['missing_games'].append({
                    'matchup': matchup,
                    'game_id': game_id
                })
                
                self.issues.append({
                    'date': date,
                    'type': 'missing_betting_line',
                    'matchup': matchup,
                    'game_id': game_id
                })
        
        # Update stats
        self.stats['games_with_betting'] += result['with_game_id']
        
        return result
    
    def analyze_date(self, date: str) -> bool:
        """Analyze all data files for a specific date"""
        print(f"\nAnalyzing data for {date}...")
        
        # First analyze game scores to build reference
        game_scores = self.analyze_game_scores(date)
        print(f"  Game Scores: {game_scores['total']} games, {game_scores['with_game_id']} with IDs, {game_scores['with_pitchers']} with pitchers")
        
        # Then analyze predictions
        predictions = self.analyze_historical_predictions(date)
        print(f"  Predictions: {predictions['total']} predictions, {predictions['with_game_id']} with game IDs")
        if predictions['missing_games']:
            print(f"  Missing predictions for {len(predictions['missing_games'])} games")
        
        # Finally analyze betting lines
        betting = self.analyze_betting_lines(date)
        print(f"  Betting Lines: {betting['total']} lines, {betting['with_game_id']} with game IDs")
        if betting['missing_games']:
            print(f"  Missing betting lines for {len(betting['missing_games'])} games")
        
        self.stats['dates_analyzed'] += 1
        return True
    
    def analyze_date_range(self, start_date: str, end_date: str = None) -> Dict:
        """Analyze all data files for a range of dates"""
        date_range = self.get_date_range(start_date, end_date)
        
        print(f"=== MLB Data Analysis: {start_date} to {end_date or self.today} ===")
        print(f"Analyzing {len(date_range)} dates...")
        
        for date in date_range:
            self.analyze_date(date)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report of the analysis"""
        print("\n=== MLB Data Analysis Report ===")
        print(f"Dates analyzed: {self.stats['dates_analyzed']}")
        print(f"Total games: {self.stats['total_games']}")
        print(f"Games with IDs: {self.stats['games_with_ids']} ({self.stats['games_with_ids']/max(1, self.stats['total_games'])*100:.1f}%)")
        print(f"Games with pitcher info: {self.stats['games_with_pitchers']} ({self.stats['games_with_pitchers']/max(1, self.stats['total_games'])*100:.1f}%)")
        print(f"Games with predictions: {self.stats['games_with_predictions']} ({self.stats['games_with_predictions']/max(1, self.stats['total_games'])*100:.1f}%)")
        print(f"Games with betting lines: {self.stats['games_with_betting']} ({self.stats['games_with_betting']/max(1, self.stats['total_games'])*100:.1f}%)")
        print(f"Duplicates found: {self.stats['duplicates']}")
        
        if self.issues:
            print("\n=== Issues Found ===")
            issue_types = {}
            for issue in self.issues:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
            
            for issue_type, count in issue_types.items():
                print(f"{issue_type}: {count} occurrences")
            
            print("\nSample Issues (first 10):")
            for i, issue in enumerate(self.issues[:10]):
                print(f"  {i+1}. {issue['date']} - {issue['type']} - {issue.get('matchup') or issue.get('away_team', '') + ' @ ' + issue.get('home_team', '')}")
            
            # Save issues to file
            report_filename = f"data_gaps_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(report_filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'stats': self.stats,
                        'issues': self.issues
                    }, f, indent=2)
                print(f"\nFull issue report saved to: {report_filename}")
            except Exception as e:
                print(f"Error saving report: {str(e)}")
        else:
            print("\nNo issues found! Data looks complete and consistent.")
        
        return self.stats

def main():
    """Main function to run the MLB Data Inspector"""
    start_date = "2025-08-07"
    end_date = None  # Today by default
    
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    inspector = MLBDataInspector()
    inspector.analyze_date_range(start_date, end_date)

if __name__ == "__main__":
    main()
