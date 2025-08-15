import json
from datetime import datetime

def integrate_premium_predictions():
    """Integrate the premium real predictions into the unified cache"""
    
    print("=== INTEGRATING PREMIUM REAL PREDICTIONS ===")
    
    # Load all data sources
    with open('unified_predictions_cache.json', 'r') as f:
        unified_data = json.load(f)
    
    with open('real_score_predictions_extracted.json', 'r') as f:
        real_predictions = json.load(f)
    
    with open('buried_predictions_extracted.json', 'r') as f:
        buried_predictions = json.load(f)
    
    upgrade_count = 0
    new_count = 0
    
    # Integration priority:
    # 1. Real predictions (highest quality)
    # 2. Buried predictions (for missing dates)
    # 3. Keep existing (for Aug 9, 14)
    
    for date in sorted(real_predictions.keys()):
        print(f"\n📅 {date}:")
        
        if date not in unified_data:
            unified_data[date] = {'games': []}
        
        real_games = real_predictions[date]['games']
        
        for game_key, real_pred in real_games.items():
            # Find matching game in unified data
            found_match = False
            
            for i, existing_game in enumerate(unified_data[date]['games']):
                existing_key = f"{existing_game['away_team']} @ {existing_game['home_team']}"
                
                if existing_key == game_key or (
                    existing_game['away_team'] in game_key and 
                    existing_game['home_team'] in game_key
                ):
                    # UPGRADE existing prediction with real data
                    original_source = existing_game.get('prediction_source', 'unknown')
                    
                    existing_game.update({
                        'predicted_away_score': real_pred['predicted_away_score'],
                        'predicted_home_score': real_pred['predicted_home_score'],
                        'predicted_total_runs': real_pred['predicted_total_runs'],
                        'away_win_probability': real_pred['away_win_probability'],
                        'home_win_probability': real_pred['home_win_probability'],
                        'confidence': real_pred['confidence'],
                        'prediction_source': 'real_predictions_premium',
                        'previous_source': original_source,
                        'upgrade_timestamp': datetime.now().isoformat(),
                        'quality_level': 'premium'
                    })
                    
                    # Add score ranges if available
                    if 'away_score_range' in real_pred:
                        existing_game['away_score_range'] = real_pred['away_score_range']
                    if 'home_score_range' in real_pred:
                        existing_game['home_score_range'] = real_pred['home_score_range']
                    
                    upgrade_count += 1
                    found_match = True
                    
                    print(f"  ⬆️ UPGRADED: {game_key}")
                    print(f"    {original_source} → real_predictions_premium")
                    print(f"    Score: {real_pred['predicted_away_score']:.1f}-{real_pred['predicted_home_score']:.1f}")
                    print(f"    Confidence: {real_pred['confidence']:.1f}%")
                    break
            
            if not found_match:
                # ADD new real prediction
                new_game = {
                    'away_team': real_pred['away_team'],
                    'home_team': real_pred['home_team'],
                    'predicted_away_score': real_pred['predicted_away_score'],
                    'predicted_home_score': real_pred['predicted_home_score'],
                    'predicted_total_runs': real_pred['predicted_total_runs'],
                    'away_win_probability': real_pred['away_win_probability'],
                    'home_win_probability': real_pred['home_win_probability'],
                    'confidence': real_pred['confidence'],
                    'prediction_source': 'real_predictions_premium',
                    'quality_level': 'premium',
                    'added_timestamp': datetime.now().isoformat()
                }
                
                if 'away_score_range' in real_pred:
                    new_game['away_score_range'] = real_pred['away_score_range']
                if 'home_score_range' in real_pred:
                    new_game['home_score_range'] = real_pred['home_score_range']
                
                unified_data[date]['games'].append(new_game)
                new_count += 1
                
                print(f"  ✅ ADDED: {game_key}")
                print(f"    Score: {real_pred['predicted_away_score']:.1f}-{real_pred['predicted_home_score']:.1f}")
                print(f"    Confidence: {real_pred['confidence']:.1f}%")
    
    # Add remaining buried predictions for Aug 12-13
    print(f"\n🔄 Adding buried predictions for missing dates...")
    
    for date in ['2025-08-12', '2025-08-13']:
        if date in buried_predictions:
            if date not in unified_data:
                unified_data[date] = {'games': []}
            
            buried_games = buried_predictions[date]['games']
            date_added = 0
            
            for game_key, buried_pred in buried_games.items():
                # Check if already exists
                found = False
                for existing_game in unified_data[date]['games']:
                    existing_key = f"{existing_game['away_team']} @ {existing_game['home_team']}"
                    if existing_key == game_key:
                        found = True
                        break
                
                if not found:
                    unified_data[date]['games'].append(buried_pred)
                    date_added += 1
            
            print(f"  📅 {date}: Added {date_added} buried predictions")
    
    print(f"\n🎯 INTEGRATION SUMMARY:")
    print(f"  ⬆️ Upgraded predictions: {upgrade_count}")
    print(f"  ✅ New predictions added: {new_count}")
    print(f"  🏆 Total premium predictions: {upgrade_count + new_count}")
    
    # Calculate final coverage
    coverage_report = {}
    total_games = 0
    total_with_scores = 0
    premium_count = 0
    
    for date, data in unified_data.items():
        if isinstance(data, dict) and 'games' in data:
            games = data['games']
            with_scores = sum(1 for g in games if g.get('predicted_away_score') is not None)
            premium = sum(1 for g in games if g.get('quality_level') == 'premium')
            
            coverage_report[date] = {
                'total': len(games),
                'with_scores': with_scores,
                'premium': premium,
                'coverage_pct': (with_scores / len(games) * 100) if games else 0
            }
            
            total_games += len(games)
            total_with_scores += with_scores
            premium_count += premium
    
    print(f"\n📊 FINAL COVERAGE REPORT:")
    for date in sorted(coverage_report.keys()):
        stats = coverage_report[date]
        print(f"  📅 {date}: {stats['with_scores']}/{stats['total']} ({stats['coverage_pct']:.1f}%) - {stats['premium']} premium")
    
    overall_coverage = (total_with_scores / total_games * 100) if total_games else 0
    premium_pct = (premium_count / total_games * 100) if total_games else 0
    
    print(f"\n🏆 OVERALL METRICS:")
    print(f"  📊 Coverage: {total_with_scores}/{total_games} ({overall_coverage:.1f}%)")
    print(f"  💎 Premium: {premium_count}/{total_games} ({premium_pct:.1f}%)")
    
    # Save upgraded unified cache
    with open('unified_predictions_cache.json', 'w') as f:
        json.dump(unified_data, f, indent=2)
    
    print(f"\n💾 Upgraded unified cache saved!")
    
    return {
        'upgraded': upgrade_count,
        'added': new_count,
        'total_coverage': overall_coverage,
        'premium_coverage': premium_pct
    }

if __name__ == "__main__":
    results = integrate_premium_predictions()
    
    print(f"\n🎉 ARCHAEOLOGICAL INTEGRATION COMPLETE!")
    print(f"We've successfully upgraded our prediction system with:")
    print(f"  💎 {results['upgraded']} premium upgrades")
    print(f"  ✅ {results['added']} new predictions")
    print(f"  📊 {results['total_coverage']:.1f}% total coverage")
    print(f"  🏆 {results['premium_coverage']:.1f}% premium quality!")
