import json

# Load and verify our archaeological treasure
with open('archaeological_treasure_unified.json', 'r') as f:
    treasure = json.load(f)

print("🏺 TREASURE VERIFICATION")
print("========================")

confidence_games = []
for game_id, game_data in treasure.items():
    confidence = game_data.get('confidence', 0)
    if confidence > 50:
        confidence_games.append((game_id, confidence, game_data))

print(f"Premium predictions found: {len(confidence_games)}")

if confidence_games:
    confidence_games.sort(key=lambda x: x[1], reverse=True)
    print(f"\n💎 TOP PREMIUM PREDICTIONS:")
    for i, (game_id, confidence, game_data) in enumerate(confidence_games[:5]):
        date = game_data.get('date', '?')
        away = game_data.get('away_team', '?')
        home = game_data.get('home_team', '?')
        print(f"{i+1}. {date} - {away} @ {home} ({confidence}%)")

# Copy to MLB-Betting
with open('MLB-Betting/unified_predictions_cache.json', 'w') as f:
    json.dump(treasure, f, indent=2)

print(f"\n🚀 Treasure deployed to MLB-Betting!")
print(f"System ready with {len(treasure)} games including {len(confidence_games)} premium predictions!")
