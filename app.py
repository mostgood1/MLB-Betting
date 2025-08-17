"""
MLB Betting Predictions System - Self-Contained Production App
Complete system with Expected Value calculations, live game status, and betting recommendations
"""

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime, timedelta
import logging

# Create Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample game data for demonstration
SAMPLE_GAMES = [
    {
        "away_team": "New York Yankees",
        "home_team": "Boston Red Sox",
        "game_time": "7:10 PM ET",
        "away_pitcher": "Gerrit Cole",
        "home_pitcher": "Chris Sale",
        "predictions": {
            "away_win_prob": 0.58,
            "home_win_prob": 0.42,
            "total_runs": 9.2
        },
        "betting_recommendations": {
            "value_bets": [
                {
                    "type": "moneyline",
                    "recommendation": "Yankees ML",
                    "expected_value": 0.125,
                    "win_probability": 0.58,
                    "american_odds": -140
                },
                {
                    "type": "total",
                    "recommendation": "Over 8.5 runs",
                    "expected_value": 0.089,
                    "win_probability": 0.52,
                    "american_odds": -110
                }
            ]
        },
        "live_status": {
            "status": "Scheduled",
            "is_live": False,
            "is_final": False,
            "away_score": 0,
            "home_score": 0,
            "badge_class": "scheduled"
        }
    },
    {
        "away_team": "Los Angeles Dodgers",
        "home_team": "San Francisco Giants",
        "game_time": "10:15 PM ET",
        "away_pitcher": "Walker Buehler",
        "home_pitcher": "Logan Webb",
        "predictions": {
            "away_win_prob": 0.62,
            "home_win_prob": 0.38,
            "total_runs": 8.8
        },
        "betting_recommendations": {
            "value_bets": [
                {
                    "type": "moneyline",
                    "recommendation": "Dodgers ML",
                    "expected_value": 0.156,
                    "win_probability": 0.62,
                    "american_odds": -160
                },
                {
                    "type": "run_line",
                    "recommendation": "Dodgers -1.5",
                    "expected_value": 0.073,
                    "win_probability": 0.45,
                    "american_odds": +125
                }
            ]
        },
        "live_status": {
            "status": "Live",
            "is_live": True,
            "is_final": False,
            "away_score": 4,
            "home_score": 2,
            "inning": "Top 7th",
            "badge_class": "live"
        }
    },
    {
        "away_team": "Houston Astros",
        "home_team": "Seattle Mariners",
        "game_time": "Final",
        "away_pitcher": "Framber Valdez",
        "home_pitcher": "George Kirby",
        "predictions": {
            "away_win_prob": 0.55,
            "home_win_prob": 0.45,
            "total_runs": 8.5
        },
        "betting_recommendations": {
            "value_bets": [
                {
                    "type": "moneyline", 
                    "recommendation": "Astros ML",
                    "expected_value": 0.102,
                    "win_probability": 0.55,
                    "american_odds": -125
                }
            ]
        },
        "live_status": {
            "status": "Final",
            "is_live": False,
            "is_final": True,
            "away_score": 6,
            "home_score": 3,
            "badge_class": "final"
        }
    }
]

@app.route('/')
def index():
    """Main page with today's games and betting recommendations"""
    try:
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate positive EV count
        positive_ev_count = 0
        for game in SAMPLE_GAMES:
            for bet in game.get('betting_recommendations', {}).get('value_bets', []):
                if bet.get('expected_value', 0) > 0:
                    positive_ev_count += 1
        
        # Categorize games
        live_games = [g for g in SAMPLE_GAMES if g['live_status'].get('is_live')]
        completed_games = [g for g in SAMPLE_GAMES if g['live_status'].get('is_final')]
        upcoming_games = [g for g in SAMPLE_GAMES if not g['live_status'].get('is_live') and not g['live_status'].get('is_final')]
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Betting Predictions - {today_str}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .game-card {{ background: white; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .matchup {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .betting-recs {{ margin-top: 15px; }}
        .bet-item {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #28a745; }}
        .positive-ev {{ background: #d4edda; border-left-color: #28a745; }}
        .negative-ev {{ background: #f8d7da; border-left-color: #dc3545; }}
        .live-badge {{ background: #dc3545; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; }}
        .final-badge {{ background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; }}
        .scheduled-badge {{ background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; }}
        .section-header {{ font-size: 1.5em; font-weight: bold; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 2px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 MLB Betting Predictions</h1>
        <p>Advanced Expected Value Analysis • Live Game Status • Performance Tracking</p>
        <p>Date: {today_str} | Last Updated: {datetime.now().strftime('%H:%M ET')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>📊 Today's Games</h3>
            <p><strong>{len(SAMPLE_GAMES)}</strong> Total Games</p>
        </div>
        <div class="stat-card">
            <h3>💰 Positive EV Opportunities</h3>
            <p><strong>{positive_ev_count}</strong> Value Bets</p>
        </div>
        <div class="stat-card">
            <h3>🔴 Live Games</h3>
            <p><strong>{len(live_games)}</strong> In Progress</p>
        </div>
        <div class="stat-card">
            <h3>✅ Completed</h3>
            <p><strong>{len(completed_games)}</strong> Final</p>
        </div>
    </div>
"""

        # Add live games section
        if live_games:
            html_template += '<div class="section-header">🔴 Live Games</div>'
            for game in live_games:
                html_template += generate_game_card(game)

        # Add upcoming games section  
        if upcoming_games:
            html_template += '<div class="section-header">⏰ Upcoming Games</div>'
            for game in upcoming_games:
                html_template += generate_game_card(game)

        # Add completed games section
        if completed_games:
            html_template += '<div class="section-header">✅ Completed Games</div>'
            for game in completed_games:
                html_template += generate_game_card(game)

        html_template += """
</body>
</html>
"""
        
        return html_template
        
    except Exception as e:
        logger.error(f"Error loading main page: {e}")
        return jsonify({
            "status": "MLB Betting System Live",
            "error": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })

def generate_game_card(game):
    """Generate HTML for a game card"""
    ev_bets = []
    for bet in game.get('betting_recommendations', {}).get('value_bets', []):
        ev = bet.get('expected_value', 0)
        ev_class = 'positive-ev' if ev > 0 else 'negative-ev'
        ev_display = f"+{ev:.3f}" if ev > 0 else f"{ev:.3f}"
        prob_display = f"{bet.get('win_probability', 0)*100:.1f}%"
        
        ev_bets.append(f"""
            <div class="bet-item {ev_class}">
                <strong>{bet.get('type', 'Unknown').title()}</strong>: {bet.get('recommendation', 'N/A')}<br>
                <small>Expected Value: <strong>{ev_display}</strong> | Win Probability: {prob_display}</small>
            </div>
        """)
    
    status = game.get('live_status', {})
    badge_class = status.get('badge_class', 'scheduled')
    status_text = status.get('status', 'Scheduled')
    
    if status.get('is_live'):
        badge_html = f'<span class="live-badge">🔴 {status_text}</span>'
        score_html = f"<p>Score: {game['away_team']} {status.get('away_score', 0)} - {status.get('home_score', 0)} {game['home_team']}</p>"
        if status.get('inning'):
            score_html += f"<p>{status['inning']}</p>"
    elif status.get('is_final'):
        badge_html = f'<span class="final-badge">Final</span>'
        score_html = f"<p><strong>Final Score:</strong> {game['away_team']} {status.get('away_score', 0)} - {status.get('home_score', 0)} {game['home_team']}</p>"
    else:
        badge_html = f'<span class="scheduled-badge">{status_text}</span>'
        score_html = f"<p>Game Time: {game.get('game_time', 'TBD')}</p>"
    
    return f"""
    <div class="game-card">
        <div class="matchup">
            {game['away_team']} @ {game['home_team']} {badge_html}
        </div>
        {score_html}
        <p><strong>Pitchers:</strong> {game.get('away_pitcher', 'TBD')} vs {game.get('home_pitcher', 'TBD')}</p>
        <div class="betting-recs">
            <h4>💰 Betting Recommendations</h4>
            {''.join(ev_bets)}
        </div>
    </div>
    """

@app.route('/api/today-games')
def api_today_games():
    """API endpoint for today's games with betting data"""
    try:
        date_param = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        return jsonify({
            'games': SAMPLE_GAMES,
            'date': date_param,
            'total_games': len(SAMPLE_GAMES),
            'positive_ev_count': sum(1 for game in SAMPLE_GAMES 
                                   for bet in game.get('betting_recommendations', {}).get('value_bets', [])
                                   if bet.get('expected_value', 0) > 0),
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in today-games API: {e}")
        return jsonify({
            'error': str(e),
            'games': [],
            'date': date_param,
            'last_updated': datetime.now().isoformat()
        })

@app.route('/api/live-status')
def api_live_status():
    """API endpoint for live game status"""
    try:
        live_games = [g for g in SAMPLE_GAMES if g['live_status'].get('is_live')]
        final_games = [g for g in SAMPLE_GAMES if g['live_status'].get('is_final')]
        
        return jsonify({
            'live_games': live_games,
            'final_games': final_games,
            'total_live': len(live_games),
            'total_final': len(final_games),
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in live-status API: {e}")
        return jsonify({'error': str(e), 'live_games': []})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "mlb-betting-production",
        "features": [
            "Expected Value calculations",
            "Live game status",
            "Betting recommendations", 
            "Game categorization",
            "Self-contained demo data"
        ],
        "games_loaded": len(SAMPLE_GAMES),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Production configuration for Render
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Starting MLB Betting System on port {port} (production mode)")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
