#!/usr/bin/env python3

import requests
import json

def test_august_14_api():
    """Test what the Flask API returns for August 14th"""
    
    url = "http://localhost:5000/api/historical-recap/2025-08-14"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('games', [])
            print(f"Total games returned: {len(games)}")
            
            for i, game in enumerate(games, 1):
                away_team = game.get('away_team', 'Unknown')
                home_team = game.get('home_team', 'Unknown')
                status = game.get('result', {}).get('status', 'Unknown')
                
                print(f"{i}. {away_team} @ {home_team} - Status: {status}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        print("Make sure Flask app is running on localhost:5000")

if __name__ == "__main__":
    test_august_14_api()
