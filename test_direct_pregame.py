#!/usr/bin/env python3
"""
Test the pregame betting function directly without the web interface
"""
import sys
import os
import json

# Set up the path
sys.path.insert(0, r'c:\Users\mostg\OneDrive\Coding\MLBCompare\mlb-clean-deploy')
os.chdir(r'c:\Users\mostg\OneDrive\Coding\MLBCompare\mlb-clean-deploy')

print("=== DIRECT PREGAME BETTING TEST ===")

try:
    print("1. Importing modules...")
    from complete_web_app import app, prediction_engine
    from datetime import datetime
    
    print(f"2. Prediction engine available: {prediction_engine is not None}")
    
    if not prediction_engine:
        print("ERROR: Prediction engine is not available!")
        sys.exit(1)
    
    print("3. Testing TodaysGames import...")
    from TodaysGames import get_games_for_date
    
    print("4. Getting today's games...")
    today_date = datetime.now().strftime('%Y-%m-%d')
    today_games = get_games_for_date(today_date, include_live_scores=False)
    
    print(f"5. Found {len(today_games) if today_games else 0} games for {today_date}")
    
    if not today_games:
        print("ERROR: No games found for today!")
        sys.exit(1)
    
    print("6. Testing first game prediction...")
    first_game = today_games[0]
    print(f"   Game: {first_game.get('away_team')} @ {first_game.get('home_team')}")
    print(f"   Pitchers: {first_game.get('away_pitcher', 'Unknown')} vs {first_game.get('home_pitcher', 'Unknown')}")
    
    print("7. Calling prediction engine...")
    prediction = prediction_engine.get_fast_prediction(
        away_team=first_game.get('away_team'),
        home_team=first_game.get('home_team'),
        away_pitcher=first_game.get('away_pitcher', 'Unknown'),
        home_pitcher=first_game.get('home_pitcher', 'Unknown'),
        sim_count=10,  # Very small count for testing
        game_date=today_date
    )
    
    print("8. Prediction result:")
    if prediction:
        print(f"   Prediction type: {type(prediction)}")
        print(f"   Prediction keys: {list(prediction.keys()) if isinstance(prediction, dict) else 'Not a dict'}")
        if isinstance(prediction, dict) and 'recommendations' in prediction:
            print(f"   Recommendations: {len(prediction['recommendations'])}")
        print(f"   Full prediction: {json.dumps(prediction, indent=2, default=str)}")
    else:
        print("   ERROR: Prediction returned None!")
    
    print("9. Testing web app with test client...")
    with app.test_client() as client:
        response = client.get('/api/pregame-betting')
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response keys: {list(data.keys())}")
            print(f"   Total games: {data.get('total_games')}")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
        else:
            print(f"   Error response: {response.get_data(as_text=True)}")
    
    print("\n=== TEST COMPLETE ===")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
