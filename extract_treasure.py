import json
from datetime import datetime

def extract_archaeological_treasure():
    """Extract all archaeological treasures and create unified cache"""
    
    print("🏺 ARCHAEOLOGICAL TREASURE EXTRACTION")
    print("=====================================")
    
    # Load the historical cache with all our treasures
    treasure_file = 'data_preservation/daily_backups/backup_20250814_220516/historical_predictions_cache.json'
    
    with open(treasure_file, 'r') as f:
        historical_data = json.load(f)
    
    print(f"Source: {treasure_file}")
    print(f"Dates found: {list(historical_data.keys())}")
    
    # Extract all games into unified structure
    unified_treasure = {}
    total_games = 0
    premium_count = 0
    confidence_levels = []
    
    for date, date_data in historical_data.items():
        if isinstance(date_data, dict):
            print(f"\n📅 Processing date: {date}")
            
            # Check all possible keys for game data
            for key, value in date_data.items():
                if isinstance(value, dict):
                    # Check if this looks like game data
                    if 'away_team' in value and 'home_team' in value:
                        game_id = f"{date}_{key}"
                        
                        # Ensure date is included
                        value['date'] = date
                        
                        unified_treasure[game_id] = value
                        total_games += 1
                        
                        confidence = value.get('confidence', 0)
                        if confidence > 0:
                            confidence_levels.append(confidence)
                        if confidence > 50:
                            premium_count += 1
                        
                        away = value.get('away_team', '?')
                        home = value.get('home_team', '?')
                        print(f"  🎯 {away} @ {home} (confidence: {confidence}%)")
                    
                    # Check if it's nested further (like cached_predictions)
                    elif 'predictions' in key.lower() or 'backfill' in key.lower():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, dict) and 'away_team' in sub_value:
                                    game_id = f"{date}_{key}_{sub_key}"
                                    sub_value['date'] = date
                                    unified_treasure[game_id] = sub_value
                                    total_games += 1
                                    
                                    confidence = sub_value.get('confidence', 0)
                                    if confidence > 0:
                                        confidence_levels.append(confidence)
                                    if confidence > 50:
                                        premium_count += 1
                                    
                                    away = sub_value.get('away_team', '?')
                                    home = sub_value.get('home_team', '?')
                                    print(f"    💎 {away} @ {home} (confidence: {confidence}%)")
    
    print(f"\n🏆 ARCHAEOLOGICAL EXTRACTION COMPLETE!")
    print(f"======================================")
    print(f"Total games extracted: {total_games}")
    print(f"Premium predictions: {premium_count}")
    print(f"Premium rate: {premium_count/total_games*100:.1f}%" if total_games > 0 else "N/A")
    print(f"Confidence levels: {sorted(set(confidence_levels))}")
    
    # Save the unified treasure
    output_file = 'archaeological_treasure_unified.json'
    with open(output_file, 'w') as f:
        json.dump(unified_treasure, f, indent=2)
    
    print(f"\n💾 Treasure saved to: {output_file}")
    
    # Copy to MLB-Betting for immediate use
    mlb_file = 'MLB-Betting/unified_predictions_cache.json'
    with open(mlb_file, 'w') as f:
        json.dump(unified_treasure, f, indent=2)
    
    print(f"💾 Treasure deployed to: {mlb_file}")
    
    return unified_treasure

if __name__ == "__main__":
    treasure = extract_archaeological_treasure()
    
    print(f"\n🚀 ARCHAEOLOGICAL MISSION: COMPLETE!")
    print(f"The MLB-Betting system now has access to all discovered treasures!")
