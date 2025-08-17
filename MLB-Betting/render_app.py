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
                                    today=datetime.now().strftime('%B %d, %Y'),
                                    timestamp=datetime.now().strftime('%I:%M %p'))
        
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
