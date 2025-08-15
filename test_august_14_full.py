#!/usr/bin/env python3

import requests
import json

def test_august_14_full():
    """Test the full response structure for August 14th API"""
    
    url = "http://localhost:5000/api/historical-recap/2025-08-14"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Full API Response Structure:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        print("Make sure Flask app is running on localhost:5000")

if __name__ == "__main__":
    test_august_14_full()
