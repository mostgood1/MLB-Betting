import json

# Check our archaeological treasure
treasure_file = 'data_preservation/daily_backups/backup_20250814_220516/buried_predictions_extracted.json'

try:
    with open(treasure_file, 'r') as f:
        data = json.load(f)
    
    print(f"🏺 ARCHAEOLOGICAL TREASURE FOUND!")
    print(f"=================================")
    print(f"File: {treasure_file}")
    print(f"Total entries: {len(data)}")
    
    premium_count = 0
    confidence_levels = []
    
    for key, value in data.items():
        if isinstance(value, dict):
            confidence = value.get('confidence', 0)
            if confidence > 0:
                confidence_levels.append(confidence)
            if confidence > 50:
                premium_count += 1
    
    print(f"Premium predictions (>50% confidence): {premium_count}")
    print(f"Confidence levels found: {sorted(set(confidence_levels))}")
    
    print(f"\n💎 Sample archaeological discoveries:")
    count = 0
    for key, value in data.items():
        if isinstance(value, dict) and value.get('confidence', 0) > 50:
            date = value.get('date', 'No date')
            away = value.get('away_team', '?')
            home = value.get('home_team', '?')
            confidence = value.get('confidence', 0)
            away_score = value.get('away_score', '?')
            home_score = value.get('home_score', '?')
            print(f"  {key}: {date} - {away} @ {home}")
            print(f"    Confidence: {confidence}% | Score: {away_score}-{home_score}")
            count += 1
            if count >= 5:
                break
                
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n🎯 This is our archaeological treasure with premium predictions!")
