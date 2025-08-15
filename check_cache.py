import json

# Load and analyze the main cache
with open('unified_predictions_cache.json', 'r') as f:
    data = json.load(f)

print(f"🏺 ARCHAEOLOGICAL TREASURE ANALYSIS")
print(f"==================================")
print(f"Total entries: {len(data)}")

premium_count = sum(1 for game in data.values() if game.get('confidence', 0) > 50)
print(f"Premium predictions: {premium_count}")

# Show sample entries
print(f"\n📊 Sample entries:")
for i, (game_id, game_data) in enumerate(data.items()):
    date = game_data.get('date', 'No date')
    away = game_data.get('away_team', '?')
    home = game_data.get('home_team', '?')
    confidence = game_data.get('confidence', 0)
    print(f"  {game_id}: {date} - {away} @ {home} (confidence: {confidence}%)")
    if i >= 4:
        break

# Check dates available
dates = set()
for game_data in data.values():
    if game_data.get('date'):
        dates.add(game_data.get('date'))

print(f"\n📅 Dates covered: {sorted(dates)}")
print(f"Date range: {len(dates)} unique dates")
