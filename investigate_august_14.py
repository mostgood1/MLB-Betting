#!/usr/bin/env python3
"""
August 14th Game Count Investigation
===================================

Investigate why August 14th shows 8 games instead of expected 7.
"""

import json
from datetime import datetime

def investigate_august_14():
    """Investigate the August 14th game count discrepancy"""
    print("🔍 AUGUST 14TH GAME COUNT INVESTIGATION")
    print("=" * 60)
    
    # Load the unified cache
    with open('unified_predictions_cache.json', 'r') as f:
        data = json.load(f)
    
    # Check both possible data locations
    predictions_data = data.get('predictions_by_date', data)
    
    target_date = '2025-08-14'
    
    if target_date in predictions_data:
        date_data = predictions_data[target_date]
        print(f"📅 Found data for {target_date}")
        
        # Extract games data
        games = None
        if 'games' in date_data:
            games = date_data['games']
        
        if games:
            # Handle both dict and list formats
            games_list = []
            if isinstance(games, dict):
                games_list = list(games.items())
                print(f"📊 Game data format: Dictionary with {len(games)} entries")
            elif isinstance(games, list):
                games_list = [(f"Game {i+1}", game) for i, game in enumerate(games)]
                print(f"📊 Game data format: List with {len(games)} entries")
            
            print(f"🎯 Total games found: {len(games_list)}")
            print()
            
            # List all games with details
            for i, (game_key, game_data) in enumerate(games_list, 1):
                print(f"🏈 Game {i}: {game_key}")
                
                if isinstance(game_data, dict):
                    away_team = game_data.get('away_team', 'Unknown')
                    home_team = game_data.get('home_team', 'Unknown')
                    away_pitcher = game_data.get('away_pitcher', 'TBD')
                    home_pitcher = game_data.get('home_pitcher', 'TBD')
                    source = game_data.get('source', 'unknown')
                    game_time = game_data.get('game_time', 'TBD')
                    
                    print(f"   Teams: {away_team} @ {home_team}")
                    print(f"   Pitchers: {away_pitcher} vs {home_pitcher}")
                    print(f"   Time: {game_time}")
                    print(f"   Source: {source}")
                    
                    # Check for scores
                    if 'predicted_away_score' in game_data:
                        away_score = game_data['predicted_away_score']
                        home_score = game_data['predicted_home_score']
                        print(f"   Score: {away_score}-{home_score}")
                    
                    # Check if this might be a duplicate
                    if game_key != f"{away_team} @ {home_team}":
                        print(f"   ⚠️  Key mismatch: '{game_key}' vs '{away_team} @ {home_team}'")
                    
                    print()
            
            # Look for potential duplicates
            print("🔍 DUPLICATE ANALYSIS")
            print("-" * 30)
            
            team_matchups = []
            for game_key, game_data in games_list:
                if isinstance(game_data, dict):
                    away = game_data.get('away_team', '')
                    home = game_data.get('home_team', '')
                    matchup = f"{away} @ {home}"
                    team_matchups.append(matchup)
            
            # Count unique matchups
            unique_matchups = set(team_matchups)
            print(f"📊 Unique team matchups: {len(unique_matchups)}")
            print(f"📊 Total game entries: {len(team_matchups)}")
            
            if len(unique_matchups) != len(team_matchups):
                print("⚠️  DUPLICATES DETECTED!")
                from collections import Counter
                matchup_counts = Counter(team_matchups)
                duplicates = {matchup: count for matchup, count in matchup_counts.items() if count > 1}
                
                for matchup, count in duplicates.items():
                    print(f"   🔄 {matchup}: {count} times")
            else:
                print("✅ No duplicate team matchups found")
            
            # Check expected MLB games for Aug 14, 2025
            print(f"\n📅 EXPECTED VS ACTUAL")
            print("-" * 30)
            print(f"Expected games for Aug 14th: 7-8 (typical MLB schedule)")
            print(f"Actual games found: {len(games_list)}")
            
            if len(games_list) == 8:
                print("✅ 8 games is within normal range for MLB")
            elif len(games_list) > 8:
                print("⚠️  More than typical MLB games - check for duplicates")
            else:
                print("ℹ️  Fewer than expected - check for missing games")
                
        else:
            print("❌ No games data found in date entry")
    else:
        print(f"❌ No data found for {target_date}")
        print("Available dates:", list(predictions_data.keys()))

if __name__ == "__main__":
    investigate_august_14()
