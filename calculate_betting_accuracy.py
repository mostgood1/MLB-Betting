#!/usr/bin/env python3
"""
MLB Prediction Accuracy Calculator
=================================

Compares our predictions against real MLB game results to calculate
accurate betting performance statistics.
"""

import json
import logging
from datetime import datetime
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_team_name(team_name):
    """Normalize team names for consistent matching"""
    if not team_name:
        return ""
    
    # Remove underscores and normalize spacing
    name = team_name.replace('_', ' ').strip()
    
    # Handle common variations
    name_mappings = {
        'Athletics': 'Oakland Athletics',
        'Oakland Athletics': 'Athletics',  # MLB API sometimes uses short form
        'Padres': 'San Diego Padres',
        'Angels': 'Los Angeles Angels',
        'Dodgers': 'Los Angeles Dodgers'
    }
    
    return name_mappings.get(name, name)

def load_predictions():
    """Load our prediction data"""
    try:
        with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading predictions: {e}")
        return None

def load_real_results():
    """Load real MLB game results"""
    try:
        with open('data/mlb_historical_results_2025.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading real results: {e}")
        return None

def calculate_betting_accuracy():
    """Calculate our betting accuracy against real results"""
    
    logger.info("🔍 Loading prediction and real result data...")
    
    predictions_data = load_predictions()
    results_data = load_real_results()
    
    if not predictions_data or not results_data:
        logger.error("Failed to load data files")
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
    
    logger.info("📊 Analyzing prediction accuracy...")
    
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
            
            pred_away = normalize_team_name(prediction.get('away_team', ''))
            pred_home = normalize_team_name(prediction.get('home_team', ''))
            
            # Find matching real game
            matching_real_game = None
            for real_game in real_games:
                real_away = normalize_team_name(real_game.get('away_team', ''))
                real_home = normalize_team_name(real_game.get('home_team', ''))
                
                if (pred_away.lower() == real_away.lower() and 
                    pred_home.lower() == real_home.lower()):
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
        'detailed_games': matched_games
    }
    
    logger.info("📈 BETTING ACCURACY RESULTS:")
    logger.info(f"Total Predictions Analyzed: {total_predictions}")
    logger.info(f"Winner Predictions Correct: {winner_correct} ({winner_accuracy_pct}%)")
    logger.info(f"Total Predictions Correct: {total_correct} ({total_accuracy_pct}%)")
    logger.info(f"Perfect Games: {perfect_games} ({perfect_games_pct}%)")
    logger.info(f"Unmatched Predictions: {len(unmatched_predictions)}")
    
    if unmatched_predictions:
        logger.info("Unmatched predictions:")
        for unmatched in unmatched_predictions[:5]:  # Show first 5
            logger.info(f"  - {unmatched}")
    
    # Save detailed results
    with open('data/betting_accuracy_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("💾 Detailed analysis saved to data/betting_accuracy_analysis.json")
    
    return results

def main():
    """Main function"""
    logger.info("🎯 MLB Prediction Accuracy Calculator Starting")
    
    results = calculate_betting_accuracy()
    
    if results:
        logger.info("✅ Betting accuracy analysis complete!")
        
        # Display key metrics
        bp = results['betting_performance']
        logger.info(f"\n🏆 FINAL RESULTS:")
        logger.info(f"📊 Games Analyzed: {results['total_predictions_analyzed']}")
        logger.info(f"🎯 Winner Accuracy: {bp['winner_predictions_correct']}/{results['total_predictions_analyzed']} ({bp['winner_accuracy_pct']}%)")
        logger.info(f"📈 Total Accuracy: {bp['total_predictions_correct']}/{results['total_predictions_analyzed']} ({bp['total_accuracy_pct']}%)")
        logger.info(f"⭐ Perfect Games: {bp['perfect_games']}/{results['total_predictions_analyzed']} ({bp['perfect_games_pct']}%)")
    else:
        logger.error("❌ Failed to complete analysis")

if __name__ == "__main__":
    main()
