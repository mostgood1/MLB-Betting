import json

# Check the historical predictions cache for our treasure
treasure_file = 'data_preservation/daily_backups/backup_20250814_220516/historical_predictions_cache.json'

try:
    with open(treasure_file, 'r') as f:
        data = json.load(f)
    
    print(f"🏺 CHECKING HISTORICAL CACHE")
    print(f"============================")
    print(f"File: {treasure_file}")
    print(f"Size: 159KB")
    print(f"Type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Top-level keys: {list(data.keys())[:10]}")
        
        # Check if it's nested by date
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"\nChecking key '{key}':")
                print(f"  Type: {type(value)}")
                if isinstance(value, dict):
                    print(f"  Sub-keys: {list(value.keys())[:5]}")
                    
                    # Check for game data
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, dict) and ('away_team' in sub_value or 'home_team' in sub_value):
                            confidence = sub_value.get('confidence', 0)
                            away = sub_value.get('away_team', '?')
                            home = sub_value.get('home_team', '?')
                            print(f"    GAME FOUND: {away} @ {home} (confidence: {confidence}%)")
                            break
                break
    
    elif isinstance(data, list):
        print(f"List with {len(data)} items")
        if len(data) > 0:
            print(f"First item type: {type(data[0])}")
            if isinstance(data[0], dict):
                print(f"First item keys: {list(data[0].keys())}")
                
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n🔍 Investigating the structure...")
