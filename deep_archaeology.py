import json

def deep_data_archaeology():
    """Perform deep data archaeology to find buried score predictions"""
    
    print("=== DEEP DATA ARCHAEOLOGY FOR SCORE PREDICTIONS ===")
    
    with open('historical_predictions_cache.json', 'r') as f:
        historical_data = json.load(f)
    
    dates_to_search = ['2025-08-07', '2025-08-08', '2025-08-09', '2025-08-10', '2025-08-11', '2025-08-12', '2025-08-13']
    
    score_predictions_found = {}
    
    for date in dates_to_search:
        if date not in historical_data:
            continue
            
        print(f"\n🔍 DEEP DIVE: {date}")
        date_data = historical_data[date]
        
        # 1. Check cached_predictions thoroughly
        cached_preds = date_data.get('cached_predictions', {})
        print(f"  Cached predictions: {len(cached_preds)}")
        
        if cached_preds:
            sample_game = list(cached_preds.values())[0]
            print(f"    Sample fields: {list(sample_game.keys())}")
            
            # Look for any field that might contain scores
            score_fields = [k for k in sample_game.keys() if 'score' in k.lower() or 'run' in k.lower() or 'point' in k.lower()]
            if score_fields:
                print(f"    🎯 Score-related fields found: {score_fields}")
                
                for field in score_fields:
                    sample_value = sample_game[field]
                    print(f"      {field}: {sample_value}")
            
            # Check for prediction data with actual values
            pred_fields = [k for k in sample_game.keys() if 'predict' in k.lower()]
            if pred_fields:
                print(f"    🎯 Prediction fields found: {pred_fields}")
                for field in pred_fields:
                    sample_value = sample_game[field]
                    print(f"      {field}: {sample_value}")
        
        # 2. Look for other prediction structures
        other_keys = [k for k in date_data.keys() if k not in ['cached_predictions', 'last_updated', 'summary'] and not k.startswith('backfill')]
        
        if other_keys:
            print(f"  🔍 Other data structures: {other_keys[:5]}")
            
            for key in other_keys[:3]:  # Check first 3
                other_data = date_data[key]
                if isinstance(other_data, dict):
                    print(f"    {key}: {list(other_data.keys())[:10]}")
                    
                    # Look for score-related data
                    if any('score' in str(k).lower() for k in other_data.keys()):
                        print(f"      🎯 SCORE DATA FOUND in {key}!")
                        score_keys = [k for k in other_data.keys() if 'score' in str(k).lower()]
                        print(f"        Score keys: {score_keys}")
        
        # 3. Look in specialized prediction entries
        prediction_keys = [k for k in date_data.keys() if 'predict' in k.lower() or 'forecast' in k.lower() or 'model' in k.lower()]
        
        if prediction_keys:
            print(f"  🎯 Prediction structures: {prediction_keys}")
            
            for pred_key in prediction_keys[:2]:
                pred_data = date_data[pred_key]
                if isinstance(pred_data, dict):
                    print(f"    {pred_key}: {list(pred_data.keys())[:10]}")

def search_for_score_patterns():
    """Search for score prediction patterns in all cache files"""
    
    print("\n" + "="*60)
    print("SEARCHING ALL CACHE FILES FOR SCORE PATTERNS")
    print("="*60)
    
    cache_files = [
        'historical_predictions_cache.json',
        'game_scores_cache.json',
        'unified_predictions_cache.json'
    ]
    
    for cache_file in cache_files:
        try:
            print(f"\n📁 Searching {cache_file}:")
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Search for score-related keys at any level
            score_findings = search_nested_dict(data, 'score')
            run_findings = search_nested_dict(data, 'run')
            predict_findings = search_nested_dict(data, 'predict')
            
            if score_findings:
                print(f"  🎯 Score patterns found: {len(score_findings)}")
                for finding in score_findings[:5]:  # Show first 5
                    print(f"    {finding}")
            
            if run_findings:
                print(f"  🎯 Run patterns found: {len(run_findings)}")
                for finding in run_findings[:5]:
                    print(f"    {finding}")
                    
            if predict_findings:
                print(f"  🎯 Predict patterns found: {len(predict_findings)}")
                for finding in predict_findings[:5]:
                    print(f"    {finding}")
                    
        except Exception as e:
            print(f"  ❌ Error reading {cache_file}: {e}")

def search_nested_dict(data, search_term, path=""):
    """Recursively search for keys containing search_term"""
    findings = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if search_term.lower() in str(key).lower():
                findings.append(f"{current_path}: {type(value).__name__}")
            
            # Recurse into nested structures (but limit depth)
            if isinstance(value, (dict, list)) and len(path.split('.')) < 4:
                findings.extend(search_nested_dict(value, search_term, current_path))
    
    elif isinstance(data, list) and len(data) > 0:
        # Check first item of lists
        if len(path.split('.')) < 4:
            findings.extend(search_nested_dict(data[0], search_term, f"{path}[0]"))
    
    return findings

if __name__ == "__main__":
    deep_data_archaeology()
    search_for_score_patterns()
