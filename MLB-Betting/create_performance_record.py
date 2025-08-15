"""
Simple Performance Tracker
=========================

Create and track basic performance metrics for the prediction engine.
"""

import json
import os
from datetime import datetime

def create_performance_record():
    """Create performance record from tuning results"""
    
    # Current metrics from tuning analysis
    current_metrics = {
        'score_mae': 2.51,
        'score_rmse': 3.23,
        'total_mae': 3.41,
        'win_accuracy': 0.543,
        'betting_roi': 0.0,
        'confidence_calibration': 0.318,
        'total_predictions': 83,
        'overall_grade': 'F - Needs Major Improvement'
    }
    
    # Create performance record
    record = {
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        **current_metrics
    }
    
    # Save to data directory
    os.makedirs('data', exist_ok=True)
    
    # Load existing records or create new
    perf_file = 'data/performance_history.json'
    performance_history = []
    
    if os.path.exists(perf_file):
        with open(perf_file, 'r') as f:
            performance_history = json.load(f)
    
    performance_history.append(record)
    
    # Save updated history
    with open(perf_file, 'w') as f:
        json.dump(performance_history, f, indent=2)
    
    print(f"✅ Performance record created")
    print(f"📊 Score MAE: {current_metrics['score_mae']:.2f}")
    print(f"🎯 Win Accuracy: {current_metrics['win_accuracy']:.1%}")
    print(f"💰 Betting ROI: {current_metrics['betting_roi']:.1f}%")
    print(f"🏆 Overall Grade: {current_metrics['overall_grade']}")
    
    return record

if __name__ == "__main__":
    create_performance_record()
