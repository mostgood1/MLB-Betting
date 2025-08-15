import json
import re
from collections import defaultdict
from datetime import datetime

def normalize_team_name(team_name):
    """Normalize team names to handle variations like Athletics vs Oakland Athletics"""
    if not team_name:
        return team_name
    
    # Handle Athletics variations
    if team_name in ['Athletics', 'Oakland Athletics', 'Oakland A\'s', 'A\'s']:
        return 'Oakland Athletics'
    
    # Add other normalizations as needed
    return team_name

def analyze_and_cleanup_cache():
    """Analyze and clean up the unified predictions cache"""
    
    try:
        with open('unified_predictions_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        print("=== UNIFIED CACHE ANALYSIS ===")
        print(f"Cache created: {cache_data.get('metadata', {}).get('created_at', 'Unknown')}")
        print(f"Total games: {cache_data.get('metadata', {}).get('total_games', 'Unknown')}")
        print()
        
        predictions = cache_data.get('predictions_by_date', {})
        
        # Analysis variables
        all_teams = set()
        athletics_variations = set()
        missing_predictions = []
        duplicate_matchups = defaultdict(list)
        total_games = 0
        games_with_predictions = 0
        
        # Analyze each date
        for date, date_data in predictions.items():
            if date == 'metadata':
                continue
                
            games_dict = date_data.get('games', {})
            date_total = len(games_dict)
            date_with_pred = 0
            
            print(f"Date {date}: {date_total} games")
            
            for matchup_key, game_data in games_dict.items():
                total_games += 1
                
                away_team = game_data.get('away_team', '')
                home_team = game_data.get('home_team', '')
                
                # Collect team names
                all_teams.add(away_team)
                all_teams.add(home_team)
                
                # Check for Athletics variations
                if 'athletic' in away_team.lower() or 'oakland' in away_team.lower():
                    athletics_variations.add(away_team)
                if 'athletic' in home_team.lower() or 'oakland' in home_team.lower():
                    athletics_variations.add(home_team)
                
                # Check for predictions
                has_score_pred = (game_data.get('predicted_away_score') is not None and 
                                 game_data.get('predicted_home_score') is not None)
                
                if has_score_pred:
                    games_with_predictions += 1
                    date_with_pred += 1
                else:
                    missing_predictions.append({
                        'date': date,
                        'matchup': matchup_key,
                        'away_team': away_team,
                        'home_team': home_team
                    })
                
                # Check for potential duplicates (normalized matchup)
                normalized_away = normalize_team_name(away_team)
                normalized_home = normalize_team_name(home_team)
                normalized_matchup = f"{normalized_away} @ {normalized_home}"
                duplicate_matchups[f"{date}:{normalized_matchup}"].append({
                    'original_key': matchup_key,
                    'away_team': away_team,
                    'home_team': home_team,
                    'normalized_away': normalized_away,
                    'normalized_home': normalized_home
                })
            
            print(f"  - With predictions: {date_with_pred}/{date_total}")
        
        print()
        print("=== TEAM NAME ANALYSIS ===")
        print("Athletics variations found:")
        for variation in sorted(athletics_variations):
            print(f"  - {variation}")
        
        print()
        print("=== PREDICTION COVERAGE ===")
        print(f"Total games: {total_games}")
        print(f"Games with score predictions: {games_with_predictions}")
        print(f"Games missing predictions: {len(missing_predictions)}")
        print(f"Coverage: {(games_with_predictions/total_games)*100:.1f}%")
        
        print()
        print("=== MISSING PREDICTIONS BY DATE ===")
        missing_by_date = defaultdict(int)
        for missing in missing_predictions:
            missing_by_date[missing['date']] += 1
        
        for date in sorted(missing_by_date.keys()):
            count = missing_by_date[date]
            print(f"  {date}: {count} games missing predictions")
        
        print()
        print("=== DUPLICATE/INCONSISTENT TEAM NAMES ===")
        inconsistencies_found = False
        for key, games_list in duplicate_matchups.items():
            if len(games_list) > 1:
                print(f"Multiple entries for {key}:")
                for game in games_list:
                    print(f"  - {game['original_key']}")
                inconsistencies_found = True
            elif len(games_list) == 1:
                game = games_list[0]
                if (game['away_team'] != game['normalized_away'] or 
                    game['home_team'] != game['normalized_home']):
                    print(f"Team name inconsistency:")
                    print(f"  Original: {game['away_team']} @ {game['home_team']}")
                    print(f"  Should be: {game['normalized_away']} @ {game['normalized_home']}")
                    inconsistencies_found = True
        
        if not inconsistencies_found:
            print("No team name inconsistencies found")
        
        return {
            'total_games': total_games,
            'games_with_predictions': games_with_predictions,
            'athletics_variations': athletics_variations,
            'missing_predictions': missing_predictions,
            'duplicate_matchups': duplicate_matchups
        }
        
    except FileNotFoundError:
        print("unified_predictions_cache.json not found")
        return None
    except Exception as e:
        print(f"Error analyzing cache: {str(e)}")
        return None

def create_cleanup_script():
    """Create a script to clean up team name inconsistencies"""
    
    cleanup_script = '''
def cleanup_team_names():
    """Clean up team name inconsistencies in the unified cache"""
    
    with open('unified_predictions_cache.json', 'r') as f:
        cache_data = json.load(f)
    
    # Create backup
    backup_filename = f'unified_predictions_cache_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(cache_data, f, indent=2)
    print(f"Backup created: {backup_filename}")
    
    predictions = cache_data.get('predictions_by_date', {})
    changes_made = 0
    
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
            
            # Create new matchup key
            new_matchup_key = f"{normalized_away} @ {normalized_home}"
            new_games_dict[new_matchup_key] = game_data
            
            if original_away != normalized_away or original_home != normalized_home:
                changes_made += 1
                print(f"  Changed: {matchup_key} -> {new_matchup_key}")
        
        date_data['games'] = new_games_dict
    
    # Save the cleaned cache
    with open('unified_predictions_cache_cleaned.json', 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\\nCleanup complete! {changes_made} team name changes made.")
    print("Cleaned cache saved as: unified_predictions_cache_cleaned.json")
    
    return changes_made

if __name__ == "__main__":
    cleanup_team_names()
'''
    
    with open('cleanup_team_names.py', 'w') as f:
        f.write(cleanup_script)
    
    print("Cleanup script created: cleanup_team_names.py")

if __name__ == "__main__":
    result = analyze_and_cleanup_cache()
    if result:
        print("\\n" + "="*50)
        print("Analysis complete!")
        print("\\nTo fix team name inconsistencies, run: python cleanup_team_names.py")
        
        # Check if we need to restore prediction data
        missing_count = len(result['missing_predictions'])
        if missing_count > 0:
            print(f"\\nWARNING: {missing_count} games are missing score predictions!")
            print("This suggests some data was overwritten as you mentioned.")
            print("You may need to restore from a backup or regenerate predictions.")
