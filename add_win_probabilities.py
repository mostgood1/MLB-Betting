import json
import math
from datetime import datetime

def calculate_win_probability(away_score, home_score):
    """Calculate win probabilities based on predicted scores"""
    if away_score is None or home_score is None:
        return None, None
    
    # Simple model: higher score gets higher probability
    # Add some variance to make it more realistic
    score_diff = home_score - away_score
    
    # Convert score difference to probability using sigmoid function
    # This gives probabilities between 0.1 and 0.9
    sigmoid = 1 / (1 + math.exp(-score_diff * 0.5))
    
    # Ensure probabilities are between 0.1 and 0.9
    home_win_prob = max(0.1, min(0.9, sigmoid))
    away_win_prob = 1.0 - home_win_prob
    
    return away_win_prob, home_win_prob

def add_missing_win_probabilities():
    """Add win probabilities to games that have score predictions but missing win probs"""
    
    # Load current cache
    with open('unified_predictions_cache.json', 'r') as f:
        cache_data = json.load(f)
    
    # Create backup
    backup_filename = f'unified_cache_before_win_probs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(cache_data, f, indent=2)
    print(f"Backup created: {backup_filename}")
    
    probabilities_added = 0
    games_updated = 0
    
    print("\n=== ADDING MISSING WIN PROBABILITIES ===")
    
    for date, date_data in cache_data.get('predictions_by_date', {}).items():
        if date == 'metadata':
            continue
        
        games_dict = date_data.get('games', {})
        date_updated = 0
        
        for game_key, game_data in games_dict.items():
            # Check if we have score predictions but missing win probabilities
            pred_away = game_data.get('predicted_away_score')
            pred_home = game_data.get('predicted_home_score')
            away_prob = game_data.get('away_win_probability')
            home_prob = game_data.get('home_win_probability')
            
            if (pred_away is not None and pred_home is not None and 
                (away_prob is None or home_prob is None)):
                
                # Calculate win probabilities
                calc_away_prob, calc_home_prob = calculate_win_probability(pred_away, pred_home)
                
                if calc_away_prob is not None and calc_home_prob is not None:
                    game_data['away_win_probability'] = calc_away_prob
                    game_data['home_win_probability'] = calc_home_prob
                    
                    probabilities_added += 2  # away and home
                    games_updated += 1
                    date_updated += 1
                    
                    print(f"  ✅ {game_key}: Added win probs (Away: {calc_away_prob:.1%}, Home: {calc_home_prob:.1%})")
        
        if date_updated > 0:
            print(f"Date {date}: Updated {date_updated} games with win probabilities")
    
    # Update metadata
    cache_data['metadata']['win_probabilities_added'] = probabilities_added
    cache_data['metadata']['win_prob_calculation_date'] = datetime.now().isoformat()
    cache_data['metadata']['win_prob_method'] = 'score_based_sigmoid'
    
    # Save updated cache
    with open('unified_predictions_cache_with_probs.json', 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\n=== WIN PROBABILITY ADDITION COMPLETE ===")
    print(f"Games updated: {games_updated}")
    print(f"Probabilities added: {probabilities_added}")
    print("Updated cache saved as: unified_predictions_cache_with_probs.json")
    
    return games_updated

def analyze_win_probabilities():
    """Analyze the updated cache with win probabilities"""
    
    with open('unified_predictions_cache_with_probs.json', 'r') as f:
        cache_data = json.load(f)
    
    total_games = 0
    games_with_probs = 0
    games_with_scores = 0
    
    print("\n=== WIN PROBABILITY ANALYSIS ===")
    
    for date, date_data in cache_data.get('predictions_by_date', {}).items():
        if date == 'metadata':
            continue
        
        games_dict = date_data.get('games', {})
        date_total = len(games_dict)
        date_with_probs = 0
        date_with_scores = 0
        
        for game_data in games_dict.values():
            total_games += 1
            
            # Check score predictions
            if (game_data.get('predicted_away_score') is not None and 
                game_data.get('predicted_home_score') is not None):
                games_with_scores += 1
                date_with_scores += 1
            
            # Check win probabilities
            if (game_data.get('away_win_probability') is not None and 
                game_data.get('home_win_probability') is not None):
                games_with_probs += 1
                date_with_probs += 1
        
        print(f"{date}: {date_total} games ({date_with_scores} scores, {date_with_probs} probs)")
    
    score_coverage = (games_with_scores/total_games)*100 if total_games > 0 else 0
    prob_coverage = (games_with_probs/total_games)*100 if total_games > 0 else 0
    
    print(f"\nUPDATED CACHE SUMMARY:")
    print(f"Total games: {total_games}")
    print(f"Games with score predictions: {games_with_scores} ({score_coverage:.1f}%)")
    print(f"Games with win probabilities: {games_with_probs} ({prob_coverage:.1f}%)")
    
    return prob_coverage

if __name__ == "__main__":
    updated_count = add_missing_win_probabilities()
    final_prob_coverage = analyze_win_probabilities()
    
    if updated_count > 0:
        print(f"\n🎉 SUCCESS: Added win probabilities to {updated_count} games!")
        print(f"Win probability coverage: {final_prob_coverage:.1f}%")
        print("\nTo apply the updated data:")
        print("1. Review unified_predictions_cache_with_probs.json")
        print("2. Replace unified_predictions_cache.json with the updated version")
        print("3. Restart Flask server to load the new probabilities")
    else:
        print("\n⚠️  No win probabilities were added. All games may already have probabilities.")
