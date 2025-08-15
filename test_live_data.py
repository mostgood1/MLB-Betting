#!/usr/bin/env python3

import sys
sys.path.append('MLB-Betting')

from live_mlb_data import get_live_game_status

def test_live_data():
    """Test what the live MLB data source is returning for Arizona @ Colorado"""
    
    # Test the specific game that shows as delayed
    result = get_live_game_status("Arizona Diamondbacks", "Colorado Rockies", "2025-08-14")
    
    print("Live MLB Data Result:")
    print("=" * 50)
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_live_data()
