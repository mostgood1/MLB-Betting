"""
Ultra-Minimal MLB Betting App for Render Deployment
Absolutely no admin features, just core data display
"""

from flask import Flask, jsonify
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_today_games():
    """Load today's games from data files"""
    today = datetime.now().strftime('%Y_%m_%d')
    
    # Try betting recommendations file
    rec_path = f'data/betting_recommendations_{today}.json'
    if os.path.exists(rec_path):
        try:
            with open(rec_path, 'r') as f:
                data = json.load(f)
                games = data.get('games', {})
                logger.info(f"Loaded {len(games)} games from recommendations")
                return list(games.values())
        except Exception as e:
            logger.error(f"Error loading recommendations: {e}")
    
    # Try unified cache
    cache_path = 'data/unified_predictions_cache.json'
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                today_str = datetime.now().strftime('%Y-%m-%d')
                today_data = data.get('predictions_by_date', {}).get(today_str, {})
                games = today_data.get('games', {})
                logger.info(f"Loaded {len(games)} games from cache")
                return list(games.values())
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    logger.warning("No games data found")
    return []

@app.route('/')
def home():
    """Main page showing today's games"""
    try:
        games = load_today_games()
        
        # Simple HTML response
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MLB Betting - Today's Games</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                .game {{ background: #ecf0f1; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #3498db; }}
                .teams {{ font-size: 20px; font-weight: bold; color: #2c3e50; }}
                .details {{ color: #7f8c8d; margin-top: 10px; }}
                .stats {{ display: flex; gap: 20px; margin-top: 10px; }}
                .stat {{ background: white; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚾ MLB Betting Analysis</h1>
                <h2>Today's Games - {datetime.now().strftime('%B %d, %Y')}</h2>
                <p><strong>{len(games)} games found</strong></p>
        """
        
        for i, game in enumerate(games[:15]):  # Limit to 15 games
            away_team = str(game.get('away_team', 'Away Team')).replace('_', ' ')
            home_team = str(game.get('home_team', 'Home Team')).replace('_', ' ')
            away_prob = game.get('away_win_probability', 0.5)
            home_prob = game.get('home_win_probability', 0.5)
            total_runs = game.get('predicted_total_runs', 9.0)
            away_pitcher = game.get('away_pitcher', 'TBD')
            home_pitcher = game.get('home_pitcher', 'TBD')
            
            html += f"""
                <div class="game">
                    <div class="teams">{away_team} @ {home_team}</div>
                    <div class="details">
                        <strong>Pitchers:</strong> {away_pitcher} vs {home_pitcher}
                    </div>
                    <div class="stats">
                        <div class="stat">
                            <strong>Win Probability:</strong><br>
                            {away_team}: {away_prob*100:.1f}%<br>
                            {home_team}: {home_prob*100:.1f}%
                        </div>
                        <div class="stat">
                            <strong>Total Runs:</strong><br>
                            {total_runs:.1f} projected
                        </div>
                    </div>
                </div>
            """
        
        if not games:
            html += """
                <div class="game">
                    <div class="teams">No games found for today</div>
                    <div class="details">Data may still be loading or today might be an off day</div>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return f"""
        <html><body>
        <h1>MLB Betting System</h1>
        <p>System starting up... Error: {str(e)}</p>
        <p>Try refreshing in a moment.</p>
        </body></html>
        """

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'service': 'mlb-betting-minimal'
    })

@app.route('/debug-files')
def debug_files():
    """Debug route to check available files"""
    debug_info = {
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        'app_directory': os.path.dirname(os.path.abspath(__file__)),
        'data_directory_exists': os.path.exists('data'),
        'data_files': []
    }
    
    if os.path.exists('data'):
        try:
            data_files = [f for f in os.listdir('data') if f.endswith('.json')]
            debug_info['data_files'] = data_files[:20]
        except Exception as e:
            debug_info['data_files_error'] = str(e)
    
    return jsonify(debug_info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
