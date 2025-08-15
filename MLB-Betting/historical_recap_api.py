#!/usr/bin/env python3
"""
Enhanced Historical Recap API Extension

This file contains additional API endpoints to provide comprehensive
historical recaps with both predictions and actual results.
"""

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Team code mapping for historical predictions
TEAM_CODE_MAPPING = {
    'ATH': 'Athletics', 'BAL': 'Baltimore Orioles', 'BOS': 'Boston Red Sox',
    'CWS': 'Chicago White Sox', 'CLE': 'Cleveland Guardians', 'DET': 'Detroit Tigers',
    'HOU': 'Houston Astros', 'KC': 'Kansas City Royals', 'LAA': 'Los Angeles Angels',
    'MIN': 'Minnesota Twins', 'NYY': 'New York Yankees', 'OAK': 'Oakland Athletics',
    'SEA': 'Seattle Mariners', 'TB': 'Tampa Bay Rays', 'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays', 'ARI': 'Arizona Diamondbacks', 'ATL': 'Atlanta Braves',
    'CHC': 'Chicago Cubs', 'CIN': 'Cincinnati Reds', 'COL': 'Colorado Rockies',
    'LAD': 'Los Angeles Dodgers', 'MIA': 'Miami Marlins', 'MIL': 'Milwaukee Brewers',
    'NYM': 'New York Mets', 'PHI': 'Philadelphia Phillies', 'PIT': 'Pittsburgh Pirates',
    'SD': 'San Diego Padres', 'SF': 'San Francisco Giants', 'STL': 'St. Louis Cardinals',
    'WSN': 'Washington Nationals'
}

def convert_team_code_to_name(code):
    """Convert team code to full team name"""
    return TEAM_CODE_MAPPING.get(code, code)

def add_historical_recap_endpoints(app: Flask, prediction_engine=None):
    """Add enhanced historical recap endpoints to the Flask app"""
    
    @app.route('/api/historical-recap/<date>')
    def get_historical_recap(date):
        """Get complete historical recap for a specific date with predictions and results"""
        try:
            print(f"Processing historical recap request for date: {date}")
            print(f"__file__ is: {__file__}")
            print(f"os.path.dirname(__file__) is: {os.path.dirname(__file__)}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Load the data files with better path handling
            script_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"Script directory: {script_dir}")
            
            game_scores_path = os.path.join(script_dir, '..', 'game_scores_cache.json')
            daily_predictions_path = os.path.join(script_dir, 'data', 'daily_predictions_cache.json')
            historical_predictions_path = os.path.join(script_dir, '..', 'historical_predictions_cache.json')
            
            print(f"Game scores path: {game_scores_path} (exists: {os.path.exists(game_scores_path)})")
            print(f"Daily predictions path: {daily_predictions_path} (exists: {os.path.exists(daily_predictions_path)})")
            print(f"Historical predictions path: {historical_predictions_path} (exists: {os.path.exists(historical_predictions_path)})")
            
            # Load game results
            game_results = []
            if os.path.exists(game_scores_path):
                with open(game_scores_path, 'r') as f:
                    scores_data = json.load(f)
                    if date in scores_data:
                        game_results = scores_data[date].get('games', [])
            
            print(f"Found {len(game_results)} game results for {date}")
            
            # Load predictions - prioritize unified cache
            game_predictions = {}
            unified_predictions_path = os.path.join(script_dir, '..', 'unified_predictions_cache.json')
            
            # Try unified cache first
            if os.path.exists(unified_predictions_path):
                try:
                    with open(unified_predictions_path, 'r') as f:
                        unified_data = json.load(f)
                    
                    print(f"📊 Loaded unified predictions cache")
                    
                    # Get predictions for the requested date
                    predictions_by_date = unified_data.get('predictions_by_date', {})
                    if date in predictions_by_date:
                        date_data = predictions_by_date[date]
                        games_data = date_data.get('games', {})
                        
                        print(f"   Found {len(games_data)} unified predictions for {date}")
                        
                        for matchup_key, prediction_data in games_data.items():
                            if isinstance(prediction_data, dict):
                                away_team = prediction_data.get('away_team', '')
                                home_team = prediction_data.get('home_team', '')
                                
                                if away_team and home_team:
                                    game_key = f"{away_team.replace(' ', '_')} @ {home_team.replace(' ', '_')}"
                                    game_predictions[game_key] = {
                                        'prediction': {
                                            'away_team': away_team.replace(' ', '_'),
                                            'home_team': home_team.replace(' ', '_'),
                                            'predicted_away_score': prediction_data.get('predicted_away_score'),
                                            'predicted_home_score': prediction_data.get('predicted_home_score'),
                                            'predicted_total_runs': prediction_data.get('predicted_total_runs'),
                                            'away_win_probability': prediction_data.get('away_win_probability'),
                                            'home_win_probability': prediction_data.get('home_win_probability'),
                                            'away_pitcher': prediction_data.get('away_pitcher', 'TBD'),
                                            'home_pitcher': prediction_data.get('home_pitcher', 'TBD'),
                                            'model_version': prediction_data.get('model_version', 'unified'),
                                            'source': prediction_data.get('source', 'unified_cache'),
                                            'prediction_time': prediction_data.get('prediction_time'),
                                            'simulation_count': prediction_data.get('simulation_count')
                                        }
                                    }
                        
                        print(f"   ✅ Loaded {len(game_predictions)} unified predictions")
                    else:
                        print(f"   ⚠️ No unified predictions found for {date}")
                        
                except Exception as e:
                    print(f"   ❌ Error loading unified predictions: {e}")
            
            # Fallback: Load predictions from daily cache (for recent dates)
            if not game_predictions and os.path.exists(daily_predictions_path):
                with open(daily_predictions_path, 'r') as f:
                    preds_data = json.load(f)
                    date_data = preds_data.get(date, {})
                    if 'games' in date_data:
                        game_predictions = date_data['games']
                        print(f"   ✅ Loaded {len(game_predictions)} daily predictions (fallback)")
            
            # Fallback: Load predictions from historical cache (for older dates)
            if not game_predictions and os.path.exists(historical_predictions_path):
                with open(historical_predictions_path, 'r') as f:
                    hist_data = json.load(f)
                    if date in hist_data:
                        date_data = hist_data[date]
                        
                        # Handle cached_predictions format (older structure)
                        if 'cached_predictions' in date_data:
                            cached_preds = date_data['cached_predictions']
                            for team_key, team_data in cached_preds.items():
                                if '@' in team_key and 'predictions' in team_data:
                                    away_code = team_data.get('away_team', '')
                                    home_code = team_data.get('home_team', '')
                                    
                                    # Convert team codes to full names
                                    away_team = convert_team_code_to_name(away_code)
                                    home_team = convert_team_code_to_name(home_code)
                                    
                                    # If codes weren't converted, try extracting from full name keys
                                    if away_team == away_code and len(away_code) <= 3:
                                        for full_key in cached_preds.keys():
                                            if ' @ ' in full_key:
                                                parts = full_key.split(' @ ')
                                                if len(parts) == 2:
                                                    away_team = parts[0]
                                                    home_team = parts[1]
                                                    break
                                    
                                    preds = team_data['predictions']
                                    game_key = f"{away_team.replace(' ', '_')} @ {home_team.replace(' ', '_')}"
                                    game_predictions[game_key] = {
                                        'prediction': {
                                            'away_team': away_team.replace(' ', '_'),
                                            'home_team': home_team.replace(' ', '_'),
                                            'predicted_away_score': preds.get('predicted_away_score'),
                                            'predicted_home_score': preds.get('predicted_home_score'),
                                            'predicted_total_runs': preds.get('predicted_total_runs'),
                                            'away_win_probability': preds.get('away_win_prob'),
                                            'home_win_probability': preds.get('home_win_prob'),
                                            'away_pitcher': 'TBD',
                                            'home_pitcher': 'TBD',
                                            'model_version': 'historical',
                                            'source': 'historical_cache'
                                        }
                                    }
                        
                        # Handle backfill format (newer structure)
                        else:
                            backfill_keys = [k for k in date_data.keys() if k.startswith('backfill_')]
                            for backfill_key in backfill_keys:
                                backfill_data = date_data[backfill_key]
                                if isinstance(backfill_data, dict):
                                    away_team = backfill_data.get('away_team', '')
                                    home_team = backfill_data.get('home_team', '')
                                    
                                    if away_team and home_team:
                                        game_key = f"{away_team.replace(' ', '_')} @ {home_team.replace(' ', '_')}"
                                        game_predictions[game_key] = {
                                            'prediction': {
                                                'away_team': away_team.replace(' ', '_'),
                                                'home_team': home_team.replace(' ', '_'),
                                                'predicted_away_score': backfill_data.get('predicted_away_score'),
                                                'predicted_home_score': backfill_data.get('predicted_home_score'),
                                                'predicted_total_runs': backfill_data.get('predicted_total_runs'),
                                                'away_win_probability': backfill_data.get('away_win_pct'),
                                                'home_win_probability': backfill_data.get('home_win_pct'),
                                                'away_pitcher': backfill_data.get('away_pitcher', 'TBD'),
                                                'home_pitcher': backfill_data.get('home_pitcher', 'TBD'),
                                                'model_version': backfill_data.get('model_version', 'backfill'),
                                                'source': 'historical_backfill'
                                            }
                                        }
            
            # Helper function to normalize team names for matching
            def normalize_team_name(name):
                return name.replace(' ', '_') if name else ''
            
            # Create lookup for predictions by team matchup
            predictions_lookup = {}
            
            for pred_key, pred_data in game_predictions.items():
                if 'prediction' in pred_data:
                    pred = pred_data['prediction']
                    # Extract team names from prediction data
                    away_team = pred.get('away_team', '')
                    home_team = pred.get('home_team', '')
                    
                    # For unified cache data, team names are already clean (no underscores)
                    # For legacy data, remove underscores if present
                    away_team_clean = away_team.replace('_', ' ')
                    home_team_clean = home_team.replace('_', ' ')
                    
                    # Create normalized lookup key (results use spaces, so normalize to underscores)
                    away_norm = normalize_team_name(away_team_clean)
                    home_norm = normalize_team_name(home_team_clean)
                    matchup_key = f"{away_norm}@{home_norm}"
                    predictions_lookup[matchup_key] = pred
                    
                    # Also create a direct lookup with clean names for debugging
                    clean_key = f"{away_team_clean}@{home_team_clean}"
                    predictions_lookup[clean_key] = pred
            
            # Combine predictions and results
            recap_games = []
            
            # Process game results and try to match with predictions
            for result in game_results:
                away_team = result.get('away_team', '')
                home_team = result.get('home_team', '')
                
                # Try multiple matching strategies
                away_norm = normalize_team_name(away_team)
                home_norm = normalize_team_name(home_team)
                matchup_key = f"{away_norm}@{home_norm}"
                clean_key = f"{away_team}@{home_team}"
                
                # Try normalized key first, then clean key
                prediction = predictions_lookup.get(matchup_key) or predictions_lookup.get(clean_key, {})
                
                recap_game = {
                    'game_id': result.get('game_pk', f"{away_norm}@{home_norm}"),
                    'away_team': away_team,
                    'home_team': home_team,
                    'has_prediction': bool(prediction),
                    'has_result': bool(result),
                    'is_complete_recap': bool(prediction and result)
                }
                
                # Add prediction data
                if prediction:
                    recap_game['prediction'] = {
                        'away_win_probability': prediction.get('away_win_probability', 0),
                        'home_win_probability': prediction.get('home_win_probability', 0),
                        'predicted_away_score': prediction.get('predicted_away_score'),
                        'predicted_home_score': prediction.get('predicted_home_score'),
                        'predicted_total_runs': prediction.get('predicted_total_runs'),
                        'away_pitcher': prediction.get('away_pitcher', 'TBD'),
                        'home_pitcher': prediction.get('home_pitcher', 'TBD'),
                        'prediction_time': prediction.get('prediction_time'),
                        'model_version': prediction.get('model_version', 'cached'),
                        'source': prediction.get('source', 'daily_cache')
                    }
                
                # Add result data
                if result:
                    recap_game['result'] = {
                        'status': result.get('status', 'Unknown'),
                        'is_final': result.get('is_final', False),
                        'away_score': result.get('away_score'),
                        'home_score': result.get('home_score'),
                        'total_score': result.get('total_score'),
                        'winning_team': result.get('winning_team'),
                        'score_differential': result.get('score_differential'),
                        'game_time': result.get('game_time'),
                        'data_source': result.get('data_source', 'MLB API')
                    }
                    
                    # Add performance analysis if both prediction and result exist
                    if prediction and result.get('is_final'):
                        recap_game['performance_analysis'] = analyze_prediction_performance(prediction, result)
                
                recap_games.append(recap_game)
            
            # Also check for predictions that don't have matching results
            for pred_key, pred_data in game_predictions.items():
                if 'prediction' in pred_data:
                    pred = pred_data['prediction']
                    # Extract and clean team names
                    away_team_orig = pred.get('away_team', '')
                    home_team_orig = pred.get('home_team', '')
                    away_team = away_team_orig.replace('_', ' ')
                    home_team = home_team_orig.replace('_', ' ')
                    
                    # Check if we already processed this game
                    already_processed = any(
                        g['away_team'] == away_team and g['home_team'] == home_team 
                        for g in recap_games
                    )
                    
                    if not already_processed:
                        away_norm = normalize_team_name(away_team)
                        home_norm = normalize_team_name(home_team)
                        recap_game = {
                            'game_id': f"{away_norm}@{home_norm}",
                            'away_team': away_team,
                            'home_team': home_team,
                            'has_prediction': True,
                            'has_result': False,
                            'is_complete_recap': False,
                            'prediction': {
                                'away_win_probability': pred.get('away_win_probability', 0),
                                'home_win_probability': pred.get('home_win_probability', 0),
                                'predicted_away_score': pred.get('predicted_away_score'),
                                'predicted_home_score': pred.get('predicted_home_score'),
                                'predicted_total_runs': pred.get('predicted_total_runs'),
                                'away_pitcher': pred.get('away_pitcher', 'TBD'),
                                'home_pitcher': pred.get('home_pitcher', 'TBD'),
                                'prediction_time': pred.get('prediction_time'),
                                'model_version': pred.get('model_version', 'cached'),
                                'source': pred.get('source', 'daily_cache')
                            }
                        }
                        recap_games.append(recap_game)
            
            # Sort by game time or alphabetically
            recap_games.sort(key=lambda x: f"{x['away_team']}_{x['home_team']}")
            
            # Calculate summary statistics
            total_games = len(recap_games)
            complete_recaps = sum(1 for game in recap_games if game['is_complete_recap'])
            final_games = sum(1 for game in recap_games if game.get('result', {}).get('is_final', False))
            
            return jsonify({
                'success': True,
                'date': date,
                'summary': {
                    'total_games': total_games,
                    'complete_recaps': complete_recaps,
                    'final_games': final_games,
                    'completion_rate': round((complete_recaps / total_games * 100), 1) if total_games > 0 else 0
                },
                'games': recap_games
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/historical-recap-range')
    def get_historical_recap_range():
        """Get historical recaps for a date range"""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if not start_date or not end_date:
                return jsonify({
                    'success': False,
                    'error': 'start_date and end_date parameters required'
                }), 400
            
            # Generate date range
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                return jsonify({
                    'success': False,
                    'error': 'start_date must be before end_date'
                }), 400
            
            date_range = []
            current = start
            while current <= end:
                date_range.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
            
            # Get recaps for each date
            all_recaps = {}
            total_games = 0
            total_complete = 0
            
            for date in date_range:
                # Make internal call to get_historical_recap
                with app.test_request_context(f'/api/historical-recap/{date}'):
                    recap_response = get_historical_recap(date)
                    
                if recap_response.status_code == 200:
                    recap_data = recap_response.get_json()
                    if recap_data['success']:
                        all_recaps[date] = recap_data
                        total_games += recap_data['summary']['total_games']
                        total_complete += recap_data['summary']['complete_recaps']
            
            return jsonify({
                'success': True,
                'date_range': {
                    'start': start_date,
                    'end': end_date,
                    'total_dates': len(date_range)
                },
                'summary': {
                    'total_games': total_games,
                    'complete_recaps': total_complete,
                    'overall_completion_rate': round((total_complete / total_games * 100), 1) if total_games > 0 else 0
                },
                'daily_recaps': all_recaps
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/performance-analytics/<date>')
    def get_performance_analytics(date):
        """Get detailed performance analytics for predictions on a specific date"""
        try:
            # Get the historical recap data first
            recap_response = get_historical_recap(date)
            recap_data = recap_response.get_json()
            
            if not recap_data['success']:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get historical recap data'
                }), 400
            
            games = recap_data.get('games', [])
            complete_games = [g for g in games if g.get('is_complete_recap', False)]
            
            # Initialize analytics
            analytics = {
                'date': date,
                'summary': {
                    'total_games': len(games),
                    'analyzed_games': len(complete_games),
                    'analysis_rate': round((len(complete_games) / len(games) * 100), 1) if len(games) > 0 else 0
                },
                'winner_performance': {
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'accuracy_rate': 0,
                    'by_confidence': {
                        'high': {'total': 0, 'correct': 0, 'accuracy': 0},
                        'medium': {'total': 0, 'correct': 0, 'accuracy': 0},
                        'low': {'total': 0, 'correct': 0, 'accuracy': 0}
                    }
                },
                'score_performance': {
                    'total_games': 0,
                    'avg_away_diff': 0,
                    'avg_home_diff': 0,
                    'avg_total_diff': 0,
                    'score_grades': {'A+': 0, 'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 'C+': 0, 'C': 0, 'C-': 0, 'D+': 0, 'D': 0}
                },
                'betting_performance': {
                    'spread_excellent': 0,
                    'spread_good': 0,
                    'spread_fair': 0,
                    'spread_poor': 0,
                    'total_excellent': 0,
                    'total_good': 0,
                    'total_fair': 0,
                    'total_poor': 0
                },
                'grade_distribution': {
                    'A+': 0, 'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 
                    'C+': 0, 'C': 0, 'C-': 0, 'D+': 0, 'D': 0
                },
                'detailed_games': []
            }
            
            # Analyze each complete game
            away_diffs = []
            home_diffs = []
            total_diffs = []
            
            for game in complete_games:
                if 'performance_analysis' in game:
                    perf = game['performance_analysis']
                    
                    # Winner performance
                    if perf.get('winner_prediction') != 'Unknown':
                        analytics['winner_performance']['total_predictions'] += 1
                        if perf.get('winner_correct', False):
                            analytics['winner_performance']['correct_predictions'] += 1
                        
                        # By confidence level
                        confidence = perf.get('confidence_level', 'low').lower()
                        if confidence in analytics['winner_performance']['by_confidence']:
                            analytics['winner_performance']['by_confidence'][confidence]['total'] += 1
                            if perf.get('winner_correct', False):
                                analytics['winner_performance']['by_confidence'][confidence]['correct'] += 1
                    
                    # Score performance
                    score_acc = perf.get('score_accuracy', {})
                    if score_acc:
                        analytics['score_performance']['total_games'] += 1
                        
                        if 'away_diff' in score_acc:
                            away_diffs.append(score_acc['away_diff'])
                        if 'home_diff' in score_acc:
                            home_diffs.append(score_acc['home_diff'])
                        if 'total_diff' in score_acc:
                            total_diffs.append(score_acc['total_diff'])
                    
                    # Betting performance
                    betting = perf.get('betting_outcomes', {})
                    if 'spread_performance' in betting:
                        spread_key = f"spread_{betting['spread_performance'].lower()}"
                        if spread_key in analytics['betting_performance']:
                            analytics['betting_performance'][spread_key] += 1
                    
                    if 'total_performance' in betting:
                        total_key = f"total_{betting['total_performance'].lower()}"
                        if total_key in analytics['betting_performance']:
                            analytics['betting_performance'][total_key] += 1
                    
                    # Grade distribution
                    grade = perf.get('overall_grade', 'D')
                    if grade in analytics['grade_distribution']:
                        analytics['grade_distribution'][grade] += 1
                    
                    # Add to detailed games
                    analytics['detailed_games'].append({
                        'matchup': f"{game.get('away_team', 'Away')} @ {game.get('home_team', 'Home')}",
                        'predicted_winner': perf.get('winner_prediction', 'Unknown'),
                        'actual_winner': perf.get('winner_actual', 'Unknown'),
                        'winner_correct': perf.get('winner_correct', False),
                        'confidence': perf.get('confidence_level', 'Unknown'),
                        'overall_grade': perf.get('overall_grade', 'N/A'),
                        'grade_percentage': perf.get('grade_percentage', 0),
                        'score_diffs': {
                            'away': score_acc.get('away_diff'),
                            'home': score_acc.get('home_diff'),
                            'total': score_acc.get('total_diff')
                        }
                    })
            
            # Calculate averages and rates
            if analytics['winner_performance']['total_predictions'] > 0:
                analytics['winner_performance']['accuracy_rate'] = round(
                    (analytics['winner_performance']['correct_predictions'] / 
                     analytics['winner_performance']['total_predictions']) * 100, 1
                )
            
            # Calculate confidence-based accuracy rates
            for conf_level in analytics['winner_performance']['by_confidence']:
                conf_data = analytics['winner_performance']['by_confidence'][conf_level]
                if conf_data['total'] > 0:
                    conf_data['accuracy'] = round((conf_data['correct'] / conf_data['total']) * 100, 1)
            
            # Calculate score averages
            if away_diffs:
                analytics['score_performance']['avg_away_diff'] = round(sum(away_diffs) / len(away_diffs), 2)
            if home_diffs:
                analytics['score_performance']['avg_home_diff'] = round(sum(home_diffs) / len(home_diffs), 2)
            if total_diffs:
                analytics['score_performance']['avg_total_diff'] = round(sum(total_diffs) / len(total_diffs), 2)
            
            # Calculate overall system grade
            total_games_with_grades = sum(analytics['grade_distribution'].values())
            if total_games_with_grades > 0:
                grade_points = {
                    'A+': 97.5, 'A': 92.5, 'A-': 87.5, 'B+': 82.5, 'B': 77.5, 'B-': 72.5,
                    'C+': 67.5, 'C': 62.5, 'C-': 57.5, 'D+': 52.5, 'D': 40
                }
                
                weighted_score = sum(
                    grade_points.get(grade, 0) * count 
                    for grade, count in analytics['grade_distribution'].items()
                )
                
                analytics['overall_system_grade'] = round(weighted_score / total_games_with_grades, 1)
                
                # Convert to letter grade
                if analytics['overall_system_grade'] >= 95:
                    analytics['overall_system_letter'] = 'A+'
                elif analytics['overall_system_grade'] >= 90:
                    analytics['overall_system_letter'] = 'A'
                elif analytics['overall_system_grade'] >= 85:
                    analytics['overall_system_letter'] = 'A-'
                elif analytics['overall_system_grade'] >= 80:
                    analytics['overall_system_letter'] = 'B+'
                elif analytics['overall_system_grade'] >= 75:
                    analytics['overall_system_letter'] = 'B'
                elif analytics['overall_system_grade'] >= 70:
                    analytics['overall_system_letter'] = 'B-'
                else:
                    analytics['overall_system_letter'] = 'C+'
            
            return jsonify({
                'success': True,
                'analytics': analytics
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

def analyze_prediction_performance(prediction: Dict, result: Dict) -> Dict:
    """Analyze how well the prediction performed against actual results"""
    analysis = {
        'winner_prediction': 'Unknown',
        'winner_actual': result.get('winning_team', 'Unknown'),
        'winner_correct': False,
        'confidence_level': 'Unknown',
        'score_prediction': {
            'away': prediction.get('predicted_away_score'),
            'home': prediction.get('predicted_home_score'),
            'total': prediction.get('predicted_total_runs')
        },
        'score_actual': {
            'away': result.get('away_score'),
            'home': result.get('home_score'),
            'total': result.get('total_score')
        },
        'score_accuracy': {},
        'betting_outcomes': {}
    }
    
    # Determine predicted winner and confidence
    away_prob = prediction.get('away_win_probability', 0) or 0
    home_prob = prediction.get('home_win_probability', 0) or 0
    
    # If probabilities are missing, try to infer from scores
    if away_prob == 0 and home_prob == 0:
        pred_away_score = prediction.get('predicted_away_score', 0) or 0
        pred_home_score = prediction.get('predicted_home_score', 0) or 0
        if pred_away_score > pred_home_score:
            analysis['winner_prediction'] = prediction.get('away_team', 'Away Team')
            analysis['confidence_level'] = 'Score-based'
        elif pred_home_score > pred_away_score:
            analysis['winner_prediction'] = prediction.get('home_team', 'Home Team')
            analysis['confidence_level'] = 'Score-based'
        else:
            analysis['winner_prediction'] = 'Tie/Close'
            analysis['confidence_level'] = 'Low'
    else:
        # Use probabilities
        if away_prob > home_prob:
            analysis['winner_prediction'] = prediction.get('away_team', 'Away Team')
            confidence_margin = away_prob - home_prob
        elif home_prob > away_prob:
            analysis['winner_prediction'] = prediction.get('home_team', 'Home Team')
            confidence_margin = home_prob - away_prob
        else:
            analysis['winner_prediction'] = 'Tie/Close'
            confidence_margin = 0
        
        # Determine confidence level
        if confidence_margin >= 0.3:
            analysis['confidence_level'] = 'High'
        elif confidence_margin >= 0.15:
            analysis['confidence_level'] = 'Medium'
        elif confidence_margin >= 0.05:
            analysis['confidence_level'] = 'Low'
        else:
            analysis['confidence_level'] = 'Very Low'
    
    # Check winner accuracy
    if analysis['winner_prediction'] != 'Unknown' and analysis['winner_actual'] != 'Unknown':
        # Normalize team names for comparison
        pred_winner_clean = analysis['winner_prediction'].replace('_', ' ')
        actual_winner_clean = analysis['winner_actual'].replace('_', ' ')
        analysis['winner_correct'] = (pred_winner_clean == actual_winner_clean)
    
    # Calculate score accuracy
    pred_away = prediction.get('predicted_away_score')
    pred_home = prediction.get('predicted_home_score')
    pred_total = prediction.get('predicted_total_runs')
    
    actual_away = result.get('away_score')
    actual_home = result.get('home_score')
    actual_total = result.get('total_score')
    
    if pred_away is not None and actual_away is not None:
        analysis['score_accuracy']['away_diff'] = abs(float(pred_away) - int(actual_away))
        analysis['score_accuracy']['away_accuracy'] = max(0, (100 - (analysis['score_accuracy']['away_diff'] * 20)) / 100)
    
    if pred_home is not None and actual_home is not None:
        analysis['score_accuracy']['home_diff'] = abs(float(pred_home) - int(actual_home))
        analysis['score_accuracy']['home_accuracy'] = max(0, (100 - (analysis['score_accuracy']['home_diff'] * 20)) / 100)
    
    if pred_total is not None and actual_total is not None:
        analysis['score_accuracy']['total_diff'] = abs(float(pred_total) - int(actual_total))
        analysis['score_accuracy']['total_accuracy'] = max(0, (100 - (analysis['score_accuracy']['total_diff'] * 10)) / 100)
    
    # Calculate betting performance
    if 'away_diff' in analysis['score_accuracy'] and 'home_diff' in analysis['score_accuracy']:
        avg_score_diff = (analysis['score_accuracy']['away_diff'] + analysis['score_accuracy']['home_diff']) / 2
        analysis['betting_outcomes']['spread_performance'] = 'Excellent' if avg_score_diff <= 1 else 'Good' if avg_score_diff <= 2 else 'Fair' if avg_score_diff <= 3 else 'Poor'
    
    if 'total_diff' in analysis['score_accuracy']:
        total_diff = analysis['score_accuracy']['total_diff']
        analysis['betting_outcomes']['total_performance'] = 'Excellent' if total_diff <= 1 else 'Good' if total_diff <= 2 else 'Fair' if total_diff <= 3 else 'Poor'
    
    # Calculate overall grade (improved scoring system)
    grade_points = 0
    grade_factors = 0
    
    # Winner prediction (50% of grade)
    if analysis['winner_correct']:
        if analysis['confidence_level'] == 'High':
            grade_points += 50
        elif analysis['confidence_level'] == 'Medium':
            grade_points += 45
        else:
            grade_points += 40
    else:
        # Partial credit for close games
        if analysis['confidence_level'] in ['Very Low', 'Low']:
            grade_points += 15  # Partial credit for uncertain predictions
    grade_factors += 50
    
    # Score accuracy (50% of grade)
    score_grade_points = 0
    score_factors = 0
    
    if 'total_diff' in analysis['score_accuracy']:
        total_diff = analysis['score_accuracy']['total_diff']
        if total_diff <= 0.5:
            score_grade_points += 25
        elif total_diff <= 1:
            score_grade_points += 20
        elif total_diff <= 2:
            score_grade_points += 15
        elif total_diff <= 3:
            score_grade_points += 10
        score_factors += 25
    
    if 'away_diff' in analysis['score_accuracy'] and 'home_diff' in analysis['score_accuracy']:
        avg_score_diff = (analysis['score_accuracy']['away_diff'] + analysis['score_accuracy']['home_diff']) / 2
        if avg_score_diff <= 0.5:
            score_grade_points += 25
        elif avg_score_diff <= 1:
            score_grade_points += 20
        elif avg_score_diff <= 2:
            score_grade_points += 15
        elif avg_score_diff <= 3:
            score_grade_points += 10
        score_factors += 25
    
    grade_points += score_grade_points
    grade_factors += score_factors
    
    # Calculate final grade
    if grade_factors > 0:
        grade_pct = (grade_points / grade_factors) * 100
        if grade_pct >= 95:
            grade = 'A+'
        elif grade_pct >= 90:
            grade = 'A'
        elif grade_pct >= 85:
            grade = 'A-'
        elif grade_pct >= 80:
            grade = 'B+'
        elif grade_pct >= 75:
            grade = 'B'
        elif grade_pct >= 70:
            grade = 'B-'
        elif grade_pct >= 65:
            grade = 'C+'
        elif grade_pct >= 60:
            grade = 'C'
        elif grade_pct >= 55:
            grade = 'C-'
        elif grade_pct >= 50:
            grade = 'D+'
        else:
            grade = 'D'
        
        analysis['overall_grade'] = grade
        analysis['grade_percentage'] = round(grade_pct / 100, 3)
        analysis['grade_breakdown'] = {
            'winner_points': grade_points - score_grade_points,
            'score_points': score_grade_points,
            'max_points': grade_factors
        }
    
    return analysis
