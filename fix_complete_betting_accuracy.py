#!/usr/bin/env python3
"""
Fix Missing Aug 10 Predictions
===============================

Integrate Aug 10 predictions from archaeological file into unified cache
and recalculate betting accuracy with proper date logic.
"""

import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def integrate_aug_10_predictions():
    """Integrate Aug 10 predictions from archaeological file"""
    
    logger.info("🔍 Loading files to integrate Aug 10 predictions...")
    
    # Load archaeological file
    try:
        with open('archaeological_treasure_fixed.json', 'r') as f:
            archaeological_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading archaeological file: {e}")
        return False
    
    # Load unified cache
    try:
        with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
            unified_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading unified cache: {e}")
        return False
    
    # Extract Aug 10 predictions from archaeological file
    aug_10_predictions = {}
    for key, value in archaeological_data.items():
        if isinstance(value, dict) and value.get('date') == '2025-08-10':
            # Convert to standard format
            away_team = value.get('away_team', '')
            home_team = value.get('home_team', '')
            game_key = f"{away_team} @ {home_team}"
            
            aug_10_predictions[game_key] = {
                'away_team': away_team,
                'home_team': home_team,
                'predicted_away_score': float(value.get('predicted_away_score', 0)),
                'predicted_home_score': float(value.get('predicted_home_score', 0)),
                'predicted_total_runs': float(value.get('predicted_total_runs', 0)),
                'away_win_probability': float(value.get('away_win_probability', 0.5)),
                'home_win_probability': float(value.get('home_win_probability', 0.5)),
                'away_pitcher': value.get('away_pitcher', 'TBD'),
                'home_pitcher': value.get('home_pitcher', 'TBD')
            }
    
    logger.info(f"Found {len(aug_10_predictions)} Aug 10 predictions to integrate")
    
    # Add Aug 10 to unified cache
    unified_data['predictions_by_date']['2025-08-10'] = {
        'date': '2025-08-10',
        'games_count': len(aug_10_predictions),
        'last_updated': datetime.now().isoformat(),
        'games': aug_10_predictions
    }
    
    # Update metadata
    unified_data['metadata']['last_updated'] = datetime.now().isoformat()
    unified_data['metadata']['aug_10_integrated'] = True
    unified_data['metadata']['aug_10_integration_date'] = datetime.now().isoformat()
    unified_data['metadata']['aug_10_games_added'] = len(aug_10_predictions)
    
    # Save updated unified cache
    with open('MLB-Betting/data/unified_predictions_cache.json', 'w') as f:
        json.dump(unified_data, f, indent=2)
    
    logger.info(f"✅ Integrated {len(aug_10_predictions)} Aug 10 predictions into unified cache")
    return True

def calculate_complete_betting_accuracy():
    """Calculate betting accuracy with proper date logic (exclude current day)"""
    
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
    
    # Get current date for logic
    current_date = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"Current date: {current_date} - excluding from analysis")
    
    # Initialize counters
    total_predictions = 0
    winner_correct = 0
    total_correct = 0  # O/U 9.5 correct
    perfect_games = 0
    unmatched_predictions = []
    matched_games = []
    
    # Common betting line for totals
    betting_line = 9.5
    
    def normalize_team_name(team_name):
        """Enhanced team name normalization"""
        if not team_name:
            return ""
        
        name = team_name.replace('_', ' ').strip().lower()
        
        team_mappings = {
            'athletics': 'oakland athletics',
            'angels': 'los angeles angels',
            'diamondbacks': 'arizona diamondbacks',
            'dodgers': 'los angeles dodgers',
            'padres': 'san diego padres',
            'giants': 'san francisco giants',
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
        
        normalized = team_mappings.get(name, name)
        return normalized.title()
    
    logger.info("📊 Analyzing prediction accuracy with complete data...")
    
    # Process each date in our predictions
    for date_str, date_data in predictions_data.get('predictions_by_date', {}).items():
        # Skip current date (today)
        if date_str == current_date:
            logger.info(f"Skipping current date {date_str} as games may not be completed")
            continue
            
        if 'games' not in date_data:
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
            
            # Find matching real game
            matching_real_game = None
            for real_game in real_games:
                real_away = normalize_team_name(real_game.get('away_team', ''))
                real_home = normalize_team_name(real_game.get('home_team', ''))
                
                pred_away_norm = normalize_team_name(pred_away)
                pred_home_norm = normalize_team_name(pred_home)
                
                if pred_away_norm == real_away and pred_home_norm == real_home:
                    matching_real_game = real_game
                    break
            
            if not matching_real_game:
                # Try partial matching
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
        'current_date_excluded': current_date,
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
    
    logger.info("📈 COMPLETE BETTING ACCURACY RESULTS:")
    logger.info(f"Current Date Excluded: {current_date}")
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
    
    logger.info("💾 Complete analysis saved to data/betting_accuracy_analysis.json")
    
    return results

def main():
    """Main function"""
    logger.info("🎯 Complete MLB Prediction Accuracy Analysis Starting")
    
    # Step 1: Integrate Aug 10 predictions
    if integrate_aug_10_predictions():
        logger.info("✅ Aug 10 predictions integrated successfully")
        
        # Step 2: Calculate complete accuracy
        results = calculate_complete_betting_accuracy()
        
        if results:
            logger.info("✅ Complete betting accuracy analysis finished!")
            
            # Display key metrics
            bp = results['betting_performance']
            logger.info(f"\n🏆 FINAL COMPLETE RESULTS:")
            logger.info(f"📊 Games Analyzed: {results['total_predictions_analyzed']}")
            logger.info(f"🎯 Winner Accuracy: {bp['winner_predictions_correct']}/{results['total_predictions_analyzed']} ({bp['winner_accuracy_pct']}%)")
            logger.info(f"📈 Total Accuracy: {bp['total_predictions_correct']}/{results['total_predictions_analyzed']} ({bp['total_accuracy_pct']}%)")
            logger.info(f"⭐ Perfect Games: {bp['perfect_games']}/{results['total_predictions_analyzed']} ({bp['perfect_games_pct']}%)")
            logger.info(f"🗓️ Current Date Excluded: {results['current_date_excluded']}")
        else:
            logger.error("❌ Failed to complete analysis")
    else:
        logger.error("❌ Failed to integrate Aug 10 predictions")

if __name__ == "__main__":
    main()
