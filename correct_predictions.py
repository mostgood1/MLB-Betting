#!/usr/bin/env python3
"""
Corrected Prediction System - Aligns with Real Market Data
==========================================================
This script fixes the inverted predictions and aligns with real betting markets
"""

import json
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def odds_to_probability(moneyline):
    """Convert moneyline odds to implied probability"""
    if isinstance(moneyline, str):
        moneyline = int(moneyline.replace('+', '').replace('-', ''))
    
    if moneyline > 0:  # Underdog (+164)
        return 100 / (moneyline + 100)
    else:  # Favorite (-196)
        return abs(moneyline) / (abs(moneyline) + 100)

def get_starting_pitchers():
    """Get real starting pitchers for today"""
    today = '2025-08-15'
    url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&hydrate=team,probablePitcher'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        pitchers = {}
        for game in data['dates'][0]['games']:
            away_team = game['teams']['away']['team']['name']
            home_team = game['teams']['home']['team']['name']
            game_key = f"{away_team} @ {home_team}"
            
            away_pitcher = 'TBD'
            home_pitcher = 'TBD'
            
            if 'probablePitcher' in game['teams']['away']:
                away_pitcher = game['teams']['away']['probablePitcher']['fullName']
            if 'probablePitcher' in game['teams']['home']:
                home_pitcher = game['teams']['home']['probablePitcher']['fullName']
            
            pitchers[game_key] = {
                'away_pitcher': away_pitcher,
                'home_pitcher': home_pitcher
            }
        
        return pitchers
    except Exception as e:
        logging.error(f"Error fetching starting pitchers: {e}")
        return {}

def correct_predictions():
    """Correct predictions to align with real market data"""
    
    # Load real betting lines
    with open('MLB-Betting/data/real_betting_lines_2025_08_15.json', 'r') as f:
        betting_data = json.load(f)
    
    # Load unified cache
    with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
        cache = json.load(f)
    
    # Get real starting pitchers
    pitchers = get_starting_pitchers()
    
    corrected_games = []
    
    for game_key, line_data in betting_data['lines'].items():
        logging.info(f"🔧 Correcting prediction for {game_key}")
        
        # Extract market probabilities from moneyline
        away_odds = line_data['moneyline']['away']
        home_odds = line_data['moneyline']['home']
        
        away_prob = odds_to_probability(away_odds)
        home_prob = odds_to_probability(home_odds)
        
        # Normalize probabilities to sum to 1
        total_prob = away_prob + home_prob
        away_prob_normalized = away_prob / total_prob
        home_prob_normalized = home_prob / total_prob
        
        # Get real starting pitchers
        game_pitchers = pitchers.get(game_key, {'away_pitcher': 'TBD', 'home_pitcher': 'TBD'})
        
        # Calculate scores based on market probabilities
        # Higher probability team should score more
        total_runs = line_data['total_runs']['line']
        
        if home_prob_normalized > away_prob_normalized:
            # Home team favored
            home_score = total_runs * 0.55  # Home team gets 55% of runs
            away_score = total_runs * 0.45
        else:
            # Away team favored
            away_score = total_runs * 0.55
            home_score = total_runs * 0.45
        
        corrected_prediction = {
            'game': game_key,
            'corrected_away_win_probability': round(away_prob_normalized, 3),
            'corrected_home_win_probability': round(home_prob_normalized, 3),
            'corrected_away_score': round(away_score, 1),
            'corrected_home_score': round(home_score, 1),
            'corrected_total_runs': total_runs,
            'market_moneyline_away': away_odds,
            'market_moneyline_home': home_odds,
            'away_pitcher': game_pitchers['away_pitcher'],
            'home_pitcher': game_pitchers['home_pitcher'],
            'correction_time': datetime.now().isoformat()
        }
        
        corrected_games.append(corrected_prediction)
        
        logging.info(f"  Market: Away {away_odds} | Home {home_odds}")
        logging.info(f"  Probabilities: Away {away_prob_normalized:.1%} | Home {home_prob_normalized:.1%}")
        logging.info(f"  Scores: Away {away_score:.1f} | Home {home_score:.1f}")
    
    # Save corrected predictions
    corrected_data = {
        'correction_date': datetime.now().isoformat(),
        'source': 'Market-aligned corrections',
        'total_games': len(corrected_games),
        'corrections': corrected_games
    }
    
    with open('corrected_predictions_2025_08_15.json', 'w') as f:
        json.dump(corrected_data, f, indent=2)
    
    logging.info(f"✅ Corrected {len(corrected_games)} predictions")
    
    # Update unified cache with corrected predictions
    update_unified_cache(cache, corrected_games)

def update_unified_cache(cache, corrected_games):
    """Update the unified cache with corrected predictions"""
    
    if '2025-08-15' not in cache['predictions_by_date']:
        logging.error("Date 2025-08-15 not found in cache")
        return
    
    for correction in corrected_games:
        game_key = correction['game']
        
        if game_key in cache['predictions_by_date']['2025-08-15']['games']:
            # Update the cached prediction
            game_data = cache['predictions_by_date']['2025-08-15']['games'][game_key]
            
            game_data['predicted_away_score'] = correction['corrected_away_score']
            game_data['predicted_home_score'] = correction['corrected_home_score']
            game_data['predicted_total_runs'] = correction['corrected_total_runs']
            game_data['away_win_probability'] = correction['corrected_away_win_probability']
            game_data['home_win_probability'] = correction['corrected_home_win_probability']
            game_data['away_pitcher'] = correction['away_pitcher']
            game_data['home_pitcher'] = correction['home_pitcher']
            game_data['market_corrected'] = True
            game_data['market_correction_time'] = correction['correction_time']
            
            # Update comprehensive details
            if game_data['away_win_probability'] > game_data['home_win_probability']:
                winner = game_data['away_team']
                confidence = round(game_data['away_win_probability'] * 100, 1)
            else:
                winner = game_data['home_team'] 
                confidence = round(game_data['home_win_probability'] * 100, 1)
            
            game_data['comprehensive_details']['winner_prediction'] = {
                'predicted_winner': winner,
                'confidence': confidence
            }
            
            game_data['comprehensive_details']['score_prediction'] = {
                'away_score': correction['corrected_away_score'],
                'home_score': correction['corrected_home_score'],
                'total_runs': correction['corrected_total_runs']
            }
            
            logging.info(f"✅ Updated cache for {game_key}")
    
    # Update metadata
    cache['metadata']['last_market_correction'] = datetime.now().isoformat()
    cache['metadata']['market_corrected_games'] = len(corrected_games)
    
    # Save updated cache
    with open('MLB-Betting/data/unified_predictions_cache.json', 'w') as f:
        json.dump(cache, f, indent=2)
    
    logging.info("✅ Unified cache updated with corrected predictions")

if __name__ == "__main__":
    logging.info("🔧 Starting prediction correction system...")
    correct_predictions()
    logging.info("✅ Prediction correction complete!")
