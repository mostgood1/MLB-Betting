"""
Render-Specific MLB Betting App
Simple, stable version designed specifically for cloud deployment
Does not interfere with the local robust app.py
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_today_games_safe():
    """Safely load today's games for Render environment"""
    try:
        today = datetime.now().strftime('%Y_%m_%d')
        today_dash = datetime.now().strftime('%Y-%m-%d')
        
        # Try different file patterns that exist on Render
        file_patterns = [
            f'data/betting_recommendations_{today}.json',
            f'data/betting_recommendations_{today_dash}.json',
            'data/unified_predictions_cache.json'
        ]
        
        for file_path in file_patterns:
            if os.path.exists(file_path):
                logger.info(f"Found data file: {file_path}")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Handle different data structures safely
                games_data = []
                
                if isinstance(data, dict):
                    if 'games' in data:
                        games_dict = data['games']
                        if isinstance(games_dict, dict):
                            # Convert dict to list of games
                            for game_key, game_data in games_dict.items():
                                if isinstance(game_data, dict):
                                    # Ensure game has required fields
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
                        elif isinstance(games_dict, list):
                            games_data = games_dict
                    
                    elif 'predictions_by_date' in data:
                        # Handle unified cache format
                        today_data = data['predictions_by_date'].get(today_dash, {})
                        if 'games' in today_data and isinstance(today_data['games'], dict):
                            for game_key, game_data in today_data['games'].items():
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
                    logger.info(f"Successfully loaded {len(games_data)} games from {file_path}")
                    return games_data
                
        logger.warning("No valid games data found")
        return []
        
    except Exception as e:
        logger.error(f"Error loading games data: {e}")
        return []

@app.route('/')
def index():
    """Simple index page showing today's games"""
    try:
        games = load_today_games_safe()
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MLB Betting Analysis</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .game-card { background: white; margin: 15px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .teams { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                .pitchers { color: #666; margin-bottom: 10px; }
                .probabilities { display: flex; justify-content: space-between; margin-bottom: 10px; }
                .prob { padding: 5px 10px; border-radius: 4px; }
                .away-prob { background: #e3f2fd; }
                .home-prob { background: #f3e5f5; }
                .total-runs { color: #333; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚾ MLB Betting Analysis</h1>
                    <h2>Today's Games - {{ today }}</h2>
                    <p>{{ games|length }} games found</p>
                </div>
                
                {% for game in games %}
                <div class="game-card">
                    <div class="teams">{{ game.away_team }} @ {{ game.home_team }}</div>
                    <div class="pitchers">Pitchers: {{ game.away_pitcher }} vs {{ game.home_pitcher }}</div>
                    <div class="probabilities">
                        <div class="prob away-prob">
                            <strong>{{ game.away_team }}:</strong> {{ "%.1f"|format(game.win_probabilities.away_prob * 100) }}%
                        </div>
                        <div class="prob home-prob">
                            <strong>{{ game.home_team }}:</strong> {{ "%.1f"|format(game.win_probabilities.home_prob * 100) }}%
                        </div>
                    </div>
                    <div class="total-runs">
                        <strong>Total Runs:</strong> {{ game.predicted_total_runs }} projected
                    </div>
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_template, 
                                    games=games, 
                                    today=datetime.now().strftime('%B %d, %Y'))
        
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error loading games",
            "status": "MLB Betting System Live",
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/games')
def api_games():
    """API endpoint for games data"""
    try:
        games = load_today_games_safe()
        return jsonify({
            "status": "success",
            "games_count": len(games),
            "games": games,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in API route: {e}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Render MLB Betting App Running",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
