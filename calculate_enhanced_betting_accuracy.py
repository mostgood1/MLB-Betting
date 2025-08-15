#!/usr/bin/env python3
"""
Enhanced MLB Prediction Accuracy Calculator
===========================================

Improved team name matching to get all 97 games matched properly.
"""

import json
import logging
from datetime import datetime
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_team_name(team_name):
    """Enhanced team name normalization for better matching"""
    if not team_name:
        return ""
    
    # Remove underscores and normalize spacing
    name = team_name.replace('_', ' ').strip().lower()
    
    # Create comprehensive mapping for team name variations
    team_mappings = {
        # Athletics variations
        'athletics': 'oakland athletics',
        'oakland athletics': 'oakland athletics',
        'a\'s': 'oakland athletics',
        
        # Angels variations  
        'angels': 'los angeles angels',
        'los angeles angels': 'los angeles angels',
        'la angels': 'los angeles angels',
        
        # Diamondbacks variations
        'diamondbacks': 'arizona diamondbacks',
        'arizona diamondbacks': 'arizona diamondbacks',
        'd-backs': 'arizona diamondbacks',
        
        # Dodgers variations
        'dodgers': 'los angeles dodgers',
        'los angeles dodgers': 'los angeles dodgers',
        'la dodgers': 'los angeles dodgers',
        
        # Padres variations
        'padres': 'san diego padres',
        'san diego padres': 'san diego padres',
        
        # Giants variations
        'giants': 'san francisco giants',
        'san francisco giants': 'san francisco giants',
        'sf giants': 'san francisco giants',
        
        # Common short name variations
        'yankees': 'new york yankees',
        'mets': 'new york mets', 
        'cubs': 'chicago cubs',
        'white sox': 'chicago white sox',
        'red sox': 'boston red sox',
        'blue jays': 'toronto blue jays',
        'phillies': 'philadelphia phillies',
        'nationals': 'washington nationals',
        'marlins': 'miami marlins',
        'braves': 'atlanta braves',
        'orioles': 'baltimore orioles',
        'rays': 'tampa bay rays',
        'guardians': 'cleveland guardians',
        'tigers': 'detroit tigers',
        'twins': 'minnesota twins',
        'astros': 'houston astros',
        'rangers': 'texas rangers',
        'mariners': 'seattle mariners',
        'royals': 'kansas city royals',
        'brewers': 'milwaukee brewers',
        'cardinals': 'st. louis cardinals',
        'reds': 'cincinnati reds',
        'pirates': 'pittsburgh pirates',
        'rockies': 'colorado rockies'
    }
    
    # Apply mapping
    normalized = team_mappings.get(name, name)
    
    # Return with proper capitalization
    return normalized.title()

def find_best_team_match(pred_team, real_games):
    """Find the best matching team from real games"""
    pred_normalized = normalize_team_name(pred_team).lower()
    
    best_match = None
    best_score = 0
    
    for game in real_games:
        away_team = normalize_team_name(game.get('away_team', '')).lower()
        home_team = normalize_team_name(game.get('home_team', '')).lower()
        
        # Exact match
        if pred_normalized == away_team or pred_normalized == home_team:
            return game, away_team if pred_normalized == away_team else home_team
        
        # Partial match scoring
        for team in [away_team, home_team]:
            score = 0
            pred_words = pred_normalized.split()
            team_words = team.split()
            
            for word in pred_words:
                if word in team_words:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = (game, team)
    
    return best_match if best_score > 0 else (None, None)

def calculate_enhanced_betting_accuracy():
    """Enhanced calculation with better team matching"""
    
    logger.info("🔍 Loading prediction and real result data...")
    
    # Load data
    try:
        with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
            predictions_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading predictions: {e}")
        return None
    
    try:
        with open('data/mlb_historical_results_2025.json', 'r') as f:
            results_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading real results: {e}")
        return None
    
    # Initialize counters
    total_predictions = 0
    winner_correct = 0
    total_correct = 0  # O/U 9.5 correct
    perfect_games = 0
    unmatched_predictions = []
    matched_games = []
    
    # Common betting line for totals
    betting_line = 9.5
    
    logger.info("📊 Analyzing prediction accuracy with enhanced matching...")
    
    # Process each date in our predictions
    for date_str, date_data in predictions_data.get('predictions_by_date', {}).items():
        if 'games' not in date_data:
            continue
            
        # Skip dates before Aug 7
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj < datetime(2025, 8, 7):
                continue
        except:
            continue
        
        # Get real results for this date
        real_games = results_data.get('games_by_date', {}).get(date_str, {}).get('games', [])
        if not real_games:
            logger.info(f"No real results found for {date_str}")
            continue
        
        # Process our predictions for this date
        games = date_data['games']
        if isinstance(games, dict):
            games_list = list(games.values())
        else:
            games_list = games
        
        logger.info(f"Processing {date_str}: {len(games_list)} predictions, {len(real_games)} real results")
        
        for prediction in games_list:
            if not isinstance(prediction, dict):
                continue
            
            pred_away = prediction.get('away_team', '')
            pred_home = prediction.get('home_team', '')
            
            # Try exact matching first
            matching_real_game = None
            for real_game in real_games:
                real_away = normalize_team_name(real_game.get('away_team', ''))
                real_home = normalize_team_name(real_game.get('home_team', ''))
                
                if (normalize_team_name(pred_away) == real_away and 
                    normalize_team_name(pred_home) == real_home):
                    matching_real_game = real_game
                    break
            
            # If no exact match, try enhanced matching
            if not matching_real_game:
                # Check if away team matches any team in real games
                away_match, away_team = find_best_team_match(pred_away, real_games)
                home_match, home_team = find_best_team_match(pred_home, real_games)
                
                # Find a game with both teams
                for real_game in real_games:
                    real_away = normalize_team_name(real_game.get('away_team', '')).lower()
                    real_home = normalize_team_name(real_game.get('home_team', '')).lower()
                    
                    pred_away_norm = normalize_team_name(pred_away).lower()
                    pred_home_norm = normalize_team_name(pred_home).lower()
                    
                    if ((pred_away_norm in real_away or real_away in pred_away_norm) and
                        (pred_home_norm in real_home or real_home in pred_home_norm)):
                        matching_real_game = real_game
                        break
            
            if not matching_real_game:
                unmatched_predictions.append(f"{pred_away} @ {pred_home} on {date_str}")
                continue
            
            # We have a match! Calculate accuracy
            total_predictions += 1
            
            # Get predicted values
            pred_away_score = float(prediction.get('predicted_away_score', 0))
            pred_home_score = float(prediction.get('predicted_home_score', 0))
            pred_total_runs = float(prediction.get('predicted_total_runs', pred_away_score + pred_home_score))
            
            # Get actual values
            actual_away_score = float(matching_real_game.get('away_score', 0))
            actual_home_score = float(matching_real_game.get('home_score', 0))
            actual_total_runs = float(matching_real_game.get('total_runs', actual_away_score + actual_home_score))
            
            # Check winner prediction
            predicted_winner = 'away' if pred_away_score > pred_home_score else 'home'
            actual_winner = 'away' if actual_away_score > actual_home_score else 'home'
            winner_is_correct = (predicted_winner == actual_winner)
            
            # Check total prediction (O/U 9.5)
            predicted_over_under = 'over' if pred_total_runs > betting_line else 'under'
            actual_over_under = 'over' if actual_total_runs > betting_line else 'under'
            total_is_correct = (predicted_over_under == actual_over_under)
            
            # Perfect game = both correct
            is_perfect = winner_is_correct and total_is_correct
            
            # Update counters
            if winner_is_correct:
                winner_correct += 1
            if total_is_correct:
                total_correct += 1
            if is_perfect:
                perfect_games += 1
            
            # Store for detailed analysis
            game_analysis = {
                'date': date_str,
                'away_team': pred_away,
                'home_team': pred_home,
                'predicted_score': f"{pred_away_score}-{pred_home_score}",
                'actual_score': f"{actual_away_score}-{actual_home_score}",
                'predicted_total': pred_total_runs,
                'actual_total': actual_total_runs,
                'winner_correct': winner_is_correct,
                'total_correct': total_is_correct,
                'perfect_game': is_perfect
            }
            matched_games.append(game_analysis)
    
    # Calculate percentages
    winner_accuracy_pct = round((winner_correct / total_predictions * 100), 1) if total_predictions > 0 else 0
    total_accuracy_pct = round((total_correct / total_predictions * 100), 1) if total_predictions > 0 else 0
    perfect_games_pct = round((perfect_games / total_predictions * 100), 1) if total_predictions > 0 else 0
    
    # Results summary
    results = {
        'analysis_date': datetime.now().isoformat(),
        'total_predictions_analyzed': total_predictions,
        'betting_performance': {
            'winner_predictions_correct': winner_correct,
            'winner_accuracy_pct': winner_accuracy_pct,
            'total_predictions_correct': total_correct,
            'total_accuracy_pct': total_accuracy_pct,
            'perfect_games': perfect_games,
            'perfect_games_pct': perfect_games_pct
        },
        'unmatched_predictions': len(unmatched_predictions),
        'unmatched_details': unmatched_predictions,
        'detailed_games': matched_games
    }
    
    logger.info("📈 ENHANCED BETTING ACCURACY RESULTS:")
    logger.info(f"Total Predictions Analyzed: {total_predictions}")
    logger.info(f"Winner Predictions Correct: {winner_correct} ({winner_accuracy_pct}%)")
    logger.info(f"Total Predictions Correct: {total_correct} ({total_accuracy_pct}%)")
    logger.info(f"Perfect Games: {perfect_games} ({perfect_games_pct}%)")
    logger.info(f"Unmatched Predictions: {len(unmatched_predictions)}")
    
    if unmatched_predictions:
        logger.info("Remaining unmatched predictions:")
        for unmatched in unmatched_predictions:
            logger.info(f"  - {unmatched}")
    
    # Save detailed results
    with open('data/betting_accuracy_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("💾 Enhanced analysis saved to data/betting_accuracy_analysis.json")
    
    return results

def main():
    """Main function"""
    logger.info("🎯 Enhanced MLB Prediction Accuracy Calculator Starting")
    
    results = calculate_enhanced_betting_accuracy()
    
    if results:
        logger.info("✅ Enhanced betting accuracy analysis complete!")
        
        # Display key metrics
        bp = results['betting_performance']
        logger.info(f"\n🏆 FINAL ENHANCED RESULTS:")
        logger.info(f"📊 Games Analyzed: {results['total_predictions_analyzed']}")
        logger.info(f"🎯 Winner Accuracy: {bp['winner_predictions_correct']}/{results['total_predictions_analyzed']} ({bp['winner_accuracy_pct']}%)")
        logger.info(f"📈 Total Accuracy: {bp['total_predictions_correct']}/{results['total_predictions_analyzed']} ({bp['total_accuracy_pct']}%)")
        logger.info(f"⭐ Perfect Games: {bp['perfect_games']}/{results['total_predictions_analyzed']} ({bp['perfect_games_pct']}%)")
        logger.info(f"🔄 Match Rate: {results['total_predictions_analyzed']}/{results['total_predictions_analyzed'] + results['unmatched_predictions']} games")
    else:
        logger.error("❌ Failed to complete analysis")

if __name__ == "__main__":
    main()
