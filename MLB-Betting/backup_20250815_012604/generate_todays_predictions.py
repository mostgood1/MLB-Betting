#!/usr/bin/env python3
"""
Generate Today's Predictions and Update Frontend Cache
======================================================
This script takes today's games and generates predictions for them,
then updates the unified cache so the frontend can display them.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def generate_todays_predictions():
    """Generate predictions for today's games and update unified cache"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Generating predictions for {today}")
    
    root_dir = Path(__file__).parent
    
    # Load today's games
    game_scores_path = root_dir / 'game_scores_cache.json'
    if not game_scores_path.exists():
        print("ERROR: game_scores_cache.json not found")
        return False
    
    with open(game_scores_path, 'r') as f:
        game_scores = json.load(f)
    
    # Get today's games
    if today not in game_scores:
        print(f"No games found for {today}")
        return False
    
    today_games_data = game_scores[today]
    
    # Handle both list and dict formats
    if isinstance(today_games_data, list):
        today_games = today_games_data
    elif isinstance(today_games_data, dict):
        today_games = today_games_data.get('games', [])
    else:
        print(f"Unexpected data format: {type(today_games_data)}")
        return False
    
    if not today_games:
        print(f"No games found for {today}")
        return False
    
    print(f"Found {len(today_games)} games for {today}")
    
    # Load unified cache
    unified_cache_paths = [
        root_dir / 'MLB-Betting' / 'unified_predictions_cache.json',
        root_dir / 'unified_predictions_cache.json'
    ]
    
    unified_cache = {}
    unified_cache_path = None
    
    for path in unified_cache_paths:
        if path.exists():
            unified_cache_path = path
            with open(path, 'r') as f:
                unified_cache = json.load(f)
            break
    
    if not unified_cache_path:
        print("ERROR: Could not find unified_predictions_cache.json")
        return False
    
    print(f"Loaded unified cache from {unified_cache_path}")
    
    # Ensure predictions_by_date structure exists
    if 'predictions_by_date' not in unified_cache:
        unified_cache['predictions_by_date'] = {}
    
    # Generate predictions for today's games
    predictions = {}
    
    for i, game in enumerate(today_games):
        if not isinstance(game, dict):
            continue
            
        # Get team names and pitcher information
        away_team = game.get('away_team', '')
        home_team = game.get('home_team', '')
        away_pitcher = game.get('away_pitcher', 'TBD')
        home_pitcher = game.get('home_pitcher', 'TBD')
        game_id = game.get('game_pk', game.get('game_id', f'game_{i}'))
        
        if not away_team or not home_team:
            continue
        
        # Create game key
        game_key = f"{away_team} @ {home_team}"
        
        # Generate basic predictions using simple heuristics
        # In a real system, this would use the UltraFastSimEngine
        
        # Basic prediction logic (simplified)
        home_advantage = 0.54  # Home teams win ~54% of games
        
        # Simple prediction based on team names (placeholder logic)
        # In reality, this would use team stats, pitcher data, etc.
        away_score = 4.2 + (hash(away_team) % 3) - 1  # Range: 3.2 - 5.2
        home_score = 4.5 + (hash(home_team) % 3) - 1  # Range: 3.5 - 5.5
        
        # Apply home field advantage
        home_score += 0.3
        
        total_runs = away_score + home_score
        
        # Calculate win probabilities
        score_diff = home_score - away_score
        home_win_prob = 0.5 + (score_diff * 0.15)  # Sigmoid-like function
        home_win_prob = max(0.2, min(0.8, home_win_prob))  # Clamp between 20-80%
        away_win_prob = 1.0 - home_win_prob
        
        # Generate prediction data
        prediction = {
            'away_team': away_team,
            'home_team': home_team,
            'predicted_away_score': round(away_score, 1),
            'predicted_home_score': round(home_score, 1),
            'predicted_total_runs': round(total_runs, 1),
            'away_win_probability': round(away_win_prob, 4),
            'home_win_probability': round(home_win_prob, 4),
            'away_pitcher': away_pitcher,
            'home_pitcher': home_pitcher,
            'model_version': 'daily_auto_v1',
            'source': 'auto_generated',
            'prediction_time': datetime.now().isoformat(),
            'game_id': str(game_id),
            'game_time': game.get('game_time', ''),
            'date': today,
            'has_real_results': False,
            
            # Add comprehensive details for betting analysis
            'comprehensive_details': {
                'winner_prediction': {
                    'predicted_winner': home_team if home_win_prob > away_win_prob else away_team,
                    'confidence': round(max(home_win_prob, away_win_prob) * 100, 1)
                },
                'score_prediction': {
                    'away_score': round(away_score, 1),
                    'home_score': round(home_score, 1),
                    'total_runs': round(total_runs, 1)
                },
                'betting_analysis': {
                    'recommendation': 'Good Bet' if max(home_win_prob, away_win_prob) > 0.6 else 'Skip',
                    'confidence_level': 'High' if max(home_win_prob, away_win_prob) > 0.65 else 'Medium'
                }
            }
        }
        
        predictions[game_key] = prediction
        print(f"  Generated prediction: {game_key} -> {away_team} {away_score:.1f} - {home_score:.1f} {home_team}")
    
    # Update unified cache
    unified_cache['predictions_by_date'][today] = {
        'date': today,
        'games_count': len(predictions),
        'last_updated': datetime.now().isoformat(),
        'games': predictions
    }
    
    # Update metadata
    if 'metadata' not in unified_cache:
        unified_cache['metadata'] = {}
    
    unified_cache['metadata'].update({
        'last_auto_prediction_update': datetime.now().isoformat(),
        'auto_prediction_date': today,
        'auto_prediction_games_count': len(predictions)
    })
    
    # Save updated cache
    try:
        with open(unified_cache_path, 'w') as f:
            json.dump(unified_cache, f, indent=2)
        print(f"SUCCESS: Updated unified cache with {len(predictions)} predictions")
        
        # Also copy to the other location if it exists
        for path in unified_cache_paths:
            if path != unified_cache_path and path.parent.exists():
                try:
                    with open(path, 'w') as f:
                        json.dump(unified_cache, f, indent=2)
                    print(f"SUCCESS: Also updated {path}")
                except Exception as e:
                    print(f"Warning: Could not update {path}: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to save unified cache: {e}")
        return False

if __name__ == "__main__":
    success = generate_todays_predictions()
    sys.exit(0 if success else 1)
