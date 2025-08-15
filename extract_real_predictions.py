import json
from datetime import datetime

def extract_real_score_predictions():
    """Extract the real detailed score predictions from buried cache structures"""
    
    print("=== EXTRACTING REAL SCORE PREDICTIONS ===")
    
    with open('historical_predictions_cache.json', 'r') as f:
        historical_data = json.load(f)
    
    extracted_predictions = {}
    total_games_found = 0
    
    # Target dates with real prediction data
    target_dates = ['2025-08-07', '2025-08-08', '2025-08-10', '2025-08-11']
    
    for date in target_dates:
        if date not in historical_data:
            continue
            
        print(f"\n📅 {date}:")
        
        cached_preds = historical_data[date].get('cached_predictions', {})
        
        if not cached_preds:
            print(f"  ❌ No cached predictions")
            continue
        
        extracted_predictions[date] = {'games': {}}
        date_count = 0
        
        for game_key, game_data in cached_preds.items():
            # Look for the predictions sub-structure
            predictions = game_data.get('predictions', {})
            
            if predictions and isinstance(predictions, dict):
                # Extract real prediction data
                real_pred = {}
                
                # Score predictions
                if 'predicted_away_score' in predictions:
                    real_pred['predicted_away_score'] = predictions['predicted_away_score']
                if 'predicted_home_score' in predictions:
                    real_pred['predicted_home_score'] = predictions['predicted_home_score']
                if 'predicted_total_runs' in predictions:
                    real_pred['predicted_total_runs'] = predictions['predicted_total_runs']
                
                # Win probabilities
                if 'away_win_prob' in predictions:
                    real_pred['away_win_probability'] = predictions['away_win_prob']
                if 'home_win_prob' in predictions:
                    real_pred['home_win_probability'] = predictions['home_win_prob']
                
                # Additional valuable data
                if 'confidence' in predictions:
                    real_pred['confidence'] = predictions['confidence']
                if 'home_score_range' in predictions:
                    real_pred['home_score_range'] = predictions['home_score_range']
                if 'away_score_range' in predictions:
                    real_pred['away_score_range'] = predictions['away_score_range']
                
                # Team and meta data
                real_pred['away_team'] = game_data.get('away_team', '')
                real_pred['home_team'] = game_data.get('home_team', '')
                real_pred['source'] = 'real_predictions_cache'
                real_pred['extraction_method'] = 'deep_archaeology'
                
                if real_pred.get('predicted_away_score') is not None:
                    game_key_normalized = f"{real_pred['away_team']} @ {real_pred['home_team']}"
                    extracted_predictions[date]['games'][game_key_normalized] = real_pred
                    date_count += 1
                    
                    pred_score = f"{real_pred.get('predicted_away_score', 'N/A')}-{real_pred.get('predicted_home_score', 'N/A')}"
                    win_probs = f"{real_pred.get('away_win_probability', 0):.1%}/{real_pred.get('home_win_probability', 0):.1%}"
                    confidence = real_pred.get('confidence', 'N/A')
                    
                    print(f"  ✅ {game_key_normalized}: {pred_score} (WP: {win_probs}, Conf: {confidence}%)")
        
        total_games_found += date_count
        print(f"  📊 Found {date_count} real predictions for {date}")
    
    print(f"\n🎯 TOTAL REAL PREDICTIONS EXTRACTED: {total_games_found}")
    
    # Save extracted data
    with open('real_score_predictions_extracted.json', 'w') as f:
        json.dump(extracted_predictions, f, indent=2)
    
    print(f"💾 Real predictions saved to: real_score_predictions_extracted.json")
    
    return extracted_predictions

def compare_prediction_quality():
    """Compare the quality of different prediction sources"""
    
    print(f"\n" + "="*60)
    print("PREDICTION QUALITY COMPARISON")
    print("="*60)
    
    with open('real_score_predictions_extracted.json', 'r') as f:
        real_preds = json.load(f)
    
    with open('buried_predictions_extracted.json', 'r') as f:
        buried_preds = json.load(f)
    
    print("\n📊 DATA SOURCE COMPARISON:")
    
    for date in sorted(set(list(real_preds.keys()) + list(buried_preds.keys()))):
        print(f"\n📅 {date}:")
        
        real_count = len(real_preds.get(date, {}).get('games', {}))
        buried_count = len(buried_preds.get(date, {}).get('games', {}))
        
        print(f"  Real predictions: {real_count} games")
        print(f"  Buried predictions: {buried_count} games")
        
        if real_count > 0:
            sample_real = list(real_preds[date]['games'].values())[0]
            print(f"  Real quality: Score predictions + confidence + ranges")
            print(f"    Confidence: {sample_real.get('confidence', 'N/A')}%")
            print(f"    Score range: {sample_real.get('away_score_range', 'N/A')}")
        
        if buried_count > 0:
            sample_buried = list(buried_preds[date]['games'].values())[0]
            print(f"  Buried quality: Win probabilities only")
            print(f"    Win prob: {sample_buried.get('away_win_probability', 'N/A'):.1%}")

def create_integration_plan():
    """Create a plan to integrate the best prediction data"""
    
    print(f"\n" + "="*60)
    print("INTEGRATION STRATEGY")
    print("="*60)
    
    print("\n🎯 RECOMMENDATION:")
    print("1. Aug 7-8, 10-11: Use REAL predictions (higher quality)")
    print("2. Aug 9: Keep existing restored predictions") 
    print("3. Aug 12-13: Use buried predictions (only available source)")
    print("4. Aug 14: Keep current predictions")
    
    print(f"\n✨ EXPECTED FINAL COVERAGE:")
    print("- Aug 7-8: 100% with REAL detailed predictions")
    print("- Aug 9: 100% with restored predictions") 
    print("- Aug 10: Partial with REAL predictions + buried")
    print("- Aug 11: 100% with REAL detailed predictions")
    print("- Aug 12-13: 100% with buried predictions")
    print("- Aug 14: 100% with current predictions")
    
    return True

if __name__ == "__main__":
    real_predictions = extract_real_score_predictions()
    compare_prediction_quality()
    create_integration_plan()
    
    if real_predictions:
        print(f"\n🏆 SUCCESS: Extracted real detailed predictions!")
        print("These predictions include confidence levels and score ranges.")
        print("Ready to integrate the highest quality prediction data!")
