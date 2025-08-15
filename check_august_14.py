#!/usr/bin/env python3

import json

def check_august_14():
    """Check the status of games on August 14th"""
    
    # Load unified cache
    with open('unified_predictions_cache.json', 'r') as f:
        data = json.load(f)
    
    games = data.get('2025-08-14', [])
    print(f"Total games on 2025-08-14: {len(games)}")
    print("\nGame Status Overview:")
    print("=" * 60)
    
    for i, game in enumerate(games, 1):
        away_team = game.get('away_team', 'Unknown')
        home_team = game.get('home_team', 'Unknown')
        status = game.get('game_status', 'Unknown')
        away_score = game.get('away_score', 'N/A')
        home_score = game.get('home_score', 'N/A')
        has_analysis = 'performance_analysis' in game
        
        print(f"{i}. {away_team} @ {home_team}")
        print(f"   Status: {status}")
        print(f"   Score: {away_team} {away_score} - {home_team} {home_score}")
        print(f"   Has Analysis: {has_analysis}")
        
        if status == 'Delayed':
            print(f"   ⚠️  DELAYED GAME FOUND!")
            print(f"   Full game data: {json.dumps(game, indent=2)}")
        
        print()

if __name__ == "__main__":
    check_august_14()
