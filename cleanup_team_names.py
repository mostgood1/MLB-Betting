import json
from datetime import datetime

def normalize_team_name(team_name):
    """Normalize team names to handle variations"""
    if not team_name:
        return team_name
    
    # Handle Athletics variations
    if team_name in ['Athletics', 'Oakland Athletics', 'Oakland A\'s', 'A\'s']:
        return 'Oakland Athletics'
    
    return team_name

def cleanup_team_names():
    """Clean up team name inconsistencies and merge duplicates in the unified cache"""
    
    with open('unified_predictions_cache.json', 'r') as f:
        cache_data = json.load(f)
    
    # Create backup
    backup_filename = f'unified_predictions_cache_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(cache_data, f, indent=2)
    print(f"Backup created: {backup_filename}")
    
    predictions = cache_data.get('predictions_by_date', {})
    changes_made = 0
    duplicates_merged = 0
    
    for date, date_data in predictions.items():
        if date == 'metadata':
            continue
            
        games_dict = date_data.get('games', {})
        new_games_dict = {}
        
        for matchup_key, game_data in games_dict.items():
            # Normalize team names
            original_away = game_data.get('away_team', '')
            original_home = game_data.get('home_team', '')
            
            normalized_away = normalize_team_name(original_away)
            normalized_home = normalize_team_name(original_home)
            
            # Update the game data
            game_data['away_team'] = normalized_away
            game_data['home_team'] = normalized_home
            
            # Create normalized matchup key
            normalized_key = f"{normalized_away} @ {normalized_home}"
            
            # Check if this normalized matchup already exists
            if normalized_key in new_games_dict:
                print(f"  Merging duplicate: {matchup_key} into {normalized_key}")
                duplicates_merged += 1
                
                # Merge data - prioritize non-null values
                existing_game = new_games_dict[normalized_key]
                
                # Merge prediction data (keep non-null values)
                for field in ['predicted_away_score', 'predicted_home_score', 'away_win_prob', 'home_win_prob']:
                    if game_data.get(field) is not None and existing_game.get(field) is None:
                        existing_game[field] = game_data[field]
                        print(f"    Restored {field}: {game_data[field]}")
                
                # Merge actual scores if available
                for field in ['away_score', 'home_score']:
                    if game_data.get(field) is not None and existing_game.get(field) is None:
                        existing_game[field] = game_data[field]
                        print(f"    Added {field}: {game_data[field]}")
                        
            else:
                new_games_dict[normalized_key] = game_data
                
                if original_away != normalized_away or original_home != normalized_home:
                    changes_made += 1
                    print(f"  Normalized: {matchup_key} -> {normalized_key}")
        
        date_data['games'] = new_games_dict
    
    # Update metadata
    cache_data['metadata']['last_cleanup'] = datetime.now().isoformat()
    cache_data['metadata']['duplicates_merged'] = duplicates_merged
    cache_data['metadata']['names_normalized'] = changes_made
    
    # Save the cleaned cache
    with open('unified_predictions_cache_cleaned.json', 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\nCleanup complete!")
    print(f"- Team names normalized: {changes_made}")
    print(f"- Duplicates merged: {duplicates_merged}")
    print("- Cleaned cache saved as: unified_predictions_cache_cleaned.json")
    
    return changes_made, duplicates_merged

if __name__ == "__main__":
    changes, merges = cleanup_team_names()
    
    # Re-analyze the cleaned cache
    print("\n" + "="*50)
    print("RE-ANALYZING CLEANED CACHE...")
    
    with open('unified_predictions_cache_cleaned.json', 'r') as f:
        cleaned_data = json.load(f)
    
    total_games = 0
    games_with_predictions = 0
    
    for date, date_data in cleaned_data.get('predictions_by_date', {}).items():
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
    
    print(f"\nCLEANED CACHE SUMMARY:")
    print(f"Total games: {total_games}")
    print(f"Games with predictions: {games_with_predictions}")
    print(f"Coverage: {(games_with_predictions/total_games)*100:.1f}%")
