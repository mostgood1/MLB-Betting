import json

# Analyze our archaeological treasure
with open('archaeological_treasure_unified.json', 'r') as f:
    treasure = json.load(f)

print("🏺 ARCHAEOLOGICAL TREASURE ANALYSIS")
print("==================================")

total_games = len(treasure)
premium_predictions = sum(1 for game in treasure.values() if game.get('confidence', 0) > 50)
confidence_levels = [game.get('confidence', 0) for game in treasure.values() if game.get('confidence', 0) > 0]

print(f"Total games: {total_games}")
print(f"Premium predictions (>50%): {premium_predictions}")
print(f"Premium rate: {premium_predictions/total_games*100:.1f}%")
print(f"Confidence range: {min(confidence_levels):.1f}% - {max(confidence_levels):.1f}%")

print(f"\n💎 PREMIUM PREDICTIONS DISCOVERED:")
premium_games = []
for game_id, game_data in treasure.items():
    confidence = game_data.get('confidence', 0)
    if confidence > 50:
        premium_games.append((game_id, game_data))

premium_games.sort(key=lambda x: x[1].get('confidence', 0), reverse=True)

for i, (game_id, game_data) in enumerate(premium_games[:10]):
    date = game_data.get('date', '?')
    away = game_data.get('away_team', '?')
    home = game_data.get('home_team', '?')
    confidence = game_data.get('confidence', 0)
    away_score = game_data.get('away_score', '?')
    home_score = game_data.get('home_score', '?')
    
    print(f"{i+1:2d}. {date} - {away} @ {home}")
    print(f"    Confidence: {confidence}% | Predicted Score: {away_score}-{home_score}")

print(f"\n🏆 ARCHAEOLOGICAL SUCCESS!")
print(f"- Recovered {total_games} total predictions")
print(f"- Discovered {premium_predictions} premium predictions with confidence levels")
print(f"- Achieved {premium_predictions/total_games*100:.1f}% premium rate")
print(f"- Confidence levels range from {min(confidence_levels):.1f}% to {max(confidence_levels):.1f}%")

# Save to both locations
with open('MLB-Betting/unified_predictions_cache.json', 'w') as f:
    json.dump(treasure, f, indent=2)

print(f"\n💾 Archaeological treasure deployed to MLB-Betting system!")
print(f"🚀 Ready for system restart with complete data!")
