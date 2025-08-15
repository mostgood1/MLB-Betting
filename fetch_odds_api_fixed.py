#!/usr/bin/env python3
"""
Fixed MLB Betting Lines Fetcher using OddsAPI

This script fetches betting lines from OddsAPI for MLB games,
formats them to match the system format, and adds them to 
the historical_betting_lines_cache.json file.
"""

import json
import os
import sys
import logging
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('odds_api_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('OddsAPIFetcher')

class OddsAPIFetcher:
    def __init__(self):
        """Initialize the OddsAPI Fetcher"""
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define file paths
        self.game_scores_path = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.betting_lines_path = os.path.join(self.root_dir, 'historical_betting_lines_cache.json')
        self.api_keys_path = os.path.join(self.root_dir, 'mlb-clean-deploy', 'api_keys.json')
        
        # Check for api_keys.json in root dir if not found in mlb-clean-deploy
        if not os.path.exists(self.api_keys_path):
            self.api_keys_path = os.path.join(self.root_dir, 'api_keys.json')
        
        # Load API key
        self.api_key = self._load_api_key()
        
        # API endpoints
        self.odds_api_url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
        
        # Track stats
        self.stats = {
            'dates_processed': 0,
            'games_found': 0,
            'betting_lines_added': 0,
            'betting_lines_updated': 0,
            'api_calls': 0,
            'errors': 0
        }
        
        # Team name variations
        self.team_name_variations = self._load_team_variations()
    
    def _load_api_key(self) -> str:
        """Load API key from api_keys.json file"""
        if not os.path.exists(self.api_keys_path):
            logger.error(f"API keys file not found at {self.api_keys_path}")
            return None
            
        try:
            with open(self.api_keys_path, 'r') as f:
                keys = json.load(f)
            
            # Debug logging
            logger.info(f"API keys loaded from {self.api_keys_path}")
            logger.info(f"Available keys: {list(keys.keys())}")
                
            if 'odds_api' in keys:
                logger.info("Found 'odds_api' key")
                return keys['odds_api']
            elif 'ODDS_API_KEY' in keys:
                logger.info("Found 'ODDS_API_KEY' key")
                return keys['ODDS_API_KEY']
            else:
                # Hard-code your key directly here as a fallback
                logger.warning("Using hardcoded API key as fallback")
                return "07da97d86f1b1e431b4e01341abbf9e2"
        except Exception as e:
            logger.error(f"Error loading API key: {str(e)}")
            # Hard-code your key directly here as a fallback
            logger.warning("Using hardcoded API key as fallback after error")
            return "07da97d86f1b1e431b4e01341abbf9e2"
    
    def _load_team_variations(self) -> Dict[str, List[str]]:
        """Load team name variations to handle different formats"""
        # This maps official MLB team names to various formats that might appear in data
        return {
            "Arizona Diamondbacks": ["Arizona", "Diamondbacks", "ARI", "Arizona D-backs", "AZ", "D-backs", "Arizona Diamondbacks"],
            "Atlanta Braves": ["Atlanta", "Braves", "ATL", "Atlanta Braves"],
            "Baltimore Orioles": ["Baltimore", "Orioles", "BAL", "Baltimore Orioles"],
            "Boston Red Sox": ["Boston", "Red Sox", "BOS", "Boston Red Sox"],
            "Chicago Cubs": ["Chicago Cubs", "Cubs", "CHC", "Chi Cubs"],
            "Chicago White Sox": ["Chicago White Sox", "White Sox", "CWS", "Chi White Sox"],
            "Cincinnati Reds": ["Cincinnati", "Reds", "CIN", "Cincinnati Reds"],
            "Cleveland Guardians": ["Cleveland", "Guardians", "CLE", "Cleveland Guardians"],
            "Colorado Rockies": ["Colorado", "Rockies", "COL", "Colorado Rockies"],
            "Detroit Tigers": ["Detroit", "Tigers", "DET", "Detroit Tigers"],
            "Houston Astros": ["Houston", "Astros", "HOU", "Houston Astros"],
            "Kansas City Royals": ["Kansas City", "Royals", "KC", "Kansas City Royals"],
            "Los Angeles Angels": ["Los Angeles Angels", "Angels", "LAA", "LA Angels"],
            "Los Angeles Dodgers": ["Los Angeles Dodgers", "Dodgers", "LAD", "LA Dodgers"],
            "Miami Marlins": ["Miami", "Marlins", "MIA", "Miami Marlins"],
            "Milwaukee Brewers": ["Milwaukee", "Brewers", "MIL", "Milwaukee Brewers"],
            "Minnesota Twins": ["Minnesota", "Twins", "MIN", "Minnesota Twins"],
            "New York Mets": ["New York Mets", "Mets", "NYM", "NY Mets"],
            "New York Yankees": ["New York Yankees", "Yankees", "NYY", "NY Yankees"],
            "Oakland Athletics": ["Oakland", "Athletics", "OAK", "Oakland Athletics", "A's"],
            "Philadelphia Phillies": ["Philadelphia", "Phillies", "PHI", "Philadelphia Phillies"],
            "Pittsburgh Pirates": ["Pittsburgh", "Pirates", "PIT", "Pittsburgh Pirates"],
            "San Diego Padres": ["San Diego", "Padres", "SD", "San Diego Padres"],
            "San Francisco Giants": ["San Francisco", "Giants", "SF", "San Francisco Giants"],
            "Seattle Mariners": ["Seattle", "Mariners", "SEA", "Seattle Mariners"],
            "St. Louis Cardinals": ["St. Louis", "Cardinals", "STL", "St. Louis Cardinals"],
            "Tampa Bay Rays": ["Tampa Bay", "Rays", "TB", "Tampa Bay Rays"],
            "Texas Rangers": ["Texas", "Rangers", "TEX", "Texas Rangers"],
            "Toronto Blue Jays": ["Toronto", "Blue Jays", "TOR", "Toronto Blue Jays"],
            "Washington Nationals": ["Washington", "Nationals", "WSH", "Washington Nationals"]
        }
    
    def load_json_file(self, file_path: str) -> Dict:
        """Load a JSON file and return its contents"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"File not found: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return {}
    
    def save_json_file(self, file_path: str, data: Dict) -> bool:
        """Save data to a JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {str(e)}")
            return False
    
    def fetch_odds_for_date(self, target_date: datetime) -> List[Dict]:
        """Fetch odds data from OddsAPI for a specific date"""
        if not self.api_key:
            logger.error("No API key available")
            return []
        
        try:
            self.stats['api_calls'] += 1
            
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            logger.info(f"Fetching odds from OddsAPI for {target_date.strftime('%Y-%m-%d')}")
            response = requests.get(self.odds_api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Fetched {len(data)} games from OddsAPI")
                
                # Filter for target date
                target_games = []
                date_str = target_date.strftime('%Y-%m-%d')
                
                for game in data:
                    if not isinstance(game, dict):
                        continue
                        
                    game_date = game.get('commence_time', '')
                    if game_date:
                        game_date = game_date.split('T')[0]  # Get just the date part
                        game_datetime = datetime.fromisoformat(game_date)
                        if game_datetime.date() == target_date.date():
                            target_games.append(game)
                
                logger.info(f"Found {len(target_games)} games for {date_str}")
                return target_games
                
            else:
                logger.error(f"API request failed with status {response.status_code}")
                self.stats['errors'] += 1
                return []
                
        except Exception as e:
            logger.error(f"Error fetching odds: {str(e)}")
            self.stats['errors'] += 1
            return []
    
    def map_to_game_ids(self, odds_data: List[Dict], date_str: str) -> List[Dict]:
        """Map OddsAPI data to game IDs from game_scores"""
        # Load game scores
        game_scores = self.load_json_file(self.game_scores_path)
        
        # Check if date exists in game_scores
        if date_str not in game_scores:
            logger.warning(f"No games found for {date_str} in game_scores")
            return []
            
        # Get games for this date - handle both dict and list formats
        date_data = game_scores[date_str]
        if isinstance(date_data, dict):
            date_games = date_data.get('games', [])
        elif isinstance(date_data, list):
            date_games = date_data
        else:
            logger.error(f"Unexpected data format for {date_str}: {type(date_data)}")
            return []
            
        if not date_games:
            logger.warning(f"No games found for {date_str}")
            return []
            
        # Create a mapping of teams to game IDs
        team_to_game_id = {}
        for game in date_games:
            if not isinstance(game, dict):
                continue
                
            game_id = str(game.get('game_pk', ''))
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            
            if game_id and away_team and home_team:
                # Standardize team names
                std_away_team = self.standardize_team_name(away_team)
                std_home_team = self.standardize_team_name(home_team)
                
                # Create a key for lookup
                key = f"{std_away_team}@{std_home_team}"
                team_to_game_id[key] = {
                    'game_id': game_id,
                    'away_team': std_away_team,
                    'home_team': std_home_team,
                    'original_away': away_team,
                    'original_home': home_team
                }
        
        # Map odds data to game IDs
        mapped_games = []
        for game in odds_data:
            try:
                # Try different ways to get teams from the game data
                teams = game.get('home_team', ''), game.get('away_team', '')
                
                # If that doesn't work, try competitors field
                if not teams[0] or not teams[1]:
                    team_names = [team.get('name', '') for team in game.get('competitors', [])]
                    if len(team_names) >= 2:
                        # Find which is home and away
                        home_idx = next((i for i, team in enumerate(game.get('competitors', [])) 
                                       if team.get('home', False)), 0)
                        away_idx = 1 - home_idx
                        
                        home_team = team_names[home_idx]
                        away_team = team_names[away_idx]
                    else:
                        logger.warning(f"Could not determine teams for game: {game}")
                        continue
                else:
                    home_team, away_team = teams
                
                # Standardize team names for lookup
                std_home_team = self.standardize_team_name(home_team)
                std_away_team = self.standardize_team_name(away_team)
                
                # Create lookup key
                lookup_key = f"{std_away_team}@{std_home_team}"
                
                # Find the game ID
                if lookup_key in team_to_game_id:
                    game_info = team_to_game_id[lookup_key]
                    
                    # Process betting lines
                    betting_lines = {}
                    
                    for bookmaker in game.get('bookmakers', []):
                        markets = bookmaker.get('markets', [])
                        
                        # Extract moneyline (h2h)
                        h2h_market = next((m for m in markets if m.get('key') == 'h2h'), None)
                        if h2h_market:
                            outcomes = h2h_market.get('outcomes', [])
                            for outcome in outcomes:
                                name = outcome.get('name', '')
                                price = outcome.get('price', None)
                                
                                if price is not None:
                                    std_name = self.standardize_team_name(name)
                                    if std_name == std_home_team:
                                        betting_lines['home_ml'] = price
                                    elif std_name == std_away_team:
                                        betting_lines['away_ml'] = price
                        
                        # Extract spreads
                        spreads_market = next((m for m in markets if m.get('key') == 'spreads'), None)
                        if spreads_market:
                            outcomes = spreads_market.get('outcomes', [])
                            for outcome in outcomes:
                                name = outcome.get('name', '')
                                price = outcome.get('price', None)
                                point = outcome.get('point', None)
                                
                                if price is not None and point is not None:
                                    std_name = self.standardize_team_name(name)
                                    if std_name == std_home_team:
                                        betting_lines['home_spread'] = point
                                        betting_lines['home_spread_odds'] = price
                                    elif std_name == std_away_team:
                                        betting_lines['away_spread'] = point
                                        betting_lines['away_spread_odds'] = price
                        
                        # Extract totals
                        totals_market = next((m for m in markets if m.get('key') == 'totals'), None)
                        if totals_market:
                            outcomes = totals_market.get('outcomes', [])
                            for outcome in outcomes:
                                name = outcome.get('name', '')
                                price = outcome.get('price', None)
                                point = outcome.get('point', None)
                                
                                if price is not None and point is not None:
                                    if name.lower() == 'over':
                                        betting_lines['over'] = point
                                        betting_lines['over_odds'] = price
                                    elif name.lower() == 'under':
                                        betting_lines['under'] = point
                                        betting_lines['under_odds'] = price
                        
                        # We only need the first bookmaker with data
                        if betting_lines:
                            break
                    
                    if betting_lines:
                        mapped_game = {
                            'game_id': game_info['game_id'],
                            'away_team': game_info['away_team'],
                            'home_team': game_info['home_team'],
                            'betting_lines': betting_lines,
                            'source': 'odds_api',
                            'timestamp': datetime.now().isoformat()
                        }
                        mapped_games.append(mapped_game)
                        logger.info(f"Mapped game {game_info['game_id']}: {game_info['away_team']} @ {game_info['home_team']}")
                else:
                    logger.warning(f"Could not find game ID for {std_away_team} @ {std_home_team}")
                    
            except Exception as e:
                logger.error(f"Error processing game: {str(e)}")
                continue
        
        return mapped_games
    
    def standardize_team_name(self, team_name: str) -> str:
        """Standardize team names to match our format"""
        if not team_name:
            return ""
        
        # Clean the name
        clean_name = team_name.strip()
        
        # Look for exact matches first
        for standard_name, variations in self.team_name_variations.items():
            if clean_name in variations:
                return standard_name
        
        # If no exact match, return the cleaned name
        return clean_name
    
    def add_to_historical_lines(self, games_data: List[Dict], date_str: str):
        """Add betting lines to historical cache"""
        # Load existing historical data
        historical_data = self.load_json_file(self.betting_lines_path)
        
        # Ensure date exists in historical data
        if date_str not in historical_data:
            historical_data[date_str] = {}
        
        # Add or update each game's betting lines
        for game in games_data:
            game_id = game['game_id']
            
            if game_id in historical_data[date_str]:
                # Update existing
                historical_data[date_str][game_id].update(game['betting_lines'])
                self.stats['betting_lines_updated'] += 1
                logger.info(f"Updated betting lines for game {game_id}")
            else:
                # Add new
                historical_data[date_str][game_id] = {
                    'away_team': game['away_team'],
                    'home_team': game['home_team'],
                    **game['betting_lines']
                }
                self.stats['betting_lines_added'] += 1
                logger.info(f"Added betting lines for game {game_id}")
        
        # Save updated historical data
        if self.save_json_file(self.betting_lines_path, historical_data):
            logger.info(f"Successfully updated historical betting lines cache")
        else:
            logger.error(f"Failed to save historical betting lines cache")
    
    def process_date_range(self, start_date: str, end_date: str = None):
        """Process a range of dates"""
        if end_date is None:
            end_date = start_date
        
        logger.info(f"Processing {1 if start_date == end_date else 'multiple'} dates from {start_date} to {end_date}")
        
        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            logger.info(f"Fetching odds for {date_str}")
            
            try:
                # Fetch odds data
                odds_data = self.fetch_odds_for_date(current)
                self.stats['games_found'] += len(odds_data)
                
                if odds_data:
                    # Map to game IDs
                    mapped_games = self.map_to_game_ids(odds_data, date_str)
                    
                    if mapped_games:
                        # Add to historical lines
                        self.add_to_historical_lines(mapped_games, date_str)
                        self.stats['dates_processed'] += 1
                    else:
                        logger.warning(f"No games could be mapped for {date_str}")
                else:
                    logger.warning(f"No odds data found for {date_str}")
                    
            except Exception as e:
                logger.error(f"Error processing date {date_str}: {str(e)}")
                self.stats['errors'] += 1
                
            current += timedelta(days=1)
            
            # Small delay between requests to be respectful
            time.sleep(1)
    
    def generate_report(self) -> str:
        """Generate a summary report"""
        report = "=== OddsAPI Fetch Report ===\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "Summary:\n"
        report += f"- Dates processed: {self.stats['dates_processed']}\n"
        report += f"- Games found: {self.stats['games_found']}\n"
        report += f"- Betting lines added: {self.stats['betting_lines_added']}\n"
        report += f"- Betting lines updated: {self.stats['betting_lines_updated']}\n"
        report += f"- API calls made: {self.stats['api_calls']}\n"
        report += f"- Errors: {self.stats['errors']}\n"
        
        return report

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python fetch_odds_api.py YYYY-MM-DD [YYYY-MM-DD]")
        print("Examples:")
        print("  python fetch_odds_api.py 2025-08-15")
        print("  python fetch_odds_api.py 2025-08-15 2025-08-17")
        sys.exit(1)
    
    start_date = sys.argv[1]
    end_date = sys.argv[2] if len(sys.argv) > 2 else start_date
    
    # Create fetcher and process
    fetcher = OddsAPIFetcher()
    fetcher.process_date_range(start_date, end_date)
    
    # Generate and save report
    report = fetcher.generate_report()
    
    # Save report to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"oddsapi_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Report written to {os.path.abspath(report_file)}")
    print(report)

if __name__ == "__main__":
    main()
