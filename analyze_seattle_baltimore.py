#!/usr/bin/env python3
"""
Seattle Mariners @ Baltimore Orioles Duplicate Analysis
======================================================
"""

import json

with open('unified_predictions_cache.json', 'r') as f:
    data = json.load(f)

predictions_data = data.get('predictions_by_date', data)
games = predictions_data['2025-08-14']['games']

print('🔍 SEATTLE MARINERS @ BALTIMORE ORIOLES ANALYSIS')
print('=' * 60)

# Find all Seattle @ Baltimore games
seattle_baltimore_games = []
for key, game in games.items():
    away = game.get('away_team', '')
    home = game.get('home_team', '')
    
    # Check if this is a Seattle @ Baltimore game (normalize for comparison)
    if (away.replace('_', ' ').replace('Mariners', 'Mariners').strip() == 'Seattle Mariners' and 
        home.replace('_', ' ').replace('Orioles', 'Orioles').strip() == 'Baltimore Orioles'):
        seattle_baltimore_games.append((key, game))

print(f'Found {len(seattle_baltimore_games)} Seattle @ Baltimore games:')
print()

for i, (key, game) in enumerate(seattle_baltimore_games, 1):
    print(f'🏈 Instance {i}:')
    print(f'   Key: "{key}"')
    print(f'   Away Team: "{game.get("away_team", "N/A")}"')
    print(f'   Home Team: "{game.get("home_team", "N/A")}"')
    print(f'   Away Pitcher: {game.get("away_pitcher", "TBD")}')
    print(f'   Home Pitcher: {game.get("home_pitcher", "TBD")}')
    print(f'   Score: {game.get("predicted_away_score", "N/A")}-{game.get("predicted_home_score", "N/A")}')
    print(f'   Source: {game.get("source", "unknown")}')
    print(f'   Game Time: {game.get("game_time", "TBD")}')
    
    # Check for any other identifying fields
    if 'game_id' in game:
        print(f'   Game ID: {game["game_id"]}')
    if 'prediction_time' in game:
        print(f'   Prediction Time: {game["prediction_time"]}')
    
    print()

if len(seattle_baltimore_games) > 1:
    print('⚠️  DUPLICATE DETECTED!')
    print('This explains why August 14th shows 8 games instead of 7.')
    print('The same game is stored with different team name formats:')
    print('- "Seattle_Mariners @ Baltimore_Orioles" (underscores)')
    print('- "Seattle Mariners @ Baltimore Orioles" (spaces)')
    print()
    print('🔧 SOLUTION NEEDED:')
    print('1. Remove one of the duplicate entries')
    print('2. Standardize team name formatting (spaces vs underscores)')
    print('3. Implement duplicate detection in data processing pipeline')
else:
    print('✅ No duplicates found - investigation needs to continue elsewhere')
