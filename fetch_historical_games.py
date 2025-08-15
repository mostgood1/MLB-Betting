#!/usr/bin/env python3
"""
Historical Game Results Fetcher

This script fetches historical game results from the MLB API for specific date ranges
to ensure we have complete game data for recaps.
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
import time

class HistoricalGamesFetcher:
    def __init__(self):
        """Initialize the Historical Games Fetcher"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.api_calls_made = 0
        
    def load_existing_data(self) -> dict:
        """Load existing game scores data"""
        if not os.path.exists(self.game_scores_path):
            return {}
        
        try:
            with open(self.game_scores_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return {}
    
    def save_data(self, data: dict):
        """Save data to file with backup"""
        # Create backup
        if os.path.exists(self.game_scores_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.game_scores_path}.bak_{timestamp}"
            os.rename(self.game_scores_path, backup_path)
            print(f"Created backup at {backup_path}")
        
        # Save new data
        with open(self.game_scores_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def fetch_games_for_date(self, date_str: str) -> list:
        """Fetch games for a specific date from MLB API"""
        print(f"Fetching games for {date_str}...")
        
        try:
            # MLB API endpoint for games on a specific date
            url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=game(content(summary,media(epg))),linescore,team,probablePitcher"
            
            response = requests.get(url, timeout=30)
            self.api_calls_made += 1
            
            if response.status_code != 200:
                print(f"Error fetching data for {date_str}: HTTP {response.status_code}")
                return []
            
            data = response.json()
            games = []
            
            # Process each date in the response
            for date_entry in data.get('dates', []):
                for game in date_entry.get('games', []):
                    game_info = self.process_game_data(game, date_str)
                    if game_info:
                        games.append(game_info)
            
            print(f"Found {len(games)} games for {date_str}")
            return games
            
        except Exception as e:
            print(f"Error fetching games for {date_str}: {e}")
            return []
    
    def process_game_data(self, game: dict, date_str: str) -> dict:
        """Process individual game data from MLB API response"""
        try:
            game_pk = game.get('gamePk')
            status = game.get('status', {})
            status_code = status.get('statusCode', '')
            
            # Teams
            teams = game.get('teams', {})
            away_team = teams.get('away', {})
            home_team = teams.get('home', {})
            
            # Basic game info
            game_info = {
                'game_pk': game_pk,
                'away_team': away_team.get('team', {}).get('name', 'Unknown'),
                'away_team_id': away_team.get('team', {}).get('id'),
                'home_team': home_team.get('team', {}).get('name', 'Unknown'),
                'home_team_id': home_team.get('team', {}).get('id'),
                'status': status.get('detailedState', 'Unknown'),
                'status_code': status_code,
                'game_time': game.get('gameDate', ''),
                'game_date': game.get('gameDate', ''),
                'data_source': 'MLB API'
            }
            
            # Probable pitchers
            probable_pitchers = game.get('teams', {})
            away_pitcher = probable_pitchers.get('away', {}).get('probablePitcher', {})
            home_pitcher = probable_pitchers.get('home', {}).get('probablePitcher', {})
            
            if away_pitcher:
                game_info['away_pitcher'] = away_pitcher.get('fullName', 'TBD')
            if home_pitcher:
                game_info['home_pitcher'] = home_pitcher.get('fullName', 'TBD')
            
            # Score information (if game is final)
            is_final = status_code in ['F', 'FT', 'FR']  # Final, Final (tied), Final (rain)
            game_info['is_final'] = is_final
            
            if is_final:
                away_score = away_team.get('score', 0)
                home_score = home_team.get('score', 0)
                
                game_info['away_score'] = away_score
                game_info['home_score'] = home_score
                game_info['total_score'] = away_score + home_score
                
                # Determine winner
                if away_score > home_score:
                    game_info['winning_team'] = game_info['away_team']
                    game_info['score_differential'] = away_score - home_score
                elif home_score > away_score:
                    game_info['winning_team'] = game_info['home_team']
                    game_info['score_differential'] = home_score - away_score
                else:
                    game_info['winning_team'] = 'Tie'
                    game_info['score_differential'] = 0
            
            return game_info
            
        except Exception as e:
            print(f"Error processing game data: {e}")
            return None
    
    def fetch_historical_games(self, start_date: str, end_date: str):
        """Fetch historical games for a date range"""
        print(f"\n=== Historical Games Fetcher ===")
        print(f"Fetching games from {start_date} to {end_date}")
        
        # Load existing data
        existing_data = self.load_existing_data()
        
        # Generate date range
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        date_range = []
        current = start
        while current <= end:
            date_range.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        total_games_added = 0
        
        # Fetch games for each date
        for date_str in date_range:
            games = self.fetch_games_for_date(date_str)
            
            if games:
                # Update existing data
                existing_data[date_str] = {
                    'games': games,
                    'last_updated': datetime.now().isoformat(),
                    'game_count': len(games)
                }
                total_games_added += len(games)
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        # Save updated data
        if total_games_added > 0:
            self.save_data(existing_data)
            print(f"\n=== Fetch Complete ===")
            print(f"Dates processed: {len(date_range)}")
            print(f"Total games added/updated: {total_games_added}")
            print(f"API calls made: {self.api_calls_made}")
        else:
            print(f"\nNo new games found to add.")

def main():
    """Main function"""
    # Default date range: August 7-13, 2025
    start_date = "2025-08-07"
    end_date = "2025-08-13"
    
    # Allow command line arguments
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    fetcher = HistoricalGamesFetcher()
    fetcher.fetch_historical_games(start_date, end_date)

if __name__ == "__main__":
    main()
