"""
Track Performance of Optimized Predictions
==========================================

Record today's optimized predictions for future validation.
"""

import json
from datetime import datetime

def record_optimized_predictions():
    """Record today's predictions with optimization metadata"""
    
    # Load today's optimized predictions
    with open('data/unified_predictions_cache.json', 'r') as f:
        data = json.load(f)
    
    today_predictions = data['predictions_by_date']['2025-08-15']['games']
    
    # Create performance tracking record
    tracking_record = {
        'date': '2025-08-15',
        'timestamp': datetime.now().isoformat(),
        'optimization_applied': True,
        'optimization_version': '1.1_optimized',
        'improvements_applied': [
            'Pitcher ERA weight: 0.35 → 0.45 (+29%)',
            'Home field advantage: 0.15 → 0.20 (+33%)',
            'Minimum edge threshold: 5% → 8% (+60%)',
            'High confidence threshold: 0.65 → 0.70 (+8%)'
        ],
        'prediction_count': len(today_predictions),
        'expected_improvements': {
            'score_mae_target': 1.8,  # Down from 2.51
            'win_accuracy_target': 0.58,  # Up from 0.543
            'betting_roi_target': 0.05  # Up from 0.0
        },
        'games': {}
    }
    
    # Record individual game predictions for later validation
    for game_key, game_data in today_predictions.items():
        tracking_record['games'][game_key] = {
            'predicted_away_score': game_data.get('predicted_away_score'),
            'predicted_home_score': game_data.get('predicted_home_score'),
            'predicted_total_runs': game_data.get('predicted_total_runs'),
            'home_win_probability': game_data.get('home_win_probability'),
            'confidence_level': game_data.get('confidence_level'),
            'betting_recommendations': game_data.get('comprehensive_details', {}).get('betting_recommendations', [])
        }
    
    # Save tracking record
    tracking_file = f"optimization_tracking_{datetime.now().strftime('%Y%m%d')}.json"
    with open(tracking_file, 'w') as f:
        json.dump(tracking_record, f, indent=2)
    
    print("📊 OPTIMIZED PREDICTIONS TRACKING RECORD")
    print("="*50)
    print(f"📅 Date: {tracking_record['date']}")
    print(f"🎯 Games Tracked: {tracking_record['prediction_count']}")
    print(f"⚡ Optimizations Applied: {len(tracking_record['improvements_applied'])}")
    print()
    
    print("🎯 Expected Performance Improvements:")
    print(f"  📈 Score MAE: 2.51 → {tracking_record['expected_improvements']['score_mae_target']}")
    print(f"  🏆 Win Accuracy: 54.3% → {tracking_record['expected_improvements']['win_accuracy_target']:.1%}")
    print(f"  💰 Betting ROI: 0% → {tracking_record['expected_improvements']['betting_roi_target']:.1%}")
    
    print()
    print("✅ Tracking record saved:", tracking_file)
    print("🔍 Use this data to validate optimization effectiveness")
    
    return tracking_record

if __name__ == "__main__":
    record_optimized_predictions()
