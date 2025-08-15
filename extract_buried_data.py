import json
from datetime import datetime

def extract_buried_predictions():
    """Extract buried prediction data from backfill entries in historical cache"""
    
    with open('historical_predictions_cache.json', 'r') as f:
        historical_data = json.load(f)
    
    print("=== SEARCHING FOR BURIED PREDICTION DATA ===")
    
    buried_predictions = {}
    missing_dates = ['2025-08-11', '2025-08-12', '2025-08-13']
    
    for date in missing_dates:
        if date not in historical_data:
            print(f"❌ {date}: No data in historical cache")
            continue
        
        date_data = historical_data[date]
        
        # Check cached_predictions first
        cached_preds = date_data.get('cached_predictions', {})
        print(f"\n📅 {date}:")
        print(f"  Cached predictions: {len(cached_preds)}")
        
        # Look for backfill entries
        backfill_keys = [k for k in date_data.keys() if 'backfill' in k]
        print(f"  Backfill entries: {len(backfill_keys)}")
        
        if backfill_keys:
            buried_predictions[date] = {
                'games': {},
                'source': 'backfill',
                'count': len(backfill_keys)
            }
            
            for backfill_key in backfill_keys:
                backfill_data = date_data[backfill_key]
                
                if all(k in backfill_data for k in ['away_team', 'home_team', 'away_win_pct', 'home_win_pct']):
                    away_team = backfill_data['away_team']
                    home_team = backfill_data['home_team']
                    game_key = f"{away_team} @ {home_team}"
                    
                    # Convert to our unified format
                    game_prediction = {
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_win_probability': backfill_data.get('away_win_pct'),
                        'home_win_probability': backfill_data.get('home_win_pct'),
                        'away_pitcher': backfill_data.get('away_pitcher', 'TBD'),
                        'home_pitcher': backfill_data.get('home_pitcher', 'TBD'),
                        'game_id': backfill_data.get('game_id'),
                        'prediction_time': backfill_data.get('prediction_time'),
                        'model_version': backfill_data.get('model_version', 'backfill-1.0'),
                        'source': 'historical_backfill',
                        # Generate estimated scores based on win probabilities
                        'predicted_away_score': 4.0 + (backfill_data.get('away_win_pct', 0.5) - 0.5) * 2,
                        'predicted_home_score': 4.0 + (backfill_data.get('home_win_pct', 0.5) - 0.5) * 2,
                        'predicted_total_runs': 8.0,
                        'estimated_scores': True  # Flag to indicate these are estimated
                    }
                    
                    buried_predictions[date]['games'][game_key] = game_prediction
                    print(f"    ✅ {game_key}: Win probs {backfill_data['away_win_pct']:.1%}/{backfill_data['home_win_pct']:.1%}")
    
    return buried_predictions

def create_buried_data_report():
    """Create a report of all buried prediction data found"""
    
    buried_data = extract_buried_predictions()
    
    print(f"\n" + "="*60)
    print("BURIED PREDICTION DATA SUMMARY")
    print("="*60)
    
    total_buried_games = 0
    
    for date, date_info in buried_data.items():
        game_count = len(date_info['games'])
        total_buried_games += game_count
        
        print(f"\n📅 {date}: {game_count} games recovered from {date_info['source']}")
        
        if game_count > 0:
            print("   Sample games:")
            for i, (game_key, game_data) in enumerate(list(date_info['games'].items())[:3]):
                away_prob = game_data['away_win_probability']
                home_prob = game_data['home_win_probability']
                print(f"     {i+1}. {game_key}")
                print(f"        Win probs: {away_prob:.1%} / {home_prob:.1%}")
                print(f"        Pitchers: {game_data['away_pitcher']} vs {game_data['home_pitcher']}")
    
    print(f"\n🎯 TOTAL BURIED GAMES FOUND: {total_buried_games}")
    
    if total_buried_games > 0:
        # Save the buried data
        with open('buried_predictions_extracted.json', 'w') as f:
            json.dump(buried_data, f, indent=2)
        
        print(f"💾 Buried data saved to: buried_predictions_extracted.json")
        print("\nNEXT STEPS:")
        print("1. Review the extracted data")
        print("2. Integrate with unified cache")
        print("3. Test the restored predictions")
    
    return buried_data

if __name__ == "__main__":
    buried_data = create_buried_data_report()
    
    if buried_data:
        print(f"\n🎉 SUCCESS: Found buried prediction data for {len(buried_data)} missing dates!")
        print("This data includes win probabilities and pitcher information.")
        print("Score predictions are estimated based on win probabilities.")
    else:
        print("\n❌ No buried prediction data found in backfill entries.")
