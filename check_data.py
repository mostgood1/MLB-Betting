import json
import os

try:
    # Get current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Path to the historical predictions file
    pred_file = 'historical_predictions_cache.json'
    if not os.path.exists(pred_file):
        print(f"File not found: {pred_file}")
        exit(1)
        
    # Load the file
    with open(pred_file, 'r') as f:
        data = json.load(f)
    
    # Print available dates
    dates = sorted(data.keys())
    print(f"Available dates in historical predictions: {dates}")
    
    # Check if today's date exists
    today = "2025-08-13"
    if today in data:
        print(f"Today's date ({today}) exists in the data")
        print(f"Structure for today: {list(data[today].keys())}")
        
        # Check if the structure is different
        if 'cached_predictions' not in data[today]:
            print(f"Warning: 'cached_predictions' key missing for {today}")
            print(f"Keys in today's data: {list(data[today].keys())}")
            
            # If it's a direct mapping of game_id -> predictions
            if len(data[today]) > 0:
                first_key = next(iter(data[today]))
                print(f"Example game key: {first_key}")
                print(f"Example game structure: {list(data[today][first_key].keys()) if isinstance(data[today][first_key], dict) else 'not a dict'}")
        else:
            # Print game keys
            games = list(data[today]['cached_predictions'].keys())
            print(f"Games: {games[:5]}...")  # Show first 5 games
    else:
        print(f"Today's date ({today}) does NOT exist in the data")
        print(f"Most recent date: {dates[-1]}")
        
    # Check betting lines file
    lines_file = 'historical_betting_lines_cache.json'
    if not os.path.exists(lines_file):
        print(f"File not found: {lines_file}")
    else:
        with open(lines_file, 'r') as f:
            lines_data = json.load(f)
        
        # Print available dates
        lines_dates = sorted(lines_data.keys())
        print(f"Available dates in betting lines: {lines_dates}")
        
        # Check if today's date exists
        if today in lines_data:
            print(f"Today's date ({today}) exists in the betting lines")
            print(f"Number of games with betting lines: {len(lines_data[today])}")
        else:
            print(f"Today's date ({today}) does NOT exist in the betting lines")
            print(f"Most recent date with betting lines: {lines_dates[-1]}")
    
except Exception as e:
    print(f"Error: {str(e)}")
