#!/usr/bin/env python3

import sys
import os
import json

# Add the parent directory to the path so we can import from MLB-Betting
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MLB-Betting'))

# Now we can import the integration module
from integrated_closing_lines import IntegratedClosingLinesManager

def test_enhanced_data_integration():
    """Test if the enhanced data integration works directly"""
    print("DIRECT INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Create the closing lines manager
        manager = IntegratedClosingLinesManager()
        print(f"SUCCESS: Closing lines manager created successfully")
        
        # Call the method that should use enhanced data
        date = '2025-08-14'
        print(f"Testing get_games_with_closing_lines for {date}")
        
        games_with_lines = manager.get_games_with_closing_lines(date)
        print(f"📊 Retrieved {len(games_with_lines)} games")
        
        if not games_with_lines:
            print("ERROR: No games returned!")
            return
        
        # Check the first game for pitcher information
        first_game = games_with_lines[0]
        print(f"\n🏟️  First Game Analysis:")
        print(f"   Away: {first_game.get('away_team', 'Unknown')}")
        print(f"   Home: {first_game.get('home_team', 'Unknown')}")
        print(f"   Away Pitcher: {first_game.get('away_pitcher', 'Missing')}")
        print(f"   Home Pitcher: {first_game.get('home_pitcher', 'Missing')}")
        
        # Count games with real pitcher data
        real_pitcher_count = 0
        for game in games_with_lines:
            away_pitcher = game.get('away_pitcher', '')
            home_pitcher = game.get('home_pitcher', '')
            
            if (away_pitcher and away_pitcher not in ['TBD', 'Missing', None] and
                home_pitcher and home_pitcher not in ['TBD', 'Missing', None]):
                real_pitcher_count += 1
        
        print(f"\n📈 RESULTS:")
        print(f"   Total games: {len(games_with_lines)}")
        print(f"   Games with real pitchers: {real_pitcher_count}")
        print(f"   Success rate: {real_pitcher_count}/{len(games_with_lines)}")
        
        if real_pitcher_count == len(games_with_lines):
            print("🏆 PERFECT! All games have real pitcher data!")
            print("SUCCESS: Enhanced data integration is working correctly!")
        elif real_pitcher_count > 0:
            print(f"⚠️  Partial success: {real_pitcher_count} games have real pitcher data")
        else:
            print("FAILURE: No games have real pitcher data")
            print("Enhanced data integration is not working")
        
        return real_pitcher_count == len(games_with_lines)
        
    except Exception as e:
        print(f"ERROR: Error during integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_data_integration()
    if success:
        print("\n🎯 Integration test PASSED")
    else:
        print("\nIntegration test FAILED")
