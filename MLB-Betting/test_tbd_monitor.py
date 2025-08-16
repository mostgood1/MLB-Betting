#!/usr/bin/env python3
"""
Test TBD Monitoring System
==========================
Create a test scenario with TBD pitchers to verify monitoring works
"""

import json
import sys
import os

def create_tbd_test():
    """Create a test with TBD pitchers"""
    
    # Load current cache
    cache_path = 'data/unified_predictions_cache.json'
    
    if not os.path.exists(cache_path):
        print("❌ Cache file not found")
        return False
    
    with open(cache_path, 'r') as f:
        data = json.load(f)
    
    current_date = '2025-08-15'
    
    if current_date not in data.get('predictions_by_date', {}):
        print(f"❌ No data for {current_date}")
        return False
    
    games = data['predictions_by_date'][current_date]['games']
    
    # Find first game and make its away pitcher TBD
    first_game_key = list(games.keys())[0]
    first_game = games[first_game_key]
    
    original_pitcher = first_game.get('away_pitcher', 'Unknown')
    first_game['away_pitcher'] = 'TBD'
    
    # Save backup and modified cache
    backup_path = 'data/unified_predictions_cache_backup.json'
    with open(backup_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Created TBD test scenario:")
    print(f"   Game: {first_game_key}")
    print(f"   Changed: {original_pitcher} → TBD")
    print(f"   Backup saved to: {backup_path}")
    
    return True

def restore_from_backup():
    """Restore original cache from backup"""
    cache_path = 'data/unified_predictions_cache.json'
    backup_path = 'data/unified_predictions_cache_backup.json'
    
    if not os.path.exists(backup_path):
        print("❌ No backup file found")
        return False
    
    with open(backup_path, 'r') as f:
        data = json.load(f)
    
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Restored cache from backup")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        restore_from_backup()
    else:
        create_tbd_test()
