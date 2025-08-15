"""
Enhanced MLB Data Fetcher for Daily Games
Fetches complete game information including starting pitchers and accurate times
"""
import requests
from datetime import datetime
from typing import List, Dict, Optional

def fetch_todays_complete_games(date: str = None) -> List[Dict]:
    """
    Fetch today's MLB games with complete information including:
    - Starting pitchers
    - Accurate game times
    - Current status
    - Team information
    """
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Use MLB API with proper hydration for pitcher and time data
        url = f'https://statsapi.mlb.com/api/v1/schedule'
        params = {
            'sportId': 1,
            'date': date,
            'hydrate': 'probablePitcher,game(content(summary,media(epg)))'
        }
        
        print(f"Fetching complete game data for {date}")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        games = []
        
        if 'dates' in data and data['dates']:
            for date_entry in data['dates']:
                if 'games' in date_entry:
                    for game in date_entry['games']:
                        game_info = extract_complete_game_info(game)
                        if game_info:
                            games.append(game_info)
        
        print(f"Successfully fetched {len(games)} complete games")
        return games
        
    except Exception as e:
        print(f"Error fetching complete games data: {e}")
        return []

def extract_complete_game_info(game: Dict) -> Optional[Dict]:
    """Extract complete game information from MLB API response"""
    try:
        # Basic game info
        away_team = game['teams']['away']['team']['name']
        home_team = game['teams']['home']['team']['name']
        game_pk = game.get('gamePk', '')
        game_date = game.get('gameDate', '')
        status = game['status']['detailedState']
        
        # Extract pitcher information
        away_pitcher = 'TBD'
        away_pitcher_id = None
        home_pitcher = 'TBD'  
        home_pitcher_id = None
        
        # Away pitcher
        if ('probablePitcher' in game['teams']['away'] and 
            game['teams']['away']['probablePitcher']):
            away_pitcher_data = game['teams']['away']['probablePitcher']
            away_pitcher = away_pitcher_data.get('fullName', 'TBD')
            away_pitcher_id = away_pitcher_data.get('id')
        
        # Home pitcher
        if ('probablePitcher' in game['teams']['home'] and 
            game['teams']['home']['probablePitcher']):
            home_pitcher_data = game['teams']['home']['probablePitcher']
            home_pitcher = home_pitcher_data.get('fullName', 'TBD')
            home_pitcher_id = home_pitcher_data.get('id')
        
        # Format game time properly
        formatted_time = game_date
        if game_date:
            try:
                dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                formatted_time = dt.isoformat()
            except:
                formatted_time = game_date
        
        game_info = {
            'away_team': away_team,
            'home_team': home_team,
            'away_pitcher': away_pitcher,
            'away_pitcher_id': away_pitcher_id,
            'home_pitcher': home_pitcher,
            'home_pitcher_id': home_pitcher_id,
            'game_time': formatted_time,
            'game_date': game_date,
            'status': status,
            'game_pk': game_pk,
            'date': game_date[:10] if game_date else datetime.now().strftime('%Y-%m-%d')
        }
        
        print(f"✅ Extracted: {away_team} @ {home_team}")
        print(f"   Pitchers: {away_pitcher} vs {home_pitcher}")
        print(f"   Time: {formatted_time}")
        
        return game_info
        
    except Exception as e:
        print(f"❌ Error extracting game info: {e}")
        return None

def test_enhanced_fetcher():
    """Test the enhanced fetcher"""
    print("🧪 TESTING ENHANCED MLB DATA FETCHER")
    print("=" * 50)
    
    games = fetch_todays_complete_games('2025-08-14')
    
    print(f"\n📊 RESULTS: {len(games)} games found")
    print("=" * 50)
    
    for i, game in enumerate(games, 1):
        print(f"{i}. {game['away_team']} @ {game['home_team']}")
        print(f"   Away Pitcher: {game['away_pitcher']}")
        print(f"   Home Pitcher: {game['home_pitcher']}")
        print(f"   Game Time: {game['game_time']}")
        print(f"   Status: {game['status']}")
        print()

if __name__ == "__main__":
    test_enhanced_fetcher()
