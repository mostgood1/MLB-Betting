#!/usr/bin/env python3
"""
Debug script for historical recap API matching issues
"""

import sys
import os
import json

# Add the MLB-Betting directory to path
sys.path.append(r'C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting')

from historical_recap_api import add_historical_recap_endpoints
from flask import Flask

def debug_matching():
    """Debug the team name matching logic"""
    
    # Create app and test
    app = Flask(__name__)
    add_historical_recap_endpoints(app)
    
    with app.test_client() as client:
        print("Testing historical recap API for 2025-08-08...")
        response = client.get('/api/historical-recap/2025-08-08')
        data = response.get_json()
        
        if data and data.get('success'):
            games = data.get('games', [])  # Games are at root level, not under 'data'
            print(f"Total games returned: {len(games)}")
            
            # Print the actual response structure
            print(f"Response keys: {list(data.keys())}")
            if 'summary' in data:
                summary = data['summary']
                print(f"Summary: {summary}")
            
            with_predictions = sum(1 for g in games if g.get('has_prediction'))
            with_results = sum(1 for g in games if g.get('has_result'))
            complete = sum(1 for g in games if g.get('is_complete_recap'))
            
            print(f"Games with predictions: {with_predictions}")
            print(f"Games with results: {with_results}")
            print(f"Complete recaps: {complete}")
            
            # Show a sample game
            if games:
                print("\nFirst game:")
                first = games[0]
                print(f"  Away: {first.get('away_team')}")
                print(f"  Home: {first.get('home_team')}")
                print(f"  Has prediction: {first.get('has_prediction')}")
                print(f"  Has result: {first.get('has_result')}")
                
                if first.get('prediction'):
                    pred = first['prediction']
                    print(f"  Predicted: {pred.get('predicted_away_score')}-{pred.get('predicted_home_score')}")
                
                if first.get('result'):
                    result = first['result']
                    print(f"  Actual: {result.get('away_score')}-{result.get('home_score')}")
        else:
            print("API call failed!")

if __name__ == "__main__":
    debug_matching()
