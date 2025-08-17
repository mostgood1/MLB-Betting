"""
MLB Betting Predictions System - Streamlined Production Version
Optimized for Render deployment with all betting features
"""

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# Sample betting data optimized for Render
GAMES_DATA = {
    "2025-08-17": [
        {
            "id": "nyy_bos_001",
            "away_team": "New York Yankees",
            "home_team": "Boston Red Sox", 
            "game_time": "7:10 PM ET",
            "status": "scheduled",
            "predictions": {"away_win_prob": 0.58, "total_runs": 9.2},
            "betting": {
                "moneyline": {"recommendation": "Yankees ML", "ev": 0.125, "prob": 0.58, "odds": -140},
                "total": {"recommendation": "Over 8.5", "ev": 0.089, "prob": 0.52, "odds": -110}
            }
        },
        {
            "id": "lad_sf_001",
            "away_team": "Los Angeles Dodgers", 
            "home_team": "San Francisco Giants",
            "game_time": "10:15 PM ET",
            "status": "live",
            "score": {"away": 4, "home": 2, "inning": "Top 7th"},
            "predictions": {"away_win_prob": 0.62, "total_runs": 8.8},
            "betting": {
                "moneyline": {"recommendation": "Dodgers ML", "ev": 0.156, "prob": 0.62, "odds": -160},
                "runline": {"recommendation": "Dodgers -1.5", "ev": 0.073, "prob": 0.45, "odds": 125}
            }
        },
        {
            "id": "hou_sea_001",
            "away_team": "Houston Astros",
            "home_team": "Seattle Mariners",
            "game_time": "Final",
            "status": "final", 
            "score": {"away": 6, "home": 3},
            "predictions": {"away_win_prob": 0.55, "total_runs": 8.5},
            "betting": {
                "moneyline": {"recommendation": "Astros ML", "ev": 0.102, "prob": 0.55, "odds": -125}
            }
        }
    ]
}

@app.route('/')
def index():
    """Main betting dashboard - lightweight HTML"""
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        games = GAMES_DATA.get(date, [])
        
        # Count positive EV opportunities
        positive_ev = sum(1 for game in games 
                         for bet_type, bet_data in game.get('betting', {}).items()
                         if bet_data.get('ev', 0) > 0)
        
        # Categorize games
        live_count = len([g for g in games if g.get('status') == 'live'])
        final_count = len([g for g in games if g.get('status') == 'final'])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MLB Betting Predictions</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; border-radius: 10px; }}
        .stats {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 120px; }}
        .game {{ background: white; margin: 15px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .matchup {{ font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }}
        .betting {{ margin-top: 15px; }}
        .bet {{ background: #f8f9fa; padding: 10px; margin: 8px 0; border-radius: 5px; }}
        .positive {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .negative {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .badge {{ padding: 4px 8px; border-radius: 12px; color: white; font-size: 0.8em; }}
        .live {{ background: #dc3545; }}
        .final {{ background: #6c757d; }}
        .scheduled {{ background: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 MLB Betting Predictions</h1>
        <p>Expected Value Analysis • Live Status • Performance Tracking</p>
        <p>{date} | Updated: {datetime.now().strftime('%H:%M ET')}</p>
    </div>
    
    <div class="stats">
        <div class="stat"><strong>{len(games)}</strong><br>Total Games</div>
        <div class="stat"><strong>{positive_ev}</strong><br>+EV Bets</div>
        <div class="stat"><strong>{live_count}</strong><br>Live Games</div>
        <div class="stat"><strong>{final_count}</strong><br>Completed</div>
    </div>
"""

        # Generate game cards
        for game in games:
            status_class = game.get('status', 'scheduled')
            badge_text = {
                'live': f"🔴 Live",
                'final': 'Final', 
                'scheduled': 'Scheduled'
            }.get(status_class, 'Scheduled')
            
            score_html = ""
            if game.get('score'):
                if status_class == 'live':
                    score_html = f"<p>Score: {game['away_team']} {game['score']['away']} - {game['score']['home']} {game['home_team']}</p><p>{game['score'].get('inning', '')}</p>"
                elif status_class == 'final':
                    score_html = f"<p><strong>Final:</strong> {game['away_team']} {game['score']['away']} - {game['score']['home']} {game['home_team']}</p>"
            else:
                score_html = f"<p>Game Time: {game.get('game_time', 'TBD')}</p>"
            
            betting_html = ""
            for bet_type, bet_data in game.get('betting', {}).items():
                ev = bet_data.get('ev', 0)
                ev_class = 'positive' if ev > 0 else 'negative'
                ev_text = f"+{ev:.3f}" if ev > 0 else f"{ev:.3f}"
                prob_text = f"{bet_data.get('prob', 0)*100:.1f}%"
                
                betting_html += f"""
                <div class="bet {ev_class}">
                    <strong>{bet_type.title()}</strong>: {bet_data.get('recommendation', 'N/A')}<br>
                    <small>EV: <strong>{ev_text}</strong> | Win Prob: {prob_text}</small>
                </div>
                """
            
            html += f"""
            <div class="game">
                <div class="matchup">
                    {game['away_team']} @ {game['home_team']} 
                    <span class="badge {status_class}">{badge_text}</span>
                </div>
                {score_html}
                <div class="betting">
                    <h4>💰 Betting Recommendations</h4>
                    {betting_html}
                </div>
            </div>
            """
        
        html += "</body></html>"
        return html
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"})

@app.route('/api/games')
def api_games():
    """API endpoint for games data"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        games = GAMES_DATA.get(date, [])
        
        return jsonify({
            'games': games,
            'date': date,
            'total_games': len(games),
            'positive_ev_count': sum(1 for game in games 
                                   for bet_type, bet_data in game.get('betting', {}).items()
                                   if bet_data.get('ev', 0) > 0),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/live')
def api_live():
    """Live games API"""
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        games = GAMES_DATA.get(date, [])
        live_games = [g for g in games if g.get('status') == 'live']
        
        return jsonify({
            'live_games': live_games,
            'count': len(live_games),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "mlb-betting-production",
        "features": ["Expected Value", "Live Status", "Betting Recommendations"],
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
