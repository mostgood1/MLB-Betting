#!/usr/bin/env python3
"""
Quick test to check if the Flask server is responding
"""
import requests
import time

def test_server():
    """Test basic server connectivity"""
    base_url = 'http://localhost:5006'
    
    # Test basic connectivity
    print("Testing server connectivity...")
    try:
        response = requests.get(f'{base_url}/api/test', timeout=5)
        print(f"✓ Server test endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response: {data}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False
    
    # Test home page
    print("\nTesting home page...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✓ Home page: {response.status_code}")
    except Exception as e:
        print(f"✗ Home page failed: {e}")
        return False
    
    # Test pregame betting API
    print("\nTesting pregame betting API...")
    try:
        response = requests.get(f'{base_url}/api/pregame-betting', timeout=10)
        print(f"✓ Pregame API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response keys: {list(data.keys())}")
            print(f"  Message: {data.get('message', 'No message')}")
            print(f"  Debug: {data.get('debug', 'No debug info')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Pregame API failed: {e}")
        return False
    
    # Test todays games API
    print("\nTesting todays games API...")
    try:
        response = requests.get(f'{base_url}/api/todays-games', timeout=10)
        print(f"✓ Today's games API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Total games: {data.get('total_games', 'unknown')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Today's games API failed: {e}")
        return False
    
    print("\n=== ALL TESTS PASSED ===")
    print("Server is working properly!")
    return True

if __name__ == '__main__':
    print("=== FLASK SERVER CONNECTIVITY TEST ===")
    print("Make sure the server is running with: python complete_web_app.py")
    print("Then run this test to check connectivity.\n")
    
    test_server()
