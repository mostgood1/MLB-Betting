import json

# Load our treasure and fix the structure
with open('archaeological_treasure_unified.json', 'r') as f:
    treasure = json.load(f)

print("🏺 FIXING ARCHAEOLOGICAL TREASURE STRUCTURE")
print("===========================================")

fixed_treasure = {}
total_games = 0
premium_count = 0

for game_id, game_data in treasure.items():
    if isinstance(game_data, dict):
        # Create a clean game entry
        clean_game = {
            'date': game_data.get('date', 'Unknown'),
            'away_team': game_data.get('away_team', ''),
            'home_team': game_data.get('home_team', ''),
        }
        
        # Check if predictions are nested
        predictions = game_data.get('predictions', {})
        if predictions:
            # Extract from nested structure
            clean_game.update({
                'home_win_probability': predictions.get('home_win_prob', 0) * 100,
                'away_win_probability': predictions.get('away_win_prob', 0) * 100,
                'home_score': predictions.get('predicted_home_score', 0),
                'away_score': predictions.get('predicted_away_score', 0),
                'total_score': predictions.get('predicted_total_runs', 0),
                'confidence': predictions.get('confidence', 0)
            })
        else:
            # Extract from top level
            clean_game.update({
                'home_win_probability': game_data.get('home_win_probability', 0),
                'away_win_probability': game_data.get('away_win_probability', 0),
                'home_score': game_data.get('home_score', 0),
                'away_score': game_data.get('away_score', 0),
                'total_score': game_data.get('total_score', 0),
                'confidence': game_data.get('confidence', 0)
            })
        
        # Set predicted winner
        if clean_game['home_win_probability'] > clean_game['away_win_probability']:
            clean_game['predicted_winner'] = clean_game['home_team']
        else:
            clean_game['predicted_winner'] = clean_game['away_team']
        
        # Only add if it has team names
        if clean_game['away_team'] and clean_game['home_team']:
            fixed_treasure[game_id] = clean_game
            total_games += 1
            
            if clean_game['confidence'] > 50:
                premium_count += 1

print(f"Total games processed: {total_games}")
print(f"Premium predictions: {premium_count}")
print(f"Premium rate: {premium_count/total_games*100:.1f}%")

# Show some premium examples
premium_games = [(gid, game) for gid, game in fixed_treasure.items() if game['confidence'] > 50]
premium_games.sort(key=lambda x: x[1]['confidence'], reverse=True)

print(f"\n💎 TOP PREMIUM PREDICTIONS:")
for i, (game_id, game) in enumerate(premium_games[:5]):
    print(f"{i+1}. {game['date']} - {game['away_team']} @ {game['home_team']}")
    print(f"   Confidence: {game['confidence']}% | Score: {game['away_score']:.1f}-{game['home_score']:.1f}")

# Save the fixed treasure
with open('archaeological_treasure_fixed.json', 'w') as f:
    json.dump(fixed_treasure, f, indent=2)

with open('MLB-Betting/unified_predictions_cache.json', 'w') as f:
    json.dump(fixed_treasure, f, indent=2)

print(f"\n🏆 ARCHAEOLOGICAL RESTORATION COMPLETE!")
print(f"Fixed treasure saved and deployed to MLB-Betting!")
print(f"System ready with {total_games} games and {premium_count} premium predictions!")
