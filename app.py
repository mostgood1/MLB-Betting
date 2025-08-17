"""
MLB Betting Predictions System - Real Production Version
Uses actual MLB-Betting directory structure and real data
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
from datetime import datetime, timedelta
import logging

# Add MLB-Betting directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'MLB-Betting'))

# Create Flask app with proper template and static paths
app = Flask(__name__, 
           template_folder='MLB-Betting/templates',
           static_folder='MLB-Betting/static')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_cache_data():
    """Load real predictions from cache"""
    try:
        cache_path = 'MLB-Betting/data/unified_predictions_cache.json'
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
        return None

def get_team_assets():
    """Load team assets if available"""
    try:
        assets_path = 'MLB-Betting/team_assets_utils.py'
        if os.path.exists(assets_path):
            # Import team assets utilities
            import importlib.util
            spec = importlib.util.spec_from_file_location("team_assets_utils", assets_path)
            team_assets = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(team_assets)
            return team_assets
        return None
    except Exception as e:
        logger.error(f"Error loading team assets: {e}")
        return None

def get_live_status_for_game(away_team, home_team, date=None):
    """Get live status for a specific game using real MLB data"""
    try:
        # Import live MLB data functions
        live_status_path = 'MLB-Betting/live_mlb_data.py'
        if os.path.exists(live_status_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("live_mlb_data", live_status_path)
            live_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(live_module)
            
            # Call the actual get_live_game_status function
            live_status = live_module.get_live_game_status(away_team, home_team, date)
            return live_status
        return None
    except Exception as e:
        logger.error(f"Error getting live status for {away_team} @ {home_team}: {e}")
        return None

def calculate_expected_value(win_probability, american_odds):
    """Calculate Expected Value for a bet"""
    try:
        if american_odds > 0:
            decimal_odds = (american_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(american_odds)) + 1
        
        expected_value = (win_probability * decimal_odds) - 1
        return round(expected_value, 3)
    except:
        return 0

@app.route('/')
def index():
    """Main page using real index.html template"""
    try:
        # Load real cache data
        cache_data = load_cache_data()
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        games = []
        if cache_data and 'games' in cache_data:
            games = cache_data['games'].get(today_str, [])
            
            # Add betting recommendations with EV calculations
            for game in games:
                if 'betting_recommendations' not in game:
                    # Create basic betting recommendations from predictions
                    predictions = game.get('predictions', {})
                    away_win_prob = predictions.get('away_win_probability', 0.5)
                    home_win_prob = predictions.get('home_win_probability', 0.5)
                    
                    value_bets = []
                    
                    # Moneyline recommendations
                    if away_win_prob > 0.52:
                        ev = calculate_expected_value(away_win_prob, -120)
                        value_bets.append({
                            'type': 'moneyline',
                            'recommendation': f"{game.get('away_team', 'Away')} ML",
                            'expected_value': ev,
                            'win_probability': away_win_prob,
                            'american_odds': -120
                        })
                    
                    if home_win_prob > 0.52:
                        ev = calculate_expected_value(home_win_prob, -115)
                        value_bets.append({
                            'type': 'moneyline',
                            'recommendation': f"{game.get('home_team', 'Home')} ML",
                            'expected_value': ev,
                            'win_probability': home_win_prob,
                            'american_odds': -115
                        })
                    
                    # Total runs recommendations
                    total_runs = predictions.get('total_runs', 8.5)
                    if total_runs > 9.0:
                        ev = calculate_expected_value(0.53, -110)
                        value_bets.append({
                            'type': 'total',
                            'recommendation': f"Over {total_runs - 0.5}",
                            'expected_value': ev,
                            'win_probability': 0.53,
                            'american_odds': -110
                        })
                    
                    game['betting_recommendations'] = {'value_bets': value_bets}
                
                # Get real live status for each game
                away_team = game.get('away_team', '')
                home_team = game.get('home_team', '')
                
                if away_team and home_team:
                    live_status = get_live_status_for_game(away_team, home_team, today_str)
                    if live_status:
                        game['live_status'] = live_status
                        # Also add live status fields directly to game for JavaScript access
                        game['away_score'] = live_status.get('away_score')
                        game['home_score'] = live_status.get('home_score')
                        game['status'] = live_status.get('status', 'Scheduled')
                        game['is_live'] = live_status.get('is_live', False)
                        game['is_final'] = live_status.get('is_final', False)
                        game['inning'] = live_status.get('inning')
                        game['inning_state'] = live_status.get('inning_state')
                    else:
                        # Fallback to basic status
                        game['live_status'] = {
                            'status': 'Scheduled',
                            'is_live': False,
                            'is_final': False,
                            'away_score': 0,
                            'home_score': 0
                        }
                        game['away_score'] = 0
                        game['home_score'] = 0
                        game['status'] = 'Scheduled'
                        game['is_live'] = False
                        game['is_final'] = False
                else:
                    game['live_status'] = {
                        'status': 'Scheduled',
                        'is_live': False,
                        'is_final': False,
                        'away_score': 0,
                        'home_score': 0
                    }
                    game['away_score'] = 0
                    game['home_score'] = 0
                    game['status'] = 'Scheduled'
                    game['is_live'] = False
                    game['is_final'] = False
        
        return render_template('index.html', 
                             games=games,
                             date=today_str,
                             last_updated=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        # Fallback to simple JSON response if template fails
        return jsonify({
            "status": "MLB Betting System Live",
            "message": "Loading real data...",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/today-games')
def api_today_games():
    """API endpoint for today's games with real data"""
    try:
        date_param = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        cache_data = load_cache_data()
        
        games = []
        if cache_data and 'games' in cache_data:
            games = cache_data['games'].get(date_param, [])
            
            # Add EV calculations and live status to each game
            for game in games:
                if 'betting_recommendations' not in game:
                    predictions = game.get('predictions', {})
                    away_win_prob = predictions.get('away_win_probability', 0.5)
                    
                    value_bets = [{
                        'type': 'moneyline',
                        'recommendation': f"{game.get('away_team', 'Away')} ML",
                        'expected_value': calculate_expected_value(away_win_prob, -120),
                        'win_probability': away_win_prob,
                        'american_odds': -120
                    }]
                    
                    game['betting_recommendations'] = {'value_bets': value_bets}
                
                # Add real live status
                away_team = game.get('away_team', '')
                home_team = game.get('home_team', '')
                
                if away_team and home_team:
                    live_status = get_live_status_for_game(away_team, home_team, date_param)
                    if live_status:
                        game['live_status'] = live_status
                        # Also add live status fields directly to game for JavaScript access
                        game['away_score'] = live_status.get('away_score')
                        game['home_score'] = live_status.get('home_score')
                        game['status'] = live_status.get('status', 'Scheduled')
                        game['is_live'] = live_status.get('is_live', False)
                        game['is_final'] = live_status.get('is_final', False)
                        game['inning'] = live_status.get('inning')
                        game['inning_state'] = live_status.get('inning_state')
        
        return jsonify({
            'games': games,
            'date': date_param,
            'total_games': len(games),
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in API: {e}")
        return jsonify({'error': str(e), 'games': []})

@app.route('/api/live-status')
def api_live_status():
    """Live status API using real MLB data"""
    try:
        # Import live MLB data functions
        live_status_path = 'MLB-Betting/live_mlb_data.py'
        if os.path.exists(live_status_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("live_mlb_data", live_status_path)
            live_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(live_module)
            
            # Get today's enhanced games data
            live_mlb_instance = live_module.LiveMLBData()
            enhanced_games = live_mlb_instance.get_enhanced_games_data()
            
            # Filter for live and final games
            live_games = []
            final_games = []
            
            for game in enhanced_games:
                if game.get('is_live'):
                    live_games.append({
                        'away_team': game.get('away_team'),
                        'home_team': game.get('home_team'),
                        'away_score': game.get('away_score', 0),
                        'home_score': game.get('home_score', 0),
                        'status': game.get('status', 'Live'),
                        'inning': game.get('inning_state', ''),
                        'is_live': True
                    })
                elif game.get('is_final'):
                    final_games.append({
                        'away_team': game.get('away_team'),
                        'home_team': game.get('home_team'),
                        'away_score': game.get('away_score', 0),
                        'home_score': game.get('home_score', 0),
                        'status': 'Final',
                        'is_final': True
                    })
            
            return jsonify({
                'live_games': live_games,
                'final_games': final_games,
                'total_live': len(live_games),
                'total_final': len(final_games),
                'last_updated': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'live_games': [],
                'total_live': 0,
                'message': 'Live status module not found',
                'last_updated': datetime.now().isoformat()
            })
    
    except Exception as e:
        logger.error(f"Error in live status API: {e}")
        return jsonify({'error': str(e), 'live_games': [], 'total_live': 0})

@app.route('/health')
def health():
    """Health check with real system status"""
    try:
        cache_data = load_cache_data()
        cache_status = "loaded" if cache_data else "not found"
        
        return jsonify({
            "status": "healthy",
            "service": "mlb-betting-production-real",
            "cache_status": cache_status,
            "features": [
                "Real predictions data",
                "Expected Value calculations", 
                "Template rendering",
                "API endpoints"
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Starting Real MLB Betting System on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
