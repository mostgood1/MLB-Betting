#!/usr/bin/env python3
"""
August 12th Data Cleanup Script

This script analyzes and cleans up duplicate game entries for August 12th.
"""

import json
import os
from collections import defaultdict

def analyze_august_12_data():
    """Analyze August 12th data for duplicates"""
    print("=== August 12th Data Analysis ===\n")
    
    # Load game scores
    with open('game_scores_cache.json', 'r') as f:
        scores_data = json.load(f)
    
    # Load predictions
    with open('historical_predictions_cache.json', 'r') as f:
        pred_data = json.load(f)
    
    aug12_scores = scores_data.get('2025-08-12', {}).get('games', [])
    aug12_preds = pred_data.get('2025-08-12', {})
    
    print(f"August 12 game scores: {len(aug12_scores)} games")
    print(f"August 12 predictions: {len(aug12_preds)} entries")
    
    # Group games by matchup to find duplicates
    matchup_groups = defaultdict(list)
    
    print("\n=== Game Scores Analysis ===")
    for i, game in enumerate(aug12_scores):
        game_pk = game.get('game_pk')
        away = game.get('away_team', 'Unknown')
        home = game.get('home_team', 'Unknown')
        matchup = f"{away} @ {home}"
        
        matchup_groups[matchup].append({
            'index': i,
            'game_pk': game_pk,
            'matchup': matchup,
            'status': game.get('status', 'Unknown'),
            'is_final': game.get('is_final', False)
        })
    
    # Show all games and identify duplicates
    duplicates_found = []
    unique_games = []
    
    for matchup, games in matchup_groups.items():
        if len(games) > 1:
            print(f"\n🔍 DUPLICATE MATCHUP: {matchup}")
            duplicates_found.extend(games)
            for game in games:
                print(f"  Game {game['index']}: ID {game['game_pk']} - {game['status']} (Final: {game['is_final']})")
            
            # Keep the game with the standard MLB ID format (7-digit number starting with 776)
            best_game = None
            for game in games:
                game_id = str(game['game_pk'])
                if game_id.startswith('776') and len(game_id) == 6:
                    best_game = game
                    break
            
            if not best_game:
                # If no standard format, keep the first one
                best_game = games[0]
            
            unique_games.append(best_game)
            print(f"  → KEEPING: Game {best_game['index']} (ID: {best_game['game_pk']})")
        else:
            unique_games.append(games[0])
    
    print(f"\n=== Summary ===")
    print(f"Total games found: {len(aug12_scores)}")
    print(f"Unique matchups: {len(matchup_groups)}")
    print(f"Duplicate entries: {len(aug12_scores) - len(matchup_groups)}")
    print(f"Games to keep: {len(unique_games)}")
    
    return unique_games, duplicates_found

def clean_august_12_data():
    """Clean up August 12th data by removing duplicates"""
    print("\n=== Cleaning August 12th Data ===")
    
    # Load predictions data to check for duplicates
    with open('historical_predictions_cache.json', 'r') as f:
        pred_data = json.load(f)
    
    aug12_preds = pred_data.get('2025-08-12', {})
    cached_preds = aug12_preds.get('cached_predictions', {})
    
    print(f"Current August 12 predictions structure:")
    print(f"  Total entries: {len(aug12_preds)}")
    print(f"  Cached predictions: {len(cached_preds)}")
    
    # Check if we have both cached and backfill predictions
    backfill_keys = [k for k in aug12_preds.keys() if k.startswith('backfill_')]
    print(f"  Backfill predictions: {len(backfill_keys)}")
    
    if cached_preds and backfill_keys:
        print("\n🔍 FOUND DUPLICATE PREDICTIONS!")
        print("Cached predictions (old format):")
        for key in list(cached_preds.keys())[:5]:
            print(f"  {key}")
        if len(cached_preds) > 5:
            print(f"  ... and {len(cached_preds) - 5} more")
        
        print("\nBackfill predictions (proper format):")
        for key in backfill_keys[:5]:
            print(f"  {key}")
        if len(backfill_keys) > 5:
            print(f"  ... and {len(backfill_keys) - 5} more")
        
        # Create backup
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'historical_predictions_cache.json.bak_aug12_cleanup_{timestamp}'
        
        with open(backup_path, 'w') as f:
            json.dump(pred_data, f, indent=2)
        print(f"\nCreated backup: {backup_path}")
        
        # Remove the cached_predictions section for August 12
        print(f"\n🧹 Removing duplicate cached_predictions...")
        del pred_data['2025-08-12']['cached_predictions']
        
        # Update metadata
        pred_data['2025-08-12']['cleaned_duplicates'] = datetime.now().isoformat()
        pred_data['2025-08-12']['removed_cached_predictions'] = len(cached_preds)
        
        # Save cleaned data
        with open('historical_predictions_cache.json', 'w') as f:
            json.dump(pred_data, f, indent=2)
        
        print(f"✅ Removed {len(cached_preds)} duplicate cached predictions")
        print(f"August 12th now has {len(backfill_keys)} unique predictions")
        
    else:
        print("No duplicate predictions found!")
    
    # Also check game scores for any potential duplicates
    unique_games, duplicates = analyze_august_12_data()
    
    if duplicates:
        print(f"\n🧹 Found {len(duplicates)} duplicate game entries to clean...")
        # Previous game cleanup logic would go here
    else:
        print("\n✅ No duplicate games found!")

if __name__ == "__main__":
    clean_august_12_data()
