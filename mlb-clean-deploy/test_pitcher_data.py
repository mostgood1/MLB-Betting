import requests
import time

# Test the final pitcher data integration
time.sleep(1)

try:
    response = requests.get('http://localhost:5000/api/today-games?date=2025-08-14', timeout=10)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        games = data.get('games', [])
        print(f'Found {len(games)} games')
        
        # Check first game for pitcher info
        if games:
            game = games[0]
            print(f'First game: {game.get("away_team")} @ {game.get("home_team")}')
            print(f'Away pitcher: {game.get("away_pitcher", "Missing")}')
            print(f'Home pitcher: {game.get("home_pitcher", "Missing")}')
            
            # Quick summary
            real_pitchers = 0
            for g in games:
                if (g.get('away_pitcher', 'TBD') not in ['TBD', 'Missing', None] and 
                    g.get('home_pitcher', 'TBD') not in ['TBD', 'Missing', None]):
                    real_pitchers += 1
            
            print(f'\nSUMMARY: {real_pitchers}/{len(games)} games have real pitcher data')
    else:
        print(f'Error: {response.text}')
        
except Exception as e:
    print(f'Exception: {e}')
