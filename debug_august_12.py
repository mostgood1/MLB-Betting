#!/usr/bin/env python3
"""
Debug August 12th Data Issues
"""

import json
from verify_game_recaps import GameRecapVerifier

def debug_august_12():
    """Debug the August 12th data discrepancy"""
    print("=== Debugging August 12th Data ===\n")
    
    verifier = GameRecapVerifier()
    result = verifier.check_game_recap_completeness('2025-08-12')
    
    print(f"Verification result:")
    print(f"  Total games: {result['total_games']}")
    print(f"  Games with predictions: {result['games_with_predictions']}")
    print(f"  Games with results: {result['games_with_results']}")
    print(f"  Complete recaps: {result['complete_recaps']}")
    
    print(f"\nMissing predictions ({len(result['missing_components']['predictions_only'])}):")
    for game in result['missing_components']['predictions_only']:
        print(f"  {game}")
    
    # Let's manually check the data
    print(f"\n=== Manual Data Check ===")
    
    # Load game scores
    with open('game_scores_cache.json', 'r') as f:
        scores_data = json.load(f)
    
    # Load predictions  
    with open('historical_predictions_cache.json', 'r') as f:
        pred_data = json.load(f)
    
    aug12_scores = scores_data.get('2025-08-12', {}).get('games', [])
    aug12_preds = pred_data.get('2025-08-12', {})
    
    print(f"Game scores file: {len(aug12_scores)} games")
    print(f"Predictions file: {len(aug12_preds)} entries")
    
    # Show game IDs from scores
    score_game_ids = [str(game['game_pk']) for game in aug12_scores]
    print(f"\nGame IDs from scores: {score_game_ids}")
    
    # Show prediction keys
    pred_keys = list(aug12_preds.keys())
    print(f"\nPrediction keys: {pred_keys}")
    
    # Extract game IDs from prediction keys
    pred_game_ids = []
    for key in pred_keys:
        if key.startswith('backfill_') or key.startswith('focused_fix_'):
            parts = key.split('_')
            if len(parts) >= 3:
                game_id = parts[-1]
                if game_id.isdigit():
                    pred_game_ids.append(game_id)
    
    print(f"\nGame IDs from predictions: {pred_game_ids}")
    
    # Find mismatches
    score_ids_set = set(score_game_ids)
    pred_ids_set = set(pred_game_ids)
    
    only_in_scores = score_ids_set - pred_ids_set
    only_in_preds = pred_ids_set - score_ids_set
    
    print(f"\nOnly in scores: {only_in_scores}")
    print(f"Only in predictions: {only_in_preds}")

if __name__ == "__main__":
    debug_august_12()
