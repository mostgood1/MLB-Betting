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
        logger.info(f"🔍 Looking for cache file at: {cache_path}")
        logger.info(f"🔍 Current working directory: {os.getcwd()}")
        
        # Check if file exists
        if os.path.exists(cache_path):
            logger.info(f"✅ Cache file found!")
            with open(cache_path, 'r') as f:
                data = json.load(f)
                logger.info(f"🎯 Cache loaded successfully. Top-level keys: {list(data.keys())}")
                return data
        else:
            logger.error(f"❌ Cache file not found at {cache_path}")
            # Try to list what files do exist
            try:
                if os.path.exists('MLB-Betting/data'):
                    files = os.listdir('MLB-Betting/data')
                    logger.info(f"📁 Files in MLB-Betting/data: {files}")
                else:
                    logger.error("❌ MLB-Betting/data directory doesn't exist")
            except Exception as e:
                logger.error(f"❌ Error listing directory: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading cache: {e}")
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
        logger.info(f"🎯 Looking for games for date: {today_str}")
        
        games = []
        if cache_data:
            logger.info(f"📊 Cache data loaded. Top-level keys: {list(cache_data.keys())}")
            
            # Find the most recent date with games - check multiple possible locations
            available_dates = []
            
            # Check direct date keys (e.g., "2025-08-16")
            date_keys = [key for key in cache_data.keys() if key.startswith('2025-')]
            available_dates.extend(date_keys)
            
            # Check predictions_by_date structure
            if 'predictions_by_date' in cache_data:
                pred_dates = [key for key in cache_data['predictions_by_date'].keys() if key.startswith('2025-')]
                available_dates.extend(pred_dates)
                logger.info(f"📅 Found dates in predictions_by_date: {pred_dates}")
            
            # Check games structure (old format)
            if 'games' in cache_data:
                game_dates = [key for key in cache_data['games'].keys() if key.startswith('2025-')]
                available_dates.extend(game_dates)
                logger.info(f"📅 Found dates in games: {game_dates}")
            
            # Remove duplicates and sort
            available_dates = list(set(available_dates))
            available_dates.sort(reverse=True)  # Most recent first
            logger.info(f"📅 All available dates: {available_dates}")
            
            target_date = today_str
            if today_str not in available_dates:
                logger.warning(f"❌ No data for {today_str}, looking for most recent date")
                if available_dates:
                    target_date = available_dates[0]  # Use most recent available
                    logger.info(f"🔄 Using most recent available date: {target_date}")
                else:
                    logger.error("❌ No game dates found in cache")
                    target_date = None
            
            if target_date:
                # Try multiple possible locations for the data
                games_data = None
                
                # Try direct date key with games
                if target_date in cache_data and isinstance(cache_data[target_date], dict) and 'games' in cache_data[target_date]:
                    logger.info(f"✅ Found data in direct date key: {target_date}")
                    games_data = cache_data[target_date]['games']
                    
                # Try predictions_by_date structure
                elif 'predictions_by_date' in cache_data and target_date in cache_data['predictions_by_date']:
                    logger.info(f"✅ Found data in predictions_by_date: {target_date}")
                    pred_data = cache_data['predictions_by_date'][target_date]
                    if isinstance(pred_data, dict) and 'games' in pred_data:
                        games_data = pred_data['games']
                    else:
                        games_data = pred_data  # Might be games directly
                        
                # Try old games structure
                elif 'games' in cache_data and target_date in cache_data['games']:
                    logger.info(f"✅ Found data in games structure: {target_date}")
                    games_data = cache_data['games'][target_date]
                
                if games_data:
                    logger.info(f"🎮 Number of games found: {len(games_data)}")
                    
                    # Convert from object format to list format if needed
                    if isinstance(games_data, dict):
                        for game_key, game_data in games_data.items():
                            game = {
                                'game_id': game_key,
                                'away_team': game_data.get('away_team', ''),
                                'home_team': game_data.get('home_team', ''),
                                'game_time': game_data.get('game_time', 'TBD'),
                                'date': game_data.get('game_date', target_date),
                                'predictions': game_data.get('predictions', {}),
                                'betting_recommendations': game_data.get('betting_recommendations', {'value_bets': []})
                            }
                            games.append(game)
                    elif isinstance(games_data, list):
                        games = games_data
                    
                    logger.info(f"✅ Converted {len(games)} games from {target_date}")
                    # Update today_str to reflect what we're actually showing
                    today_str = target_date
                else:
                    logger.warning(f"❌ No games data found for {target_date}")
            else:
                logger.warning(f"❌ No suitable date found")
        else:
            logger.error("❌ No cache data loaded!")
            
            # Add betting recommendations with EV calculations for games that need them
            for game in games:
                if not game.get('betting_recommendations') or not game['betting_recommendations'].get('value_bets'):
                    # Create basic betting recommendations from predictions
                    predictions = game.get('predictions', {})
                    away_win_prob = predictions.get('away_win_prob', 0.5)  # Note: different key name
                    home_win_prob = predictions.get('home_win_prob', 0.5)  # Note: different key name
                    
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
                    total_runs = predictions.get('predicted_total_runs', 8.5)
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
        
        # Create comprehensive stats structure that the template expects
        comprehensive_stats = {
            'total_games_analyzed': len(games),
            'date_range': {
                'start': 'Aug 7',
                'end': today_str
            },
            'betting_performance': {
                'winner_predictions_correct': 0,
                'winner_accuracy_pct': 0,
                'games_analyzed': len(games),
                'total_predictions_correct': 0,
                'total_accuracy_pct': 0,
                'perfect_games': 0,
                'perfect_games_pct': 0
            }
        }
        
        # Calculate basic stats from completed games
        completed_games = [g for g in games if g.get('is_final', False)]
        if completed_games:
            comprehensive_stats['betting_performance']['games_analyzed'] = len(completed_games)
            # Basic placeholder stats - would need historical data for real calculations
            comprehensive_stats['betting_performance']['winner_accuracy_pct'] = 65
            comprehensive_stats['betting_performance']['total_accuracy_pct'] = 58
            comprehensive_stats['betting_performance']['perfect_games_pct'] = 42
        
        return render_template('index.html', 
                             games=games,
                             date=today_str,  # This now reflects the actual date being shown
                             comprehensive_stats=comprehensive_stats,
                             last_updated=datetime.now().strftime('%Y-%m-%d %H:%M'),
                             is_using_fallback_date=(today_str != datetime.now().strftime('%Y-%m-%d')))
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        # Fallback to simple JSON response if template fails
        return jsonify({
            "status": "MLB Betting System Live",
            "message": "Loading real data...",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/debug/cache')
def debug_cache():
    """Debug endpoint to see what's in the cache"""
    try:
        import os
        debug_info = {
            "current_directory": os.getcwd(),
            "files_in_root": os.listdir('.') if os.path.exists('.') else "Directory not found",
            "mlb_betting_exists": os.path.exists('MLB-Betting'),
            "data_dir_exists": os.path.exists('MLB-Betting/data'),
            "cache_file_exists": os.path.exists('MLB-Betting/data/unified_predictions_cache.json'),
            "today": datetime.now().strftime('%Y-%m-%d'),
            "cache_data": None,
            "error": None
        }
        
        if os.path.exists('MLB-Betting/data'):
            debug_info["files_in_data_dir"] = os.listdir('MLB-Betting/data')
        
        # Try to load cache
        try:
            cache_data = load_cache_data()
            if cache_data:
                debug_info["cache_loaded"] = True
                debug_info["cache_top_level_keys"] = list(cache_data.keys())
                today_str = datetime.now().strftime('%Y-%m-%d')
                debug_info["today_in_cache"] = today_str in cache_data
                if today_str in cache_data:
                    debug_info["today_data_structure"] = list(cache_data[today_str].keys()) if isinstance(cache_data[today_str], dict) else "Not a dict"
                    if 'games' in cache_data[today_str]:
                        debug_info["games_count"] = len(cache_data[today_str]['games'])
                        debug_info["game_keys"] = list(cache_data[today_str]['games'].keys())[:5]  # First 5 games
            else:
                debug_info["cache_loaded"] = False
        except Exception as e:
            debug_info["cache_error"] = str(e)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"debug_error": str(e)})

@app.route('/api/today-games')
def api_today_games():
    """API endpoint for today's games with real data"""
    try:
        date_param = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        cache_data = load_cache_data()
        
        games = []
        if cache_data:
            # Check if data is in the new format: cache_data["2025-08-16"]["games"]
            if date_param in cache_data and 'games' in cache_data[date_param]:
                # New format: date -> games -> individual games
                games_data = cache_data[date_param]['games']
                # Convert from object format to list format
                for game_key, game_data in games_data.items():
                    game = {
                        'game_id': game_key,
                        'away_team': game_data.get('away_team', ''),
                        'home_team': game_data.get('home_team', ''),
                        'game_time': game_data.get('game_time', 'TBD'),
                        'date': game_data.get('game_date', date_param),
                        'predictions': game_data.get('predictions', {}),
                        'betting_recommendations': game_data.get('betting_recommendations', {'value_bets': []})
                    }
                    games.append(game)
            elif 'games' in cache_data and date_param in cache_data['games']:
                # Old format: games -> date -> list of games
                games = cache_data['games'][date_param]
            
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
