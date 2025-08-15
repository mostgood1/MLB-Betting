#!/usr/bin/env python3
"""
Real Prediction Data Restoration
================================
Replaces placeholder prediction scores (4-4, 3.952-4.048) with real simulation data.
"""

import json
import os
from datetime import datetime

def backup_current_cache():
    """Create a backup of current cache before modifications"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'unified_predictions_cache_before_real_restore_{timestamp}.json'
    
    with open('unified_predictions_cache.json', 'r') as f:
        data = json.load(f)
    
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def load_real_predictions():
    """Load real prediction data from extracted file"""
    if not os.path.exists('real_score_predictions_extracted.json'):
        print("❌ Real prediction data not found!")
        return None
    
    with open('real_score_predictions_extracted.json', 'r') as f:
        return json.load(f)

def convert_team_names(game_data):
    """Convert abbreviated team names to full names for consistency"""
    team_mapping = {
        'ATH': 'Athletics',
        'WSN': 'Washington Nationals',
        'CWS': 'Chicago White Sox',
        'SEA': 'Seattle Mariners',
        'CIN': 'Cincinnati Reds',
        'PIT': 'Pittsburgh Pirates',
        'LAD': 'Los Angeles Dodgers',
        'NYY': 'New York Yankees',
        'HOU': 'Houston Astros',
        'ATL': 'Atlanta Braves',
        'MIA': 'Miami Marlins',
        'NYM': 'New York Mets',
        'TOR': 'Toronto Blue Jays',
        'CLE': 'Cleveland Guardians',
        'TB': 'Tampa Bay Rays',
        'BOS': 'Boston Red Sox',
        'BAL': 'Baltimore Orioles',
        'LAA': 'Los Angeles Angels',
        'MIN': 'Minnesota Twins',
        'DET': 'Detroit Tigers',
        'CHC': 'Chicago Cubs',
        'PHI': 'Philadelphia Phillies',
        'STL': 'St. Louis Cardinals',
        'MIL': 'Milwaukee Brewers',
        'TEX': 'Texas Rangers',
        'COL': 'Colorado Rockies',
        'ARI': 'Arizona Diamondbacks',
        'OAK': 'Athletics',
        'SD': 'San Diego Padres',
        'SF': 'San Francisco Giants',
        'KC': 'Kansas City Royals'
    }
    
    # Convert team names
    away_team = game_data.get('away_team', '')
    home_team = game_data.get('home_team', '')
    
    if away_team in team_mapping:
        game_data['away_team'] = team_mapping[away_team]
    if home_team in team_mapping:
        game_data['home_team'] = team_mapping[home_team]
    
    return game_data

def is_placeholder_data(game_data):
    """Check if game data contains placeholder scores"""
    away_score = game_data.get('predicted_away_score')
    home_score = game_data.get('predicted_home_score')
    
    if away_score is None or home_score is None:
        return True
    
    # Check for common placeholder patterns
    if (away_score == 4.0 and home_score == 4.0) or \
       (away_score == 3.952 and home_score == 4.048) or \
       (str(away_score) == '4.0' and str(home_score) == '4.0') or \
       (str(away_score) == '3.952' and str(home_score) == '4.048'):
        return True
    
    return False

def restore_real_predictions():
    """Main function to restore real prediction data"""
    print("🔄 REAL PREDICTION DATA RESTORATION")
    print("=" * 50)
    
    # Backup current cache
    backup_file = backup_current_cache()
    
    # Load data
    real_data = load_real_predictions()
    if not real_data:
        return
    
    with open('unified_predictions_cache.json', 'r') as f:
        current_cache = json.load(f)
    
    # Track changes
    replacements_made = 0
    dates_modified = []
    
    # Process each date in real data
    for date, real_date_data in real_data.items():
        real_games = real_date_data.get('games', {})
        
        print(f"\n📅 Processing {date}...")
        
        # Check predictions_by_date structure
        if date in current_cache.get('predictions_by_date', {}):
            current_date_data = current_cache['predictions_by_date'][date]
            current_games = current_date_data.get('games', {})
            
            if isinstance(current_games, dict):
                # Check if current data needs replacement
                needs_replacement = False
                for game_id, game_data in current_games.items():
                    if is_placeholder_data(game_data):
                        needs_replacement = True
                        break
                
                if needs_replacement:
                    print(f"  🔄 Replacing placeholder data with real predictions...")
                    
                    # Convert real data format to match current structure
                    new_games = {}
                    for real_game_id, real_game_data in real_games.items():
                        # Convert team names
                        converted_game = convert_team_names(real_game_data.copy())
                        
                        # Create game ID from team names
                        away_team = converted_game['away_team']
                        home_team = converted_game['home_team']
                        new_game_id = f"{away_team} @ {home_team}"
                        
                        # Format data to match current structure
                        new_game = {
                            'away_team': away_team,
                            'home_team': home_team,
                            'predicted_away_score': converted_game.get('predicted_away_score'),
                            'predicted_home_score': converted_game.get('predicted_home_score'),
                            'predicted_total_runs': converted_game.get('predicted_total_runs'),
                            'away_win_probability': converted_game.get('away_win_probability', 0) * 100,  # Convert to percentage
                            'home_win_probability': converted_game.get('home_win_probability', 0) * 100,
                            'confidence': converted_game.get('confidence', 0),
                            'away_pitcher': current_games.get(list(current_games.keys())[0], {}).get('away_pitcher', 'TBD'),
                            'home_pitcher': current_games.get(list(current_games.keys())[0], {}).get('home_pitcher', 'TBD'),
                            'game_time': current_games.get(list(current_games.keys())[0], {}).get('game_time', 'TBD')
                        }
                        
                        new_games[new_game_id] = new_game
                    
                    # Replace the games data
                    current_cache['predictions_by_date'][date]['games'] = new_games
                    
                    replacements_made += len(new_games)
                    dates_modified.append(date)
                    print(f"  ✅ Replaced {len(new_games)} games with real prediction data")
                else:
                    print(f"  ✅ Already has good prediction data")
        
        # Also update direct date structure if it exists
        if date in current_cache and isinstance(current_cache[date], list):
            print(f"  🔄 Also updating direct date structure...")
            # This would need similar conversion logic
    
    # Save updated cache
    with open('unified_predictions_cache.json', 'w') as f:
        json.dump(current_cache, f, indent=2)
    
    print(f"\n🎯 RESTORATION COMPLETE!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"  • Dates modified: {len(dates_modified)}")
    print(f"  • Games replaced: {replacements_made}")
    print(f"  • Backup created: {backup_file}")
    print(f"  • Modified dates: {dates_modified}")
    
    return True

if __name__ == "__main__":
    restore_real_predictions()
