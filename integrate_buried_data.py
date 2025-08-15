import json
from datetime import datetime

def integrate_buried_predictions():
    """Integrate buried prediction data into the unified cache"""
    
    # Load current unified cache
    with open('unified_predictions_cache.json', 'r') as f:
        unified_cache = json.load(f)
    
    # Load buried predictions
    with open('buried_predictions_extracted.json', 'r') as f:
        buried_data = json.load(f)
    
    # Create backup
    backup_filename = f'unified_cache_before_buried_integration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(unified_cache, f, indent=2)
    print(f"Backup created: {backup_filename}")
    
    games_added = 0
    games_updated = 0
    
    print("\n=== INTEGRATING BURIED PREDICTIONS ===")
    
    for date, date_info in buried_data.items():
        print(f"\n📅 Processing {date}:")
        
        # Ensure date exists in unified cache
        if date not in unified_cache['predictions_by_date']:
            unified_cache['predictions_by_date'][date] = {
                'games': {},
                'summary': {
                    'total_games': 0,
                    'games_with_predictions': 0
                }
            }
            print(f"  Created new date entry for {date}")
        
        buried_games = date_info['games']
        unified_games = unified_cache['predictions_by_date'][date]['games']
        
        for game_key, game_data in buried_games.items():
            if game_key in unified_games:
                # Update existing game with buried data
                existing_game = unified_games[game_key]
                
                # Only update if current data is missing or incomplete
                updates_made = []
                
                if existing_game.get('away_win_probability') is None:
                    existing_game['away_win_probability'] = game_data['away_win_probability']
                    updates_made.append('away_win_prob')
                
                if existing_game.get('home_win_probability') is None:
                    existing_game['home_win_probability'] = game_data['home_win_probability']
                    updates_made.append('home_win_prob')
                
                if existing_game.get('predicted_away_score') is None:
                    existing_game['predicted_away_score'] = game_data['predicted_away_score']
                    updates_made.append('away_score')
                
                if existing_game.get('predicted_home_score') is None:
                    existing_game['predicted_home_score'] = game_data['predicted_home_score']
                    updates_made.append('home_score')
                
                if existing_game.get('away_pitcher') in [None, 'TBD']:
                    existing_game['away_pitcher'] = game_data['away_pitcher']
                    updates_made.append('away_pitcher')
                
                if existing_game.get('home_pitcher') in [None, 'TBD']:
                    existing_game['home_pitcher'] = game_data['home_pitcher']
                    updates_made.append('home_pitcher')
                
                # Add source tracking
                existing_game['buried_data_integrated'] = True
                existing_game['buried_source'] = 'historical_backfill'
                
                if updates_made:
                    games_updated += 1
                    print(f"  ✅ Updated {game_key}: {', '.join(updates_made)}")
                else:
                    print(f"  ➡️  {game_key}: No updates needed")
                    
            else:
                # Add new game from buried data
                unified_games[game_key] = game_data
                games_added += 1
                print(f"  ➕ Added {game_key}: New game from buried data")
        
        # Update summary
        total_games = len(unified_games)
        games_with_predictions = sum(1 for game in unified_games.values() 
                                   if game.get('predicted_away_score') is not None 
                                   and game.get('predicted_home_score') is not None)
        
        unified_cache['predictions_by_date'][date]['summary'] = {
            'total_games': total_games,
            'games_with_predictions': games_with_predictions,
            'buried_games_integrated': len(buried_games)
        }
        
        print(f"  📊 Date summary: {total_games} total games, {games_with_predictions} with predictions")
    
    # Update metadata
    unified_cache['metadata']['buried_data_integrated'] = True
    unified_cache['metadata']['buried_integration_date'] = datetime.now().isoformat()
    unified_cache['metadata']['buried_games_added'] = games_added
    unified_cache['metadata']['buried_games_updated'] = games_updated
    
    # Save updated cache
    with open('unified_predictions_cache_with_buried.json', 'w') as f:
        json.dump(unified_cache, f, indent=2)
    
    print(f"\n=== INTEGRATION COMPLETE ===")
    print(f"Games added: {games_added}")
    print(f"Games updated: {games_updated}")
    print("Updated cache saved as: unified_predictions_cache_with_buried.json")
    
    return games_added, games_updated

def analyze_final_coverage():
    """Analyze the final prediction coverage after integrating buried data"""
    
    with open('unified_predictions_cache_with_buried.json', 'r') as f:
        cache_data = json.load(f)
    
    total_games = 0
    games_with_predictions = 0
    games_with_win_probs = 0
    
    print("\n=== FINAL PREDICTION COVERAGE ANALYSIS ===")
    
    for date, date_data in cache_data.get('predictions_by_date', {}).items():
        if date == 'metadata':
            continue
        
        games_dict = date_data.get('games', {})
        date_total = len(games_dict)
        date_with_pred = 0
        date_with_probs = 0
        
        for game_data in games_dict.values():
            total_games += 1
            
            # Check score predictions
            if (game_data.get('predicted_away_score') is not None and 
                game_data.get('predicted_home_score') is not None):
                games_with_predictions += 1
                date_with_pred += 1
            
            # Check win probabilities
            if (game_data.get('away_win_probability') is not None and 
                game_data.get('home_win_probability') is not None):
                games_with_win_probs += 1
                date_with_probs += 1
        
        score_pct = (date_with_pred/date_total)*100 if date_total > 0 else 0
        prob_pct = (date_with_probs/date_total)*100 if date_total > 0 else 0
        
        print(f"{date}: {date_total} games ({date_with_pred} scores [{score_pct:.0f}%], {date_with_probs} probs [{prob_pct:.0f}%])")
    
    score_coverage = (games_with_predictions/total_games)*100 if total_games > 0 else 0
    prob_coverage = (games_with_win_probs/total_games)*100 if total_games > 0 else 0
    
    print(f"\n🎯 FINAL SYSTEM COVERAGE:")
    print(f"Total games: {total_games}")
    print(f"Games with score predictions: {games_with_predictions} ({score_coverage:.1f}%)")
    print(f"Games with win probabilities: {games_with_win_probs} ({prob_coverage:.1f}%)")
    
    return score_coverage, prob_coverage

if __name__ == "__main__":
    added, updated = integrate_buried_predictions()
    final_score_coverage, final_prob_coverage = analyze_final_coverage()
    
    print(f"\n🎉 BURIED DATA INTEGRATION SUCCESS!")
    print(f"Added {added} new games, updated {updated} existing games")
    print(f"Final coverage: {final_score_coverage:.1f}% scores, {final_prob_coverage:.1f}% win probabilities")
    
    if final_score_coverage > 70:
        print("\n✨ EXCELLENT! Coverage is now above 70%")
    elif final_score_coverage > 50:
        print("\n👍 GOOD! Coverage is now above 50%")
    else:
        print("\n📈 Coverage improved significantly with buried data")
