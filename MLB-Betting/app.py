# Render Deployment - Minimal MLB Betting App
from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

def load_games():
    """Load games from available data files"""
    try:
        # Try multiple file locations and names
        file_paths = [
            'data/betting_recommendations_2025_08_18.json',
            'data/betting_recommendations_2025_08_17.json',
            'data/betting_recommendations_2025_08_16.json',
            'data/unified_predictions_cache.json'
        ]
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Handle different data formats
                if isinstance(data, dict):
                    if 'games' in data and isinstance(data['games'], dict):
                        games_data = []
                        for game_key, game_data in data['games'].items():
                            if isinstance(game_data, dict):
                                games_data.append({
                                    'game_id': game_key,
                                    'away_team': game_data.get('away_team', 'Away Team'),
                                    'home_team': game_data.get('home_team', 'Home Team'),
                                    'away_pitcher': game_data.get('away_pitcher', 'TBD'),
                                    'home_pitcher': game_data.get('home_pitcher', 'TBD'),
                                    'predicted_total_runs': game_data.get('predicted_total_runs', 8.5),
                                    'win_probabilities': game_data.get('win_probabilities', {
                                        'away_prob': 0.5,
                                        'home_prob': 0.5
                                    })
                                })
                        if games_data:
                            return games_data
                    
                    # Handle unified cache format
                    elif 'predictions_by_date' in data:
                        for date_key in sorted(data['predictions_by_date'].keys(), reverse=True):
                            date_data = data['predictions_by_date'][date_key]
                            if 'games' in date_data and isinstance(date_data['games'], dict):
                                games_data = []
                                for game_key, game_data in date_data['games'].items():
                                    if isinstance(game_data, dict):
                                        games_data.append({
                                            'game_id': game_key,
                                            'away_team': game_data.get('away_team', 'Away Team'),
                                            'home_team': game_data.get('home_team', 'Home Team'),
                                            'away_pitcher': game_data.get('away_pitcher', 'TBD'),
                                            'home_pitcher': game_data.get('home_pitcher', 'TBD'),
                                            'predicted_total_runs': game_data.get('predicted_total_runs', 8.5),
                                            'win_probabilities': game_data.get('win_probabilities', {
                                                'away_prob': 0.5,
                                                'home_prob': 0.5
                                            })
                                        })
                                if games_data:
                                    return games_data
        
        return []
    except Exception as e:
        print(f"Error loading games: {e}")
        return []

@app.route('/')
def index():
    """Main page"""
    games = load_games()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLB Betting Predictions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1e3c72; color: white; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .game-card { 
                background: rgba(255,255,255,0.1); 
                margin: 10px 0; 
                padding: 20px; 
                border-radius: 10px; 
                border: 1px solid rgba(255,255,255,0.2);
            }
            .matchup { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
            .pitchers { color: #4fd1c7; margin-bottom: 15px; }
            .predictions { display: flex; justify-content: space-between; }
            .pred-item { text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚾ MLB Betting Predictions</h1>
                <p>Advanced Prediction System - {{ games|length }} Games Today</p>
                <p>Last Updated: {{ timestamp }}</p>
            </div>
            
            {% if games %}
                {% for game in games %}
                <div class="game-card">
                    <div class="matchup">{{ game.away_team }} @ {{ game.home_team }}</div>
                    <div class="pitchers">{{ game.away_pitcher }} vs {{ game.home_pitcher }}</div>
                    <div class="predictions">
                        <div class="pred-item">
                            <strong>{{ game.away_team }}</strong><br>
                            {{ "%.1f"|format(game.win_probabilities.away_prob * 100) }}%
                        </div>
                        <div class="pred-item">
                            <strong>Total Runs</strong><br>
                            {{ game.predicted_total_runs }}
                        </div>
                        <div class="pred-item">
                            <strong>{{ game.home_team }}</strong><br>
                            {{ "%.1f"|format(game.win_probabilities.home_prob * 100) }}%
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="game-card">
                    <p>No games found. Checking data files...</p>
                    <p>Files checked: betting_recommendations_2025_08_18.json, unified_predictions_cache.json</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, games=games, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health():
    """Health check"""
    games = load_games()
    return jsonify({
        "status": "healthy",
        "games_count": len(games),
        "timestamp": datetime.now().isoformat(),
        "deployment": "working"
    })

@app.route('/debug')
def debug():
    """Debug info"""
    try:
        debug_info = {
            "cwd": os.getcwd(),
            "files_exist": {},
            "data_dir_exists": os.path.exists('data'),
        }
        
        test_files = [
            'data/betting_recommendations_2025_08_18.json',
            'data/betting_recommendations_2025_08_17.json', 
            'data/betting_recommendations_2025_08_16.json',
            'data/unified_predictions_cache.json'
        ]
        
        for file_path in test_files:
            debug_info["files_exist"][file_path] = os.path.exists(file_path)
        
        if os.path.exists('data'):
            data_files = [f for f in os.listdir('data') if f.endswith('.json')]
            debug_info["data_files"] = data_files[:10]  # First 10 files
        
        games = load_games()
        debug_info["games_loaded"] = len(games)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
