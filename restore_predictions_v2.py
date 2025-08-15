import json
from datetime import datetime

def normalize_team_name_to_short(full_name):
    """Convert full team names to short names used in historical cache"""
    team_mapping = {
        'Miami Marlins': 'Marlins',
        'Atlanta Braves': 'Braves', 
        'Houston Astros': 'Astros',
        'New York Yankees': 'Yankees',
        'Washington Nationals': 'Nationals',
        'San Francisco Giants': 'Giants',
        'Los Angeles Angels': 'Angels',
        'Detroit Tigers': 'Tigers',
        'Cincinnati Reds': 'Reds',
        'Pittsburgh Pirates': 'Pirates',
        'Oakland Athletics': 'Athletics',
        'Baltimore Orioles': 'Orioles',
        'Kansas City Royals': 'Royals',
        'Minnesota Twins': 'Twins',
        'Cleveland Guardians': 'Guardians',
        'Chicago White Sox': 'White Sox',
        'New York Mets': 'Mets',
        'Milwaukee Brewers': 'Brewers',
        'Chicago Cubs': 'Cubs',
        'St. Louis Cardinals': 'Cardinals',
        'Philadelphia Phillies': 'Phillies',
        'Texas Rangers': 'Rangers',
        'Colorado Rockies': 'Rockies',
        'Arizona Diamondbacks': 'Diamondbacks',
        'Boston Red Sox': 'Red Sox',
        'San Diego Padres': 'Padres',
        'Toronto Blue Jays': 'Blue Jays',
        'Los Angeles Dodgers': 'Dodgers',
        'Tampa Bay Rays': 'Rays',
        'Seattle Mariners': 'Mariners'
    }
    return team_mapping.get(full_name, full_name)

def restore_missing_predictions_v2():
    """Restore missing predictions from historical_predictions_cache.json (v2 - correct format)"""
    
    # Load both caches
    with open('unified_predictions_cache.json', 'r') as f:
        unified_cache = json.load(f)
    
    with open('historical_predictions_cache.json', 'r') as f:
        historical_cache = json.load(f)
    
    # Create backup
    backup_filename = f'unified_cache_before_restore_v2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(unified_cache, f, indent=2)
    print(f"Backup created: {backup_filename}")
    
    predictions_restored = 0
    games_updated = 0
    
    print("\n=== RESTORING MISSING PREDICTIONS (V2) ===")
    
    for date, date_data in unified_cache.get('predictions_by_date', {}).items():
        if date == 'metadata':
            continue
        
        if date not in historical_cache:
            print(f"No historical data for {date}")
            continue
        
        # Get the cached_predictions from historical cache
        historical_date_data = historical_cache[date]
        if 'cached_predictions' not in historical_date_data:
            print(f"No cached_predictions for {date}")
            continue
            
        historical_games = historical_date_data['cached_predictions']
        unified_games = date_data.get('games', {})
        
        date_restored = 0
        
        print(f"\nProcessing {date}:")
        print(f"  Historical games available: {len(historical_games)}")
        print(f"  Unified games to check: {len(unified_games)}")
        
        for game_key, game_data in unified_games.items():
            # Skip if already has predictions
            if (game_data.get('predicted_away_score') is not None and 
                game_data.get('predicted_home_score') is not None):
                continue
            
            away_team = game_data.get('away_team', '')
            home_team = game_data.get('home_team', '')
            
            # Convert to short names for matching
            short_away = normalize_team_name_to_short(away_team)
            short_home = normalize_team_name_to_short(home_team)
            
            # Try to find matching game in historical cache
            historical_key = f"{short_away} @ {short_home}"
            
            if historical_key in historical_games:
                historical_game = historical_games[historical_key]
                
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
                    
                    predictions_restored += 1
                    date_restored += 1
                    games_updated += 1
                    
                    print(f"  ✅ {game_key}: Restored predictions ({pred_away}-{pred_home}) from {historical_key}")
                else:
                    print(f"  ⚠️  {game_key}: Found match {historical_key} but no predictions")
            else:
                print(f"  ❌ {game_key} -> {historical_key}: No match found")
        
        if date_restored > 0:
            print(f"  📊 Date {date}: Restored {date_restored} predictions")
    
    # Update metadata
    unified_cache['metadata']['predictions_restored'] = predictions_restored
    unified_cache['metadata']['restoration_date'] = datetime.now().isoformat()
    unified_cache['metadata']['restoration_method'] = 'v2_cached_predictions'
    
    # Save updated cache
    with open('unified_predictions_cache_restored_v2.json', 'w') as f:
        json.dump(unified_cache, f, indent=2)
    
    print(f"\n=== RESTORATION COMPLETE ===")
    print(f"Predictions restored: {predictions_restored}")
    print(f"Games updated: {games_updated}")
    print("Restored cache saved as: unified_predictions_cache_restored_v2.json")
    
    return predictions_restored

def analyze_restoration_v2():
    """Analyze the restoration results"""
    
    with open('unified_predictions_cache_restored_v2.json', 'r') as f:
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
        
        coverage_pct = (date_with_pred/date_total)*100 if date_total > 0 else 0
        print(f"{date}: {date_total} games ({date_with_pred} with predictions - {coverage_pct:.1f}%)")
    
    coverage = (games_with_predictions/total_games)*100 if total_games > 0 else 0
    print(f"\nRESTORED CACHE SUMMARY:")
    print(f"Total games: {total_games}")
    print(f"Games with predictions: {games_with_predictions}")
    print(f"Coverage: {coverage:.1f}%")
    
    return coverage

if __name__ == "__main__":
    restored_count = restore_missing_predictions_v2()
    final_coverage = analyze_restoration_v2()
    
    if restored_count > 0:
        print(f"\n🎉 SUCCESS: Restored {restored_count} missing predictions!")
        print(f"Final prediction coverage: {final_coverage:.1f}%")
        print("\nTo apply the restored data:")
        print("1. Review unified_predictions_cache_restored_v2.json")
        print("2. Replace unified_predictions_cache.json with the restored version")
        print("3. Test the frontend to confirm predictions display")
    else:
        print("\n⚠️  No predictions were restored. Check the data format compatibility.")
