#!/usr/bin/env python3
"""
Quick August 14th Duplicate Check
=================================
"""

import json

with open('unified_predictions_cache.json', 'r') as f:
    data = json.load(f)

predictions_data = data.get('predictions_by_date', data)
games = predictions_data['2025-08-14']['games']

print('🔍 AUGUST 14TH GAME KEYS AND TEAMS:')
print('=' * 50)

for i, (key, game) in enumerate(games.items(), 1):
    away = game.get('away_team', 'N/A')
    home = game.get('home_team', 'N/A')
    expected_key = f'{away} @ {home}'
    
    print(f'{i}. Key: "{key}"')
    print(f'   Teams: {away} @ {home}')
    print(f'   Expected: "{expected_key}"')
    
    if key != expected_key:
        print(f'   ⚠️  KEY MISMATCH!')
    
    # Check for duplicate teams
    matchup = f'{away} @ {home}'
    duplicate_count = sum(1 for k, g in games.items() 
                         if f'{g.get("away_team", "")} @ {g.get("home_team", "")}' == matchup)
    if duplicate_count > 1:
        print(f'   🔄 DUPLICATE: {duplicate_count} instances of this matchup')
    
    print()

print(f'📊 SUMMARY:')
print(f'Total game entries: {len(games)}')

# Count unique matchups
unique_matchups = set()
for game in games.values():
    away = game.get('away_team', '')
    home = game.get('home_team', '')
    unique_matchups.add(f'{away} @ {home}')

print(f'Unique team matchups: {len(unique_matchups)}')

if len(unique_matchups) != len(games):
    print(f'⚠️  DUPLICATES DETECTED: {len(games) - len(unique_matchups)} duplicate(s)')
else:
    print(f'✅ No duplicates found')
