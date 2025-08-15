#!/usr/bin/env python3
"""
MLB Betting Lines Fetcher using OddsAPI

This script fetches betting lines from OddsAPI for MLB games,
formats them to match the system format, and adds them to 
the historical_betting_lines_cache.json file.
"""
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
            return []t json
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
            "Chicago Cubs": ["Chicago Cubs", "Cubs", "CHC", "CHI", "Chicago Cubs"],
            "Chicago White Sox": ["Chicago White Sox", "White Sox", "CWS", "CHW", "Chicago White Sox"],
            "Cincinnati Reds": ["Cincinnati", "Reds", "CIN", "Cincinnati Reds"],
            "Cleveland Guardians": ["Cleveland", "Guardians", "CLE", "Cleveland Indians", "Cleveland Guardians"],
            "Colorado Rockies": ["Colorado", "Rockies", "COL", "Colorado Rockies"],
            "Detroit Tigers": ["Detroit", "Tigers", "DET", "Detroit Tigers"],
            "Houston Astros": ["Houston", "Astros", "HOU", "Houston Astros"],
            "Kansas City Royals": ["Kansas City", "Royals", "KC", "KCR", "Kansas City Royals"],
            "Los Angeles Angels": ["LA Angels", "Angels", "LAA", "Los Angeles Angels", "Los Angeles Angels"],
            "Los Angeles Dodgers": ["LA Dodgers", "Dodgers", "LAD", "Los Angeles Dodgers", "Los Angeles Dodgers"],
            "Miami Marlins": ["Miami", "Marlins", "MIA", "Miami Marlins"],
            "Milwaukee Brewers": ["Milwaukee", "Brewers", "MIL", "Milwaukee Brewers"],
            "Minnesota Twins": ["Minnesota", "Twins", "MIN", "Minnesota Twins"],
            "New York Mets": ["NY Mets", "Mets", "NYM", "New York Mets", "New York Mets"],
            "New York Yankees": ["NY Yankees", "Yankees", "NYY", "New York Yankees", "New York Yankees"],
            "Oakland Athletics": ["Oakland", "Athletics", "OAK", "Oakland A's", "A's", "Athletics", "Oakland Athletics"],
            "Philadelphia Phillies": ["Philadelphia", "Phillies", "PHI", "Philadelphia Phillies"],
            "Pittsburgh Pirates": ["Pittsburgh", "Pirates", "PIT", "Pittsburgh Pirates"],
            "San Diego Padres": ["San Diego", "Padres", "SD", "SDP", "San Diego Padres"],
            "San Francisco Giants": ["SF Giants", "Giants", "SF", "SFG", "San Francisco Giants"],
            "Seattle Mariners": ["Seattle", "Mariners", "SEA", "Seattle Mariners"],
            "St. Louis Cardinals": ["St. Louis", "Cardinals", "STL", "St. Louis Cardinals"],
            "Tampa Bay Rays": ["Tampa Bay", "Rays", "TB", "TBR", "Tampa Bay Rays"],
            "Texas Rangers": ["Texas", "Rangers", "TEX", "Texas Rangers"],
            "Toronto Blue Jays": ["Toronto", "Blue Jays", "TOR", "Toronto Blue Jays"],
            "Washington Nationals": ["Washington", "Nationals", "WSH", "WAS", "WSN", "Washington Nationals"]
        }
    
    def standardize_team_name(self, team_name: str) -> str:
        """Standardize team name to official MLB team name"""
        if not team_name:
            return ""
            
        # Check if it's already an official name
        for official_name in self.team_name_variations.keys():
            if team_name == official_name:
                return official_name
        
        # Try to match with variations
        for official_name, variations in self.team_name_variations.items():
            if any(v.lower() == team_name.lower() for v in variations):
                return official_name
        
        # Last resort: try to find a partial match
        for official_name, variations in self.team_name_variations.items():
            if any(team_name.lower() in v.lower() or v.lower() in team_name.lower() 
                   for v in variations + [official_name]):
                return official_name
        
        # No match found
        logger.warning(f"Could not standardize team name: {team_name}")
        return team_name
    
    def load_json_file(self, filepath: str) -> dict:
        """Load a JSON file with error handling"""
        if not os.path.exists(filepath):
            logger.warning(f"File not found - {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            self.stats['errors'] += 1
            return {}
    
    def save_json_file(self, filepath: str, data: dict) -> bool:
        """Save data to a JSON file with error handling"""
        try:
            # Create a backup first
            if os.path.exists(filepath):
                backup_path = f"{filepath}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(filepath, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                logger.info(f"Created backup at {backup_path}")
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {filepath}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def fetch_odds_for_date(self, date_str: str) -> List[Dict]:
        """Fetch odds for a specific date from OddsAPI"""
        if not self.api_key:
            logger.error("No API key available")
            return []
        
        # Format date for OddsAPI (YYYY-MM-DD)
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Prepare parameters
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',  # Get moneyline, run line, and totals
            'oddsFormat': 'american',
            'dateFormat': 'iso',
            'eventIds': None  # Fetch all events for MLB
        }
        
        try:
            logger.info(f"Fetching odds for {date_str}")
            response = requests.get(self.odds_api_url, params=params)
            self.stats['api_calls'] += 1
            
            # Check if we've hit the rate limit
            if response.status_code == 429:
                logger.warning("Rate limit reached, waiting before retry")
                time.sleep(5)  # Wait 5 seconds before retry
                return []
                
            # Check for other errors
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return []
            
            # Get odds data
            odds_data = response.json()
            
            # Filter for games on the target date
            target_games = []
            for game in odds_data:
                game_date = game.get('commence_time', '')
                if game_date:
                    game_date = game_date.split('T')[0]  # Get just the date part
                    game_datetime = datetime.fromisoformat(game_date)
                    if game_datetime.date() == target_date.date():
                        target_games.append(game)
            
            logger.info(f"Found {len(target_games)} games for {date_str}")
            return target_games
            
        except Exception as e:
            logger.error(f"Error fetching odds: {str(e)}")
            self.stats['errors'] += 1
            return []
    
    def map_to_game_ids(self, odds_data: List[Dict], date_str: str) -> List[Dict]:
        """Map OddsAPI data to game IDs from game_scores"""
        # Load game scores
        game_scores = self.load_json_file(self.game_scores_path)
        
        # Check if date exists
        if date_str not in game_scores:
            logger.warning(f"No games found for {date_str} in game_scores")
            return []
            
        # Get games for this date
        date_games = game_scores[date_str].get('games', [])
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
                    'home_team': std_home_team
                }
        
        # Map odds data to game IDs
        mapped_odds = []
        for game in odds_data:
            try:
                home_team = None
                away_team = None
                
                # Extract teams
                teams = game.get('home_team', ''), game.get('away_team', '')
                if not teams[0] or not teams[1]:
                    # Try alternative format
                    team_names = [team.get('name', '') for team in game.get('competitors', [])]
                    if len(team_names) >= 2:
                        # Determine home and away teams
                        home_idx = next((i for i, team in enumerate(game.get('competitors', [])) 
                                       if team.get('home', False)), 0)
                        away_idx = 1 - home_idx  # If home is 0, away is 1 and vice versa
                        
                        home_team = team_names[home_idx]
                        away_team = team_names[away_idx]
                else:
                    home_team, away_team = teams
                
                if not home_team or not away_team:
                    continue
                    
                # Standardize team names
                std_home_team = self.standardize_team_name(home_team)
                std_away_team = self.standardize_team_name(away_team)
                
                # Create key for lookup
                key = f"{std_away_team}@{std_home_team}"
                
                if key in team_to_game_id:
                    game_info = team_to_game_id[key]
                    
                    # Extract odds
                    moneyline_home = None
                    moneyline_away = None
                    spread_home = None
                    spread_away = None
                    total_over = None
                    total_under = None
                    total_value = None
                    
                    # Process bookmakers
                    for bookmaker in game.get('bookmakers', []):
                        markets = bookmaker.get('markets', [])
                        
                        # Extract moneyline (h2h)
                        h2h_market = next((m for m in markets if m.get('key') == 'h2h'), None)
                        if h2h_market:
                            outcomes = h2h_market.get('outcomes', [])
                            for outcome in outcomes:
                                name = outcome.get('name', '')
                                price = outcome.get('price', None)
                                
                                # Try to match team with outcome
                                if self.team_matches(name, std_home_team):
                                    moneyline_home = price
                                elif self.team_matches(name, std_away_team):
                                    moneyline_away = price
                        
                        # Extract spread
                        spreads_market = next((m for m in markets if m.get('key') == 'spreads'), None)
                        if spreads_market:
                            outcomes = spreads_market.get('outcomes', [])
                            for outcome in outcomes:
                                name = outcome.get('name', '')
                                point = outcome.get('point', None)
                                price = outcome.get('price', None)
                                
                                # Try to match team with outcome
                                if self.team_matches(name, std_home_team):
                                    spread_home = {'line': point, 'odds': price}
                                elif self.team_matches(name, std_away_team):
                                    spread_away = {'line': point, 'odds': price}
                        
                        # Extract totals
                        totals_market = next((m for m in markets if m.get('key') == 'totals'), None)
                        if totals_market:
                            outcomes = totals_market.get('outcomes', [])
                            total_value = next((o.get('point') for o in outcomes if 'point' in o), None)
                            
                            for outcome in outcomes:
                                name = outcome.get('name', '').lower()
                                price = outcome.get('price', None)
                                
                                if name == 'over':
                                    total_over = price
                                elif name == 'under':
                                    total_under = price
                    
                    # Create formatted odds object
                    odds = {
                        'game_id': game_info['game_id'],
                        'away_team': std_away_team,
                        'home_team': std_home_team,
                        'moneyline': {
                            'away': moneyline_away,
                            'home': moneyline_home
                        },
                        'spread': {
                            'away': spread_away,
                            'home': spread_home
                        },
                        'total': {
                            'value': total_value,
                            'over': total_over,
                            'under': total_under
                        },
                        'source': 'OddsAPI',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    mapped_odds.append(odds)
            except Exception as e:
                logger.error(f"Error mapping game odds: {str(e)}")
                continue
        
        return mapped_odds
    
    def team_matches(self, name1: str, name2: str) -> bool:
        """Check if two team names match"""
        if not name1 or not name2:
            return False
            
        name1 = name1.lower()
        name2 = name2.lower()
        
        # Direct match
        if name1 == name2:
            return True
            
        # Check for substring match
        if name1 in name2 or name2 in name1:
            return True
            
        # Check for variations
        for team, variations in self.team_name_variations.items():
            team_lower = team.lower()
            variations_lower = [v.lower() for v in variations]
            
            if (name1 == team_lower or name1 in variations_lower) and \
               (name2 == team_lower or name2 in variations_lower):
                return True
        
        return False
    
    def update_betting_lines(self, mapped_odds: List[Dict], date_str: str) -> Dict:
        """Update historical_betting_lines_cache.json with new odds"""
        # Load current betting lines
        betting_lines = self.load_json_file(self.betting_lines_path)
        
        # Initialize for this date if needed
        if date_str not in betting_lines:
            betting_lines[date_str] = {}
            
        # Track stats for this update
        added = 0
        updated = 0
        
        # Process mapped odds
        for odds in mapped_odds:
            game_id = odds.get('game_id', '')
            if not game_id:
                continue
                
            # Generate a unique ID for this betting line
            line_id = f"odds_api_{date_str}_{game_id}"
            
            # Check if we need to add or update
            if line_id in betting_lines[date_str]:
                # Update existing entry
                betting_lines[date_str][line_id].update(odds)
                updated += 1
            else:
                # Add new entry
                betting_lines[date_str][line_id] = odds
                added += 1
        
        # Save updated betting lines
        if added > 0 or updated > 0:
            self.save_json_file(self.betting_lines_path, betting_lines)
            
            # Update stats
            self.stats['betting_lines_added'] += added
            self.stats['betting_lines_updated'] += updated
            
            logger.info(f"Added {added} and updated {updated} betting lines for {date_str}")
        
        return {'added': added, 'updated': updated}
    
    def process_date(self, date_str: str) -> Dict:
        """Process a single date to fetch and update betting lines"""
        try:
            # Fetch odds for this date
            odds_data = self.fetch_odds_for_date(date_str)
            
            if not odds_data:
                logger.warning(f"No odds data found for {date_str}")
                return {'added': 0, 'updated': 0}
                
            # Map odds data to game IDs
            mapped_odds = self.map_to_game_ids(odds_data, date_str)
            
            if not mapped_odds:
                logger.warning(f"Could not map any odds to games for {date_str}")
                return {'added': 0, 'updated': 0}
                
            # Update betting lines
            result = self.update_betting_lines(mapped_odds, date_str)
            
            # Update processed dates count
            self.stats['dates_processed'] += 1
            self.stats['games_found'] += len(mapped_odds)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing date {date_str}: {str(e)}")
            self.stats['errors'] += 1
            return {'added': 0, 'updated': 0}
    
    def process_date_range(self, start_date: str, end_date: str = None) -> Dict:
        """Process a range of dates to fetch and update betting lines"""
        # Use today's date if end_date not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Generate date range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_range = []
        current = start
        while current <= end:
            date_range.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        logger.info(f"Processing {len(date_range)} dates from {start_date} to {end_date}")
        
        # Process each date
        for date_str in date_range:
            self.process_date(date_str)
            
            # Respect API rate limits (3 requests per second)
            time.sleep(0.33)
        
        # Generate report
        self.generate_report()
        
        return self.stats
    
    def generate_report(self) -> str:
        """Generate a report of the fetch operation"""
        report = f"=== OddsAPI Fetch Report ===\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += f"Summary:\n"
        report += f"- Dates processed: {self.stats['dates_processed']}\n"
        report += f"- Games found: {self.stats['games_found']}\n"
        report += f"- Betting lines added: {self.stats['betting_lines_added']}\n"
        report += f"- Betting lines updated: {self.stats['betting_lines_updated']}\n"
        report += f"- API calls made: {self.stats['api_calls']}\n"
        report += f"- Errors: {self.stats['errors']}\n"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.root_dir, f"oddsapi_report_{timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Report written to {report_path}")
        print(f"\nReport written to {os.path.basename(report_path)}")
        
        return report

def main():
    """Main function to fetch betting lines from OddsAPI"""
    start_date = "2025-08-09"  # Default to August 9 since Aug 7-8 already have lines
    end_date = None  # Today by default
    
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    
    print(f"=== MLB Betting Lines Fetcher (OddsAPI) ===")
    if start_date and end_date:
        print(f"Date range: {start_date} to {end_date}")
    elif start_date:
        print(f"From date: {start_date} to today")
    
    fetcher = OddsAPIFetcher()
    
    if not fetcher.api_key:
        print("ERROR: No OddsAPI key found. Please add your key to api_keys.json")
        print("The key should be stored as either 'odds_api' or 'ODDS_API_KEY'")
        sys.exit(1)
    
    stats = fetcher.process_date_range(start_date, end_date)
    
    print("\n=== Fetch Complete ===")
    print(f"Dates processed: {stats['dates_processed']}")
    print(f"Games found: {stats['games_found']}")
    print(f"Betting lines added: {stats['betting_lines_added']}")
    print(f"Betting lines updated: {stats['betting_lines_updated']}")
    print(f"API calls made: {stats['api_calls']}")
    print(f"Errors: {stats['errors']}")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
