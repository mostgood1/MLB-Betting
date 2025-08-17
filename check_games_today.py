#!/usr/bin/env python3
"""
Check actual MLB games for today
"""
import sys
import os
sys.path.append('MLB-Betting')

from live_mlb_data import live_mlb_data

games = live_mlb_data.get_enhanced_games_data()
print(f"Found {len(games)} actual MLB games today:")

for i, game in enumerate(games):
    print(f"  {i+1}. {game['away_team']} @ {game['home_team']} - {game.get('status', 'Unknown')}")
    if game.get('game_time'):
        print(f"      Time: {game['game_time']}")
    if game.get('away_score') is not None and game.get('home_score') is not None:
        print(f"      Score: {game['away_team']} {game['away_score']} - {game['home_team']} {game['home_score']}")
    print()
