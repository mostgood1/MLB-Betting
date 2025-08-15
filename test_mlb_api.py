#!/usr/bin/env python3
"""
MLB API Integration Test Script

This script tests the MLB API integration for a single date
and displays the results.
"""

import sys
import json
import os
from mlb_api_integration import MLBApiIntegration
from datetime import datetime, timedelta

def test_single_date(date=None):
    """Test the MLB API integration for a single date"""
    if not date:
        # Use yesterday's date for testing
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"=== Testing MLB API Integration for {date} ===")
    
    # Initialize the integrator
    integrator = MLBApiIntegration()
    
    # Fetch data from MLB API
    mlb_games = integrator.fetch_mlb_api_data(date)
    
    if not mlb_games:
        print(f"No games found for {date}")
        return False
    
    print(f"Found {len(mlb_games)} games for {date}")
    
    # Process one game as an example
    if mlb_games:
        game = mlb_games[0]
        game_id = game.get('gamePk', '')
        
        teams = game.get('teams', {})
        away_team = teams.get('away', {}).get('team', {}).get('name', '')
        home_team = teams.get('home', {}).get('team', {}).get('name', '')
        
        # Get pitcher info
        away_pitcher = "TBD"
        away_pitcher_data = teams.get('away', {}).get('probablePitcher', {})
        if away_pitcher_data:
            away_pitcher = away_pitcher_data.get('fullName', 'TBD')
        
        home_pitcher = "TBD"
        home_pitcher_data = teams.get('home', {}).get('probablePitcher', {})
        if home_pitcher_data:
            home_pitcher = home_pitcher_data.get('fullName', 'TBD')
        
        print("\nExample Game:")
        print(f"  Game ID: {game_id}")
        print(f"  Matchup: {away_team} @ {home_team}")
        print(f"  Away Pitcher: {away_pitcher}")
        print(f"  Home Pitcher: {home_pitcher}")
        
        # Display the normalized format
        normalized = integrator.convert_to_normalized_format(game, date)
        print("\nNormalized Format:")
        print(json.dumps(normalized, indent=2))
        
        # Display the game scores format
        game_scores = integrator.convert_to_game_scores_format(game, date)
        print("\nGame Scores Format:")
        print(json.dumps(game_scores, indent=2))
    
    return True

def main():
    """Main function"""
    date = None
    
    if len(sys.argv) > 1:
        date = sys.argv[1]
        try:
            # Validate date format
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("Error: Date must be in YYYY-MM-DD format")
            return False
    
    return test_single_date(date)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
