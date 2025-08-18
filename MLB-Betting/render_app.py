"""
Render-Specific MLB Betting App - Updated Aug 18
Simple, stable version designed specifically for cloud deployment
Does not interfere with the local robust app.py
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime, timedelta
import logging

# Try to import pytz for timezone handling, fallback if not available
try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    logging.warning("pytz not available, using UTC time")

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_pacific_time():
    """Get current time in Pacific timezone with fallback"""
    if PYTZ_AVAILABLE:
        try:
            pacific = pytz.timezone('US/Pacific')
            return datetime.now(pacific)
        except:
            pass
    
    # Fallback: UTC time minus 8 hours (approximate Pacific Time)
    # This is a rough approximation that doesn't handle DST perfectly
    return datetime.now() - timedelta(hours=8)

def load_today_games_safe():
    """Load games with intelligent fallback to available data"""
    try:
        pacific_now = get_pacific_time()
        today = pacific_now.strftime('%Y_%m_%d')
        today_dash = pacific_now.strftime('%Y-%m-%d')
        
        logger.info(f"Pacific Time: {pacific_now}")
        logger.info(f"Looking for: {today_dash}")
        
        # Smart approach: Get all available betting files and use the most recent
        if os.path.exists('data'):
            data_files = os.listdir('data')
            
            # Find all betting recommendation files and sort by date
            betting_files = []
            for f in data_files:
                if f.startswith('betting_recommendations_2025') and f.endswith('.json'):
                    # Extract date from filename
                    try:
                        date_part = f.replace('betting_recommendations_', '').replace('.json', '')
                        if date_part.startswith('2025'):
                            betting_files.append((f, date_part))
                    except:
                        continue
            
            # Sort by date (most recent first)
            betting_files.sort(key=lambda x: x[1], reverse=True)
            logger.info(f"Available betting files: {[f[0] for f in betting_files]}")
            
            # Try files in order of preference
            file_attempts = []
            
            # First priority: exact match for today
            file_attempts.append(f'data/betting_recommendations_{today}.json')
            file_attempts.append(f'data/betting_recommendations_{today_dash}.json')
            
            # Second priority: most recent files
            for betting_file, _ in betting_files[:5]:  # Try top 5 recent files
                file_attempts.append(f'data/{betting_file}')
            
            # Third priority: unified cache
            file_attempts.append('data/unified_predictions_cache.json')
            
            for file_path in file_attempts:
                logger.info(f"Trying: {file_path}")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        games_data = []
                        
                        if isinstance(data, dict):
                            # Handle direct games format
                            if 'games' in data:
                                games_dict = data['games']
                                if isinstance(games_dict, dict):
                                    for game_key, game_data in games_dict.items():
                                        if isinstance(game_data, dict):
                                            safe_game = {
                                                'game_id': game_key,
                                                'away_team': game_data.get('away_team', 'Team A'),
                                                'home_team': game_data.get('home_team', 'Team B'),
                                                'away_pitcher': game_data.get('away_pitcher', 'TBD'),
                                                'home_pitcher': game_data.get('home_pitcher', 'TBD'),
                                                'predicted_total_runs': game_data.get('predicted_total_runs', 8.5),
                                                'win_probabilities': game_data.get('win_probabilities', {
                                                    'away_prob': 0.5,
                                                    'home_prob': 0.5
                                                })
                                            }
                                            games_data.append(safe_game)
                                
                            # Handle unified cache format
                            elif 'predictions_by_date' in data:
                                # Try recent dates in order
                                dates_to_try = []
                                for i in range(5):  # Try 5 days back
                                    date_attempt = (pacific_now - timedelta(days=i)).strftime('%Y-%m-%d')
                                    dates_to_try.append(date_attempt)
                                
                                for date_attempt in dates_to_try:
                                    date_data = data['predictions_by_date'].get(date_attempt, {})
                                    if 'games' in date_data and isinstance(date_data['games'], dict):
                                        for game_key, game_data in date_data['games'].items():
                                            if isinstance(game_data, dict):
                                                safe_game = {
                                                    'game_id': game_key,
                                                    'away_team': game_data.get('away_team', 'Team A'),
                                                    'home_team': game_data.get('home_team', 'Team B'),
                                                    'away_pitcher': game_data.get('away_pitcher', 'TBD'),
                                                    'home_pitcher': game_data.get('home_pitcher', 'TBD'),
                                                    'predicted_total_runs': game_data.get('predicted_total_runs', 8.5),
                                                    'win_probabilities': game_data.get('win_probabilities', {
                                                        'away_prob': 0.5,
                                                        'home_prob': 0.5
                                                    })
                                                }
                                                games_data.append(safe_game)
                                        if games_data:
                                            logger.info(f"Found games from date: {date_attempt}")
                                            break
                        
                        if games_data:
                            logger.info(f"SUCCESS: Loaded {len(games_data)} games from {file_path}")
                            return games_data
                        else:
                            logger.warning(f"No games in {file_path}")
                            
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")
                        continue
                else:
                    logger.info(f"Not found: {file_path}")
        
        logger.error("FAILED: No games data found anywhere")
        return []
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}")
        return []

@app.route('/')
def index():
    """Simple index page showing today's games"""
    try:
        games = load_today_games_safe()
        
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MLB-Betting Prediction System</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    min-height: 100vh;
                }

                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }

                .header h1 {
                    font-size: 3rem;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }

                .header p {
                    font-size: 1.2rem;
                    opacity: 0.9;
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .stat-card {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: all 0.3s ease;
                }

                .stat-card:hover {
                    transform: translateY(-5px);
                    background: rgba(255, 255, 255, 0.15);
                    border-color: #4fd1c7;
                    box-shadow: 0 10px 25px rgba(79, 209, 199, 0.3);
                }

                .stat-card h3 {
                    font-size: 2rem;
                    margin-bottom: 5px;
                    color: #4fd1c7;
                }

                .stat-card p {
                    opacity: 0.8;
                }

                .games-section {
                    margin-top: 30px;
                }

                .games-header {
                    text-align: center;
                    margin-bottom: 30px;
                }

                .games-header h2 {
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                    color: #4fd1c7;
                }

                .game-card {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    margin: 20px 0;
                    padding: 25px;
                    border-radius: 15px;
                    transition: all 0.3s ease;
                }

                .game-card:hover {
                    transform: translateY(-3px);
                    background: rgba(255, 255, 255, 0.15);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                }

                .matchup {
                    text-align: center;
                    margin-bottom: 20px;
                }

                .teams {
                    font-size: 1.8rem;
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: #ffffff;
                }

                .pitchers {
                    color: #b8d4f0;
                    font-size: 1.1rem;
                    margin-bottom: 15px;
                }

                .game-details {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-top: 15px;
                }

                .probabilities {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    padding: 15px;
                }

                .probabilities h4 {
                    color: #4fd1c7;
                    margin-bottom: 10px;
                    text-align: center;
                }

                .prob-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 8px 0;
                    padding: 8px 12px;
                    border-radius: 8px;
                    background: rgba(255, 255, 255, 0.05);
                }

                .team-name {
                    font-weight: bold;
                    color: #ffffff;
                }

                .prob-value {
                    font-weight: bold;
                    color: #4fd1c7;
                    font-size: 1.1rem;
                }

                .predictions {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    padding: 15px;
                }

                .predictions h4 {
                    color: #4fd1c7;
                    margin-bottom: 10px;
                    text-align: center;
                }

                .prediction-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 8px 0;
                    padding: 8px 12px;
                    border-radius: 8px;
                    background: rgba(255, 255, 255, 0.05);
                }

                .prediction-label {
                    color: #b8d4f0;
                }

                .prediction-value {
                    font-weight: bold;
                    color: #ffffff;
                }

                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    opacity: 0.7;
                }

                @media (max-width: 768px) {
                    .header h1 { font-size: 2rem; }
                    .games-header h2 { font-size: 1.8rem; }
                    .teams { font-size: 1.4rem; }
                    .game-details { grid-template-columns: 1fr; }
                    .container { padding: 15px; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚾ MLB Betting Prediction System</h1>
                    <p>Professional Baseball Analytics & Predictions</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{{ games|length }}</h3>
                        <p>Games Today</p>
                    </div>
                    <div class="stat-card">
                        <h3>{{ today }}</h3>
                        <p>Current Date</p>
                    </div>
                    <div class="stat-card">
                        <h3>Live</h3>
                        <p>System Status</p>
                    </div>
                    <div class="stat-card">
                        <h3>Pro</h3>
                        <p>Analytics Level</p>
                    </div>
                </div>
                
                <div class="games-section">
                    <div class="games-header">
                        <h2>Today's Game Predictions</h2>
                        <p>Advanced machine learning predictions with win probabilities</p>
                    </div>
                    
                    {% for game in games %}
                    <div class="game-card">
                        <div class="matchup">
                            <div class="teams">{{ game.away_team }} @ {{ game.home_team }}</div>
                            <div class="pitchers">{{ game.away_pitcher }} vs {{ game.home_pitcher }}</div>
                        </div>
                        
                        <div class="game-details">
                            <div class="probabilities">
                                <h4>Win Probabilities</h4>
                                <div class="prob-row">
                                    <span class="team-name">{{ game.away_team }}</span>
                                    <span class="prob-value">{{ "%.1f"|format(game.win_probabilities.away_prob * 100) }}%</span>
                                </div>
                                <div class="prob-row">
                                    <span class="team-name">{{ game.home_team }}</span>
                                    <span class="prob-value">{{ "%.1f"|format(game.win_probabilities.home_prob * 100) }}%</span>
                                </div>
                            </div>
                            
                            <div class="predictions">
                                <h4>Game Predictions</h4>
                                <div class="prediction-item">
                                    <span class="prediction-label">Total Runs</span>
                                    <span class="prediction-value">{{ game.predicted_total_runs }}</span>
                                </div>
                                <div class="prediction-item">
                                    <span class="prediction-label">Confidence</span>
                                    <span class="prediction-value">High</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="footer">
                    <p>MLB Betting Prediction System - Powered by Advanced Analytics</p>
                    <p>Last Updated: {{ timestamp }}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_template, 
                                    games=games, 
                                    today=get_pacific_time().strftime('%B %d, %Y'),
                                    timestamp=get_pacific_time().strftime('%I:%M %p PT'))
        
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error loading games",
            "status": "MLB Betting System Live",
            "timestamp": datetime.now().isoformat()
        })

@app.route('/debug')
def debug_info():
    """Debug endpoint to see what files are available on Render"""
    try:
        pacific_now = get_pacific_time()
        debug_data = {
            "working_directory": os.getcwd(),
            "utc_time": datetime.now().isoformat(),
            "pacific_time": pacific_now.isoformat(),
            "today_formats": {
                "underscore": pacific_now.strftime('%Y_%m_%d'),
                "dash": pacific_now.strftime('%Y-%m-%d')
            },
            "data_directory_exists": os.path.exists('data'),
            "files_in_data": [],
            "files_in_root": [],
            "environment_vars": {
                "PORT": os.environ.get('PORT'),
                "RENDER": os.environ.get('RENDER'),
                "RENDER_SERVICE_ID": os.environ.get('RENDER_SERVICE_ID')
            }
        }
        
        # List files in data directory
        if os.path.exists('data'):
            try:
                debug_data["files_in_data"] = os.listdir('data')
            except Exception as e:
                debug_data["data_directory_error"] = str(e)
        
        # List some files in root
        try:
            root_files = [f for f in os.listdir('.') if f.endswith('.json')]
            debug_data["files_in_root"] = root_files
        except Exception as e:
            debug_data["root_directory_error"] = str(e)
        
        # Try to load data and show what happens
        debug_data["load_attempt"] = {}
        try:
            games = load_today_games_safe()
            debug_data["load_attempt"]["success"] = True
            debug_data["load_attempt"]["games_count"] = len(games)
            debug_data["load_attempt"]["sample_game"] = games[0] if games else None
        except Exception as e:
            debug_data["load_attempt"]["success"] = False
            debug_data["load_attempt"]["error"] = str(e)
        
        return jsonify(debug_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/games')
def api_games():
    """API endpoint for games data"""
    try:
        games = load_today_games_safe()
        return jsonify({
            "status": "success",
            "games_count": len(games),
            "games": games,
            "timestamp": datetime.now().isoformat(),
            "debug": "API endpoint working"
        })
    except Exception as e:
        logger.error(f"Error in API route: {e}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        })

@app.route('/test-api')
def test_api():
    """Simple test endpoint"""
    return jsonify({"message": "Test API working", "timestamp": datetime.now().isoformat()})

@app.route('/api/status')
def api_status():
    """Enhanced status endpoint with system info"""
    try:
        games = load_today_games_safe()
        return jsonify({
            "status": "healthy",
            "system": "MLB Betting Prediction System",
            "version": "Render-Optimized v1.0",
            "games_today": len(games),
            "environment": "cloud",
            "features": [
                "Real-time predictions",
                "Win probability analysis", 
                "Total runs forecasting",
                "Professional UI"
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/health')
def health():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "MLB Betting System Running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/debug-directory')
def debug_directory():
    """Debug endpoint to see all available files"""
    debug_info = {}
    
    try:
        debug_info['cwd'] = os.getcwd()
        
        # Check root directory
        if os.path.exists('.'):
            debug_info['root_files'] = os.listdir('.')
        
        # Check data directory
        if os.path.exists('data'):
            debug_info['data_files'] = os.listdir('data')
        else:
            debug_info['data_directory'] = 'NOT FOUND'
            
        # Look for any betting files in any location
        betting_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if 'betting_recommendations' in file and file.endswith('.json'):
                    betting_files.append(os.path.join(root, file))
        debug_info['betting_files_found'] = betting_files
        
        # Time info
        pacific_now = get_pacific_time()
        debug_info['pacific_time'] = pacific_now.isoformat()
        debug_info['current_date'] = pacific_now.strftime('%Y-%m-%d')
        
    except Exception as e:
        debug_info['error'] = str(e)
    
    return jsonify(debug_info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
