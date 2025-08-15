#!/usr/bin/env python3
"""
Fix August 14th Duplicate Game
=============================

Remove the duplicate Seattle Mariners @ Baltimore Orioles entry
and standardize team name formatting.
"""

import json
from datetime import datetime

def fix_august_14_duplicate():
    """Fix the duplicate game issue for August 14th"""
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'unified_predictions_cache_before_aug14_fix_{timestamp}.json'
    
    print("🔧 FIXING AUGUST 14TH DUPLICATE GAME")
    print("=" * 50)
    
    # Load current data
    with open('unified_predictions_cache.json', 'r') as f:
        data = json.load(f)
    
    # Create backup
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Backup created: {backup_file}")
    
    # Fix the data
    predictions_data = data.get('predictions_by_date', data)
    
    if '2025-08-14' in predictions_data:
        games = predictions_data['2025-08-14']['games']
        
        print(f"\n📊 Before fix: {len(games)} games")
        
        # Identify the duplicate entries
        underscore_key = "Seattle_Mariners @ Baltimore_Orioles"
        spaces_key = "Seattle Mariners @ Baltimore Orioles"
        
        if underscore_key in games and spaces_key in games:
            print(f"🔍 Found both entries:")
            print(f"   Underscores: {underscore_key}")
            print(f"   Spaces: {spaces_key}")
            
            # Compare the two entries
            underscore_game = games[underscore_key]
            spaces_game = games[spaces_key]
            
            print(f"\n📊 Comparison:")
            print(f"   Underscores - Score: {underscore_game.get('predicted_away_score')}-{underscore_game.get('predicted_home_score')}, Time: {underscore_game.get('prediction_time', 'N/A')}")
            print(f"   Spaces - Score: {spaces_game.get('predicted_away_score')}-{spaces_game.get('predicted_home_score')}, Time: {spaces_game.get('prediction_time', 'N/A')}")
            
            # Keep the spaces version (more standard) and remove underscores version
            print(f"\n🗑️  Removing duplicate with underscores...")
            del games[underscore_key]
            
            # Update metadata
            if 'metadata' in data:
                data['metadata']['aug_14_duplicate_fixed'] = True
                data['metadata']['duplicate_fix_date'] = datetime.now().isoformat()
                data['metadata']['removed_duplicate'] = underscore_key
                data['metadata']['kept_entry'] = spaces_key
            
            print(f"✅ Duplicate removed!")
            
        else:
            print("❌ Duplicate entries not found as expected")
            return
        
        print(f"📊 After fix: {len(games)} games")
        
        # Verify the fix
        print(f"\n🔍 Verification:")
        seattle_baltimore_count = 0
        for key, game in games.items():
            away = game.get('away_team', '').replace('_', ' ')
            home = game.get('home_team', '').replace('_', ' ')
            if away == 'Seattle Mariners' and home == 'Baltimore Orioles':
                seattle_baltimore_count += 1
                print(f"   ✅ Found: {key}")
        
        print(f"   Seattle @ Baltimore games: {seattle_baltimore_count}")
        
        if seattle_baltimore_count == 1:
            print("✅ Fix successful - only one Seattle @ Baltimore game remains")
        else:
            print("⚠️  Issue not fully resolved")
        
        # Save the fixed data
        with open('unified_predictions_cache.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Updated cache saved")
        print(f"📊 August 14th now has {len(games)} games (should be 7)")
        
    else:
        print("❌ August 14th data not found")

if __name__ == "__main__":
    fix_august_14_duplicate()
