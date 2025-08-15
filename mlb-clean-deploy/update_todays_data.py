"""
Direct Enhanced Game Data Integration for Today's Games
This script directly integrates enhanced game data into the app
"""

import sys
import os

# Add the MLB-Betting directory to path
mlb_betting_dir = os.path.join(os.path.dirname(__file__), '..', 'MLB-Betting')
sys.path.insert(0, mlb_betting_dir)

from enhanced_mlb_fetcher import fetch_todays_complete_games
import json

def update_todays_game_data():
    """Update today's game data with complete pitcher information"""
    print("DIRECT GAME DATA UPDATE")
    print("=" * 40)
    
    # Fetch complete data for today
    today = '2025-08-14'
    complete_games = fetch_todays_complete_games(today)
    
    if complete_games:
        print(f"SUCCESS: Fetched {len(complete_games)} complete games")
        
        # Save to a file that the app can read
        output_file = os.path.join(mlb_betting_dir, 'data', 'todays_complete_games.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                'date': today,
                'games': complete_games,
                'count': len(complete_games)
            }, f, indent=2)
        
        print(f"💾 Saved complete game data to: {output_file}")
        
        # Also update the live test to verify
        print("\n🧪 VERIFICATION:")
        for i, game in enumerate(complete_games, 1):
            print(f"{i}. {game['away_team']} @ {game['home_team']}")
            print(f"   Pitchers: {game['away_pitcher']} vs {game['home_pitcher']}")
            print(f"   Time: {game['game_time']}")
        
        return True
    else:
        print("ERROR: No games fetched")
        return False

if __name__ == "__main__":
    update_todays_game_data()
