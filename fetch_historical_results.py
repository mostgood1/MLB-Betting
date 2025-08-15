#!/usr/bin/env python3
"""
MLB Historical Game Results Fetcher
==================================

Fetches all MLB game results for 2025 from the official MLB API
and saves them to a comprehensive data file for prediction accuracy analysis.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLBHistoricalFetcher:
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self.results_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source': 'MLB Stats API',
                'year': 2025,
                'description': 'Complete MLB game results for 2025'
            },
            'games_by_date': {}
        }
    
    def get_games_for_date(self, date_str):
        """Get all games for a specific date"""
        try:
            url = f"{self.base_url}/schedule/games/?sportId=1&date={date_str}&hydrate=score,team"
            logger.info(f"Fetching games for {date_str}...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            games = data.get('dates', [])
            
            if not games:
                logger.info(f"No games found for {date_str}")
                return []
            
            game_results = []
            for date_info in games:
                for game in date_info.get('games', []):
                    # Only process completed games
                    if game.get('status', {}).get('statusCode') in ['F', 'O']:  # Final or Other (completed)
                        away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', '')
                        home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', '')
                        
                        away_score = game.get('teams', {}).get('away', {}).get('score', 0)
                        home_score = game.get('teams', {}).get('home', {}).get('score', 0)
                        
                        game_result = {
                            'game_pk': game.get('gamePk'),
                            'date': date_str,
                            'away_team': away_team,
                            'home_team': home_team,
                            'away_score': away_score,
                            'home_score': home_score,
                            'total_runs': away_score + home_score,
                            'winner': 'away' if away_score > home_score else 'home',
                            'status': game.get('status', {}).get('detailedState', ''),
                            'game_type': game.get('gameType', ''),
                            'double_header': game.get('doubleHeader', 'N')
                        }
                        game_results.append(game_result)
                        logger.info(f"  {away_team} @ {home_team}: {away_score}-{home_score}")
            
            return game_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching games for {date_str}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error for {date_str}: {e}")
            return []
    
    def fetch_season_results(self, start_date=None, end_date=None):
        """Fetch all game results for the 2025 season"""
        
        # Default to full season range
        if not start_date:
            start_date = datetime(2025, 3, 1)  # Spring training starts
        if not end_date:
            end_date = datetime.now()  # Up to today
        
        logger.info(f"🏟️ Fetching MLB game results from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        current_date = start_date
        total_games = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Get games for this date
            games = self.get_games_for_date(date_str)
            
            if games:
                self.results_data['games_by_date'][date_str] = {
                    'date': date_str,
                    'games_count': len(games),
                    'games': games
                }
                total_games += len(games)
                logger.info(f"✅ {date_str}: {len(games)} completed games")
            
            # Move to next day
            current_date += timedelta(days=1)
            
            # Rate limiting - be nice to MLB API
            time.sleep(0.5)
        
        self.results_data['metadata']['total_games'] = total_games
        self.results_data['metadata']['date_range'] = {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
        
        logger.info(f"🎯 Total games fetched: {total_games}")
        return self.results_data
    
    def save_results(self, filename='data/mlb_historical_results_2025.json'):
        """Save the fetched results to a JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results_data, f, indent=2)
            
            logger.info(f"💾 Results saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

def main():
    """Main function to fetch and save MLB historical results"""
    logger.info("🚀 MLB Historical Game Results Fetcher Starting")
    
    fetcher = MLBHistoricalFetcher()
    
    # Fetch results from August 7th (when our predictions started) to today
    start_date = datetime(2025, 8, 7)
    end_date = datetime.now()
    
    logger.info(f"📅 Fetching games from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Fetch the data
    results = fetcher.fetch_season_results(start_date, end_date)
    
    # Save to file
    if fetcher.save_results():
        logger.info("✅ Historical game results successfully fetched and saved!")
        
        # Summary
        total_games = results['metadata']['total_games']
        date_count = len(results['games_by_date'])
        logger.info(f"📊 Summary: {total_games} games across {date_count} dates")
        
    else:
        logger.error("❌ Failed to save results")

if __name__ == "__main__":
    main()
