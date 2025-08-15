#!/usr/bin/env python3
"""
MLB Game Recap Verification Script

This script verifies that all games from a specified date range have:
1. Predictions (pre-game analysis)
2. Final scores/results (post-game recap)
3. Comprehensive game data

Focus on ensuring complete "recaps" for historical analysis.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

class GameRecapVerifier:
    def __init__(self):
        """Initialize the Game Recap Verifier"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.historical_predictions_path = os.path.join(self.root_dir, 'historical_predictions_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
    
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
    
    def check_game_recap_completeness(self, date: str) -> Dict[str, Any]:
        """Check completeness of game recaps for a specific date"""
        result = {
            'date': date,
            'total_games': 0,
            'games_with_predictions': 0,
            'games_with_results': 0,
            'complete_recaps': 0,
            'incomplete_games': [],
            'missing_components': {
                'predictions_only': [],
                'results_only': [],
                'no_data': []
            }
        }
        
        # Load data files
        game_scores = self.load_json_file(self.game_scores_path)
        predictions = self.load_json_file(self.historical_predictions_path)
        
        # Check if date exists in either dataset
        has_scores = date in game_scores
        has_predictions = date in predictions
        
        if not has_scores and not has_predictions:
            print(f"No data found for {date}")
            return result
        
        # Collect all games from scores - use game_pk as primary key
        games_from_scores = {}
        if has_scores:
            date_entry = game_scores.get(date, {})
            if isinstance(date_entry, dict) and 'games' in date_entry:
                for game in date_entry['games']:
                    if isinstance(game, dict) and 'game_pk' in game:
                        game_id = str(game['game_pk'])
                        games_from_scores[game_id] = {
                            'game_id': game_id,
                            'away_team': game.get('away_team', 'Unknown'),
                            'home_team': game.get('home_team', 'Unknown'),
                            'status': game.get('status', 'Unknown'),
                            'is_final': game.get('is_final', False),
                            'away_score': game.get('away_score'),
                            'home_score': game.get('home_score'),
                            'winning_team': game.get('winning_team')
                        }
        
        # Collect all games from predictions
        games_from_predictions = {}
        team_matchups = {}  # Track matchups for alternate matching
        
        if has_predictions:
            date_predictions = predictions.get(date, {})
            if isinstance(date_predictions, dict):
                # Handle both old format (cached_predictions) and new format (direct)
                pred_data = {}
                
                # Merge cached_predictions if it exists
                if 'cached_predictions' in date_predictions:
                    pred_data.update(date_predictions['cached_predictions'])
                
                # Also include any backfill predictions (they start with 'backfill_' or 'focused_fix_')
                for key, value in date_predictions.items():
                    if (key.startswith('backfill_') or key.startswith('focused_fix_')) and isinstance(value, dict):
                        pred_data[key] = value
                
                # If no cached_predictions, assume everything is predictions
                if 'cached_predictions' not in date_predictions:
                    for key, value in date_predictions.items():
                        if key not in ['last_updated', 'backfilled'] and isinstance(value, dict):
                            pred_data[key] = value
                
                for key, pred in pred_data.items():
                    if isinstance(pred, dict):
                        # Extract game_id from key or prediction data
                        game_id = pred.get('game_id', '')
                        if not game_id and '_' in key:
                            # Try to extract from backfill key format
                            parts = key.split('_')
                            if len(parts) >= 3:
                                game_id = parts[-1]
                        
                        # Skip entries that don't have valid game IDs
                        if game_id and (game_id.isdigit() or len(game_id) > 6):
                            away_team = pred.get('away_team', 'Unknown')
                            home_team = pred.get('home_team', 'Unknown')
                            
                            games_from_predictions[str(game_id)] = {
                                'game_id': str(game_id),
                                'away_team': away_team,
                                'home_team': home_team,
                                'prediction_exists': True
                            }
                            
                            # Create matchup key for alternate matching
                            if away_team != 'Unknown' and home_team != 'Unknown':
                                matchup_key = f"{away_team}_{home_team}"
                                team_matchups[matchup_key] = str(game_id)
        
        # Try to match predictions to games by team matchups if direct ID match fails
        for score_game_id, score_game in games_from_scores.items():
            if score_game_id not in games_from_predictions:
                away = score_game['away_team']
                home = score_game['home_team']
                matchup_key = f"{away}_{home}"
                
                # Look for a prediction with matching teams
                for pred_id, pred_game in games_from_predictions.items():
                    if (pred_game['away_team'] == away and pred_game['home_team'] == home and 
                        pred_id not in [sg['game_id'] for sg in games_from_scores.values()]):
                        # Found a matching prediction - create alias
                        games_from_predictions[score_game_id] = pred_game.copy()
                        games_from_predictions[score_game_id]['game_id'] = score_game_id
                        break
        
        # Combine all unique games (prefer actual MLB game IDs)
        all_game_ids = set()
        
        # Add all game IDs from scores (these are authoritative MLB game PKs)
        for game_id in games_from_scores.keys():
            if game_id.isdigit():
                all_game_ids.add(game_id)
        
        # Add prediction-only games that don't have matches
        for pred_id in games_from_predictions.keys():
            if pred_id not in games_from_scores and pred_id.isdigit():
                all_game_ids.add(pred_id)
        
        result['total_games'] = len(all_game_ids)
        
        # Analyze each game
        for game_id in all_game_ids:
            has_prediction = game_id in games_from_predictions
            has_result = game_id in games_from_scores
            
            if has_prediction:
                result['games_with_predictions'] += 1
            if has_result:
                result['games_with_results'] += 1
            
            # Determine completeness
            if has_prediction and has_result:
                result['complete_recaps'] += 1
                # Check if result is actually final
                game_data = games_from_scores[game_id]
                if not game_data.get('is_final', False):
                    result['incomplete_games'].append({
                        'game_id': game_id,
                        'issue': 'Game not final',
                        'matchup': f"{game_data.get('away_team', 'Unknown')} @ {game_data.get('home_team', 'Unknown')}",
                        'status': game_data.get('status', 'Unknown')
                    })
            else:
                # Add to incomplete list
                game_info = games_from_scores.get(game_id, games_from_predictions.get(game_id, {}))
                matchup = f"{game_info.get('away_team', 'Unknown')} @ {game_info.get('home_team', 'Unknown')}"
                
                incomplete_entry = {
                    'game_id': game_id,
                    'matchup': matchup
                }
                
                if has_prediction and not has_result:
                    result['missing_components']['results_only'].append(incomplete_entry)
                elif has_result and not has_prediction:
                    result['missing_components']['predictions_only'].append(incomplete_entry)
                else:
                    result['missing_components']['no_data'].append(incomplete_entry)
        
        return result
    
    def generate_recap_report(self, start_date: str, end_date: str) -> str:
        """Generate a comprehensive recap completeness report"""
        print(f"\n=== MLB Game Recap Verification Report ===")
        print(f"Date Range: {start_date} to {end_date}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Generate date range
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        date_range = []
        current = start
        while current <= end:
            date_range.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        # Analyze each date
        all_results = {}
        total_games = 0
        total_complete = 0
        total_predictions = 0
        total_results = 0
        
        for date in date_range:
            print(f"\nAnalyzing {date}...")
            result = self.check_game_recap_completeness(date)
            all_results[date] = result
            
            total_games += result['total_games']
            total_complete += result['complete_recaps']
            total_predictions += result['games_with_predictions']
            total_results += result['games_with_results']
            
            # Print daily summary
            if result['total_games'] > 0:
                completeness_pct = (result['complete_recaps'] / result['total_games']) * 100
                print(f"  {result['total_games']} games, {result['complete_recaps']} complete recaps ({completeness_pct:.1f}%)")
                
                if result['incomplete_games']:
                    print(f"  Issues: {len(result['incomplete_games'])} games with problems")
            else:
                print(f"  No games scheduled")
        
        # Generate summary report
        print(f"\n=== SUMMARY ===")
        print(f"Total Games: {total_games}")
        print(f"Games with Predictions: {total_predictions} ({(total_predictions/total_games)*100:.1f}%)" if total_games > 0 else "Games with Predictions: 0")
        print(f"Games with Results: {total_results} ({(total_results/total_games)*100:.1f}%)" if total_games > 0 else "Games with Results: 0")
        print(f"Complete Recaps: {total_complete} ({(total_complete/total_games)*100:.1f}%)" if total_games > 0 else "Complete Recaps: 0")
        
        # Identify problems
        problem_summary = {
            'missing_predictions': [],
            'missing_results': [],
            'non_final_games': []
        }
        
        for date, result in all_results.items():
            for game in result['missing_components']['results_only']:
                problem_summary['missing_predictions'].append(f"{date}: {game['matchup']} (ID: {game['game_id']})")
            
            for game in result['missing_components']['predictions_only']:
                problem_summary['missing_results'].append(f"{date}: {game['matchup']} (ID: {game['game_id']})")
            
            for game in result['incomplete_games']:
                if 'not final' in game.get('issue', '').lower():
                    problem_summary['non_final_games'].append(f"{date}: {game['matchup']} (ID: {game['game_id']}) - {game.get('status', 'Unknown')}")
        
        if any(problem_summary.values()):
            print(f"\n=== ISSUES FOUND ===")
            
            if problem_summary['missing_results']:
                print(f"\nMissing Results ({len(problem_summary['missing_results'])}):")
                for issue in problem_summary['missing_results'][:10]:  # Show first 10
                    print(f"  {issue}")
                if len(problem_summary['missing_results']) > 10:
                    print(f"  ... and {len(problem_summary['missing_results']) - 10} more")
            
            if problem_summary['missing_predictions']:
                print(f"\nMissing Predictions ({len(problem_summary['missing_predictions'])}):")
                for issue in problem_summary['missing_predictions'][:10]:  # Show first 10
                    print(f"  {issue}")
                if len(problem_summary['missing_predictions']) > 10:
                    print(f"  ... and {len(problem_summary['missing_predictions']) - 10} more")
            
            if problem_summary['non_final_games']:
                print(f"\nNon-Final Games ({len(problem_summary['non_final_games'])}):")
                for issue in problem_summary['non_final_games']:
                    print(f"  {issue}")
        else:
            print(f"\n✅ ALL GAMES HAVE COMPLETE RECAPS!")
            print("All games in the specified date range have both predictions and final results.")
        
        return all_results

def main():
    """Main function"""
    # Default date range: August 7-13, 2025
    start_date = "2025-08-07"
    end_date = "2025-08-13"
    
    # Allow command line arguments
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    verifier = GameRecapVerifier()
    results = verifier.generate_recap_report(start_date, end_date)
    
    # Save detailed results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"game_recap_verification_{timestamp}.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {report_path}")

if __name__ == "__main__":
    main()
