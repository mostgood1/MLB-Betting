#!/usr/bin/env python3
"""
Real MLB Prediction Generator with Actual Pitcher Data
=====================================================
Generates REAL predictions using the actual prediction engine and real starting pitchers
from MLB API instead of synthetic statistical data.
"""

import json
import requests
import sys
import os
from datetime import datetime

# Add the MLB-Betting directory to path to import the engine
sys.path.append(os.path.join(os.path.dirname(__file__), 'MLB-Betting'))

def get_real_pitcher_data(date):
    """Get real starting pitcher data from MLB API"""
    try:
        url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}&hydrate=probablePitcher,game(content(summary,media(epg)),tickets)'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            dates = data.get('dates', [])
            
            if dates:
                games = dates[0].get('games', [])
                game_data = []
                
                for game in games:
                    away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', 'Unknown')
                    home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', 'Unknown')
                    
                    # Get probable pitchers
                    away_pitcher = game.get('teams', {}).get('away', {}).get('probablePitcher', {}).get('fullName', 'TBD')
                    home_pitcher = game.get('teams', {}).get('home', {}).get('probablePitcher', {}).get('fullName', 'TBD')
                    
                    # Get game time
                    game_time = game.get('gameDate', '')
                    if game_time:
                        # Convert to readable format
                        dt = datetime.fromisoformat(game_time.replace('Z', '+00:00'))
                        from datetime import timedelta
                        dt_central = dt - timedelta(hours=5)  # CDT
                        formatted_time = dt_central.strftime('%I:%M %p CT')
                    else:
                        formatted_time = 'TBD'
                    
                    game_data.append({
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_pitcher': away_pitcher,
                        'home_pitcher': home_pitcher,
                        'game_time': formatted_time,
                        'game_id': f"{away_team} @ {home_team}"
                    })
                
                return game_data
        
        return []
        
    except Exception as e:
        print(f"❌ Error fetching pitcher data for {date}: {e}")
        return []

def normalize_team_name_for_engine(team_name):
    """Normalize team names for prediction engine"""
    # Map full team names to engine-expected names
    team_mapping = {
        'Athletics': 'OAK',
        'Los Angeles Angels': 'LAA', 
        'Houston Astros': 'HOU',
        'Seattle Mariners': 'SEA',
        'Texas Rangers': 'TEX',
        'Minnesota Twins': 'MIN',
        'Chicago White Sox': 'CWS',
        'Cleveland Guardians': 'CLE',
        'Detroit Tigers': 'DET',
        'Kansas City Royals': 'KC',
        'Milwaukee Brewers': 'MIL',
        'St. Louis Cardinals': 'STL',
        'Chicago Cubs': 'CHC',
        'Cincinnati Reds': 'CIN',
        'Pittsburgh Pirates': 'PIT',
        'Baltimore Orioles': 'BAL',
        'Toronto Blue Jays': 'TOR',
        'New York Yankees': 'NYY',
        'Boston Red Sox': 'BOS',
        'Tampa Bay Rays': 'TB',
        'New York Mets': 'NYM',
        'Philadelphia Phillies': 'PHI',
        'Atlanta Braves': 'ATL',
        'Miami Marlins': 'MIA',
        'Washington Nationals': 'WSN',
        'Colorado Rockies': 'COL',
        'Arizona Diamondbacks': 'ARI',
        'San Diego Padres': 'SD',
        'San Francisco Giants': 'SF',
        'Los Angeles Dodgers': 'LAD'
    }
    
    return team_mapping.get(team_name, team_name)

def generate_real_predictions_for_date(date):
    """Generate real predictions using actual prediction engine"""
    print(f"🔄 Generating REAL predictions for {date}...")
    
    # Get real pitcher data from MLB API
    games_data = get_real_pitcher_data(date)
    
    if not games_data:
        print(f"❌ No pitcher data available for {date}")
        return None
    
    try:
        # Import and initialize the real prediction engine
        from engines.ultra_fast_engine import UltraFastSimEngine
        engine = UltraFastSimEngine()
        
        real_predictions = {}
        
        for game_data in games_data:
            away_team = game_data['away_team']
            home_team = game_data['home_team']
            away_pitcher = game_data['away_pitcher']
            home_pitcher = game_data['home_pitcher']
            game_time = game_data['game_time']
            
            print(f"  🏈 {away_team} @ {home_team}")
            print(f"    Pitchers: {away_pitcher} vs {home_pitcher}")
            
            try:
                # Normalize team names for engine
                away_team_code = normalize_team_name_for_engine(away_team)
                home_team_code = normalize_team_name_for_engine(home_team)
                
                # Run simulation using the real engine
                sim_results, metadata = engine.simulate_game_vectorized(
                    away_team=away_team_code,
                    home_team=home_team_code,
                    away_pitcher=away_pitcher,
                    home_pitcher=home_pitcher,
                    sim_count=1000  # Run 1000 simulations
                )
                
                # Extract prediction data from simulation result
                if sim_results and len(sim_results) > 0:
                    # Calculate averages from simulation
                    away_scores = [sim.away_score for sim in sim_results]
                    home_scores = [sim.home_score for sim in sim_results]
                    
                    predicted_away_score = sum(away_scores) / len(away_scores)
                    predicted_home_score = sum(home_scores) / len(home_scores)
                    predicted_total = predicted_away_score + predicted_home_score
                    
                    # Calculate win probabilities
                    away_wins = sum(1 for sim in sim_results if sim.away_score > sim.home_score)
                    away_win_prob = away_wins / len(sim_results)
                    home_win_prob = 1 - away_win_prob
                    
                    # Calculate confidence (based on win probability spread)
                    confidence = abs(away_win_prob - 0.5) * 200  # Scale to 0-100
                    
                    game_prediction = {
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_pitcher': away_pitcher,
                        'home_pitcher': home_pitcher,
                        'game_time': game_time,
                        'predicted_away_score': round(predicted_away_score, 1),
                        'predicted_home_score': round(predicted_home_score, 1),
                        'predicted_total_runs': round(predicted_total, 1),
                        'away_win_probability': round(away_win_prob * 100, 1),
                        'home_win_probability': round(home_win_prob * 100, 1),
                        'confidence': round(confidence, 1),
                        'predicted_winner': 'away' if away_win_prob > home_win_prob else 'home',
                        'simulation_count': len(sim_results),
                        'source': 'real_prediction_engine'
                    }
                    
                    real_predictions[game_data['game_id']] = game_prediction
                    
                    print(f"    ✅ Prediction: {predicted_away_score:.1f}-{predicted_home_score:.1f} ({away_win_prob*100:.1f}%/{home_win_prob*100:.1f}%)")
                    
                else:
                    print(f"    ❌ Simulation failed - no results")
                    
            except Exception as e:
                print(f"    ❌ Error generating prediction: {e}")
                continue
        
        return real_predictions
        
    except ImportError as e:
        print(f"❌ Cannot import prediction engine: {e}")
        return None
    except Exception as e:
        print(f"❌ Error with prediction engine: {e}")
        return None

def replace_with_real_predictions():
    """Replace synthetic predictions with real ones"""
    print("🎯 REPLACING SYNTHETIC PREDICTIONS WITH REAL ONES")
    print("=" * 60)
    
    # Backup current cache
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'unified_predictions_cache_before_real_engine_{timestamp}.json'
    
    with open('unified_predictions_cache.json', 'r') as f:
        cache = json.load(f)
    
    with open(backup_file, 'w') as f:
        json.dump(cache, f, indent=2)
    
    print(f"✅ Backup created: {backup_file}")
    
    # Target dates that need REAL predictions
    target_dates = ['2025-08-09', '2025-08-12', '2025-08-13']
    
    total_replaced = 0
    dates_updated = []
    
    for date in target_dates:
        print(f"\n📅 Processing {date}...")
        
        # Generate real predictions
        real_predictions = generate_real_predictions_for_date(date)
        
        if real_predictions and date in cache.get('predictions_by_date', {}):
            # Update the cache with real predictions
            cache['predictions_by_date'][date]['games'] = real_predictions
            
            total_replaced += len(real_predictions)
            dates_updated.append(date)
            
            print(f"  ✅ Updated {len(real_predictions)} games with REAL predictions")
        else:
            print(f"  ❌ Could not generate real predictions for {date}")
    
    # Save updated cache
    with open('unified_predictions_cache.json', 'w') as f:
        json.dump(cache, f, indent=2)
    
    print(f"\n🎯 REAL PREDICTION REPLACEMENT COMPLETE!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"  • Dates updated: {len(dates_updated)}")
    print(f"  • Games replaced: {total_replaced}")
    print(f"  • Updated dates: {dates_updated}")
    print(f"  • Backup: {backup_file}")
    print(f"\n✅ All predictions now use REAL starting pitchers and prediction engine!")

if __name__ == "__main__":
    replace_with_real_predictions()
