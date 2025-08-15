import json

# Check different cache files for our archaeological treasures
cache_files = [
    'unified_predictions_cache_with_buried.json',
    'unified_predictions_cache_restored_v2.json',
    'unified_predictions_cache_with_probs.json'
]

for cache_file in cache_files:
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        print(f"\n🏺 ANALYZING: {cache_file}")
        print(f"=====================================")
        print(f"Total entries: {len(data)}")
        
        # Check if it has our archaeological structure
        premium_count = 0
        total_games = 0
        
        # Check different structures
        if isinstance(data, dict):
            # Check if it's our individual game structure
            for key, value in data.items():
                if isinstance(value, dict) and ('away_team' in value or 'home_team' in value):
                    total_games += 1
                    confidence = value.get('confidence', 0)
                    if confidence > 50:
                        premium_count += 1
        
        print(f"Games found: {total_games}")
        print(f"Premium predictions: {premium_count}")
        
        if total_games > 0:
            print(f"📊 Sample games:")
            count = 0
            for key, value in data.items():
                if isinstance(value, dict) and ('away_team' in value or 'home_team' in value):
                    date = value.get('date', 'No date')
                    away = value.get('away_team', '?')
                    home = value.get('home_team', '?')
                    confidence = value.get('confidence', 0)
                    print(f"  {key}: {date} - {away} @ {home} (confidence: {confidence}%)")
                    count += 1
                    if count >= 3:
                        break
    
    except FileNotFoundError:
        print(f"❌ {cache_file} not found")
    except Exception as e:
        print(f"❌ Error reading {cache_file}: {e}")

print(f"\n🎯 CONCLUSION: Look for the file with the most games and premium predictions!")
