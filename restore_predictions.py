import json
from datetime import datetime

def restore_missing_predictions():
    """Restore missing predictions from historical_predictions_cache.json to unified cache"""
    
    # Load both caches
    with open('unified_predictions_cache.json', 'r') as f:
        unified_cache = json.load(f)
    
    with open('historical_predictions_cache.json', 'r') as f:
        historical_cache = json.load(f)
    
    # Create backup
    backup_filename = f'unified_predictions_cache_before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(unified_cache, f, indent=2)
    print(f"Backup created: {backup_filename}")
    
    predictions_restored = 0
    games_updated = 0
    
    print("\n=== RESTORING MISSING PREDICTIONS ===")
    
    for date, date_data in unified_cache.get('predictions_by_date', {}).items():
        if date == 'metadata':
            continue
        
        if date not in historical_cache:
            print(f"No historical data for {date}")
            continue
        
        historical_games = historical_cache[date]
        unified_games = date_data.get('games', {})
        
        date_restored = 0
        
        for game_key, game_data in unified_games.items():
            # Skip if already has predictions
            if (game_data.get('predicted_away_score') is not None and 
                game_data.get('predicted_home_score') is not None):
                continue
            
            away_team = game_data.get('away_team', '')
            home_team = game_data.get('home_team', '')
            
            # Try to find matching game in historical cache
            found_match = False
            
            # Try various key formats
            possible_keys = [
                f"{away_team} @ {home_team}",
                f"{away_team} at {home_team}",
                f"{away_team}_at_{home_team}",
                f"{away_team.replace(' ', '_')}_at_{home_team.replace(' ', '_')}",
                # Handle team name variations
                f"Athletics @ {home_team}" if away_team == "Oakland Athletics" else None,
                f"Oakland Athletics @ {home_team}" if away_team == "Athletics" else None,
            ]
            
            # Remove None values
            possible_keys = [k for k in possible_keys if k is not None]
            
            for key in possible_keys:
                if key in historical_games:
                    historical_game = historical_games[key]
                    
                    # Check if historical game has predictions
                    pred_away = historical_game.get('predicted_away_score')
                    pred_home = historical_game.get('predicted_home_score')
                    
                    if pred_away is not None and pred_home is not None:
                        # Restore predictions
                        game_data['predicted_away_score'] = pred_away
                        game_data['predicted_home_score'] = pred_home
                        
                        # Also restore other prediction data if available
                        if 'predicted_total_runs' in historical_game:
                            game_data['predicted_total_runs'] = historical_game['predicted_total_runs']
                        
                        if 'away_win_prob' in historical_game and game_data.get('away_win_prob') is None:
                            game_data['away_win_prob'] = historical_game.get('away_win_prob')
                        
                        if 'home_win_prob' in historical_game and game_data.get('home_win_prob') is None:
                            game_data['home_win_prob'] = historical_game.get('home_win_prob')
                        
                        predictions_restored += 1
                        date_restored += 1
                        games_updated += 1
                        found_match = True
                        
                        print(f"  ✅ {game_key}: Restored predictions ({pred_away}-{pred_home})")
                        break
            
            if not found_match:
                print(f"  ❌ {game_key}: No matching historical data found")
        
        if date_restored > 0:
            print(f"Date {date}: Restored {date_restored} predictions")
    
    # Update metadata
    unified_cache['metadata']['predictions_restored'] = predictions_restored
    unified_cache['metadata']['restoration_date'] = datetime.now().isoformat()
    
    # Save updated cache
    with open('unified_predictions_cache_restored.json', 'w') as f:
        json.dump(unified_cache, f, indent=2)
    
    print(f"\n=== RESTORATION COMPLETE ===")
    print(f"Predictions restored: {predictions_restored}")
    print(f"Games updated: {games_updated}")
    print("Restored cache saved as: unified_predictions_cache_restored.json")
    
    return predictions_restored

def analyze_restoration():
    """Analyze the restoration results"""
    
    with open('unified_predictions_cache_restored.json', 'r') as f:
        restored_cache = json.load(f)
    
    total_games = 0
    games_with_predictions = 0
    
    print("\n=== POST-RESTORATION ANALYSIS ===")
    
    for date, date_data in restored_cache.get('predictions_by_date', {}).items():
        if date == 'metadata':
            continue
        
        games_dict = date_data.get('games', {})
        date_total = len(games_dict)
        date_with_pred = 0
        
        for game_data in games_dict.values():
            total_games += 1
            if (game_data.get('predicted_away_score') is not None and 
                game_data.get('predicted_home_score') is not None):
                games_with_predictions += 1
                date_with_pred += 1
        
        print(f"{date}: {date_total} games ({date_with_pred} with predictions)")
    
    coverage = (games_with_predictions/total_games)*100 if total_games > 0 else 0
    print(f"\nRESTORED CACHE SUMMARY:")
    print(f"Total games: {total_games}")
    print(f"Games with predictions: {games_with_predictions}")
    print(f"Coverage: {coverage:.1f}%")
    
    return coverage

if __name__ == "__main__":
    restored_count = restore_missing_predictions()
    final_coverage = analyze_restoration()
    
    if restored_count > 0:
        print(f"\n🎉 SUCCESS: Restored {restored_count} missing predictions!")
        print(f"Final prediction coverage: {final_coverage:.1f}%")
        print("\nTo apply the restored data:")
        print("1. Review unified_predictions_cache_restored.json")
        print("2. Replace unified_predictions_cache.json with the restored version")
    else:
        print("\n⚠️  No predictions were restored. Check the data format compatibility.")
