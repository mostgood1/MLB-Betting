#!/usr/bin/env python3
"""
Complete MLB Prediction Web Application
Original user implementation recreated based on workspace structure
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Initialize prediction engine
prediction_engine = None

try:
    # Try to import prediction engine from the main directory structure
    sys.path.insert(0, r'c:\Users\mostg\OneDrive\Coding\MLBCompare\mlb-team-comparator')
    from ultra_fast_engine import FastPredictionEngine
    prediction_engine = FastPredictionEngine()
    print("✓ Prediction engine initialized successfully")
except ImportError as e:
    print(f"⚠ Could not import FastPredictionEngine: {e}")
    try:
        from mlb_team_comparator.src.ultra_fast_engine import FastPredictionEngine
        prediction_engine = FastPredictionEngine()
        print("✓ Prediction engine initialized from src directory")
    except ImportError as e2:
        print(f"⚠ Could not import from src directory either: {e2}")
        prediction_engine = None

# Try to import TodaysGames
try:
    sys.path.insert(0, r'c:\Users\mostg\OneDrive\Coding\MLBCompare\mlb-team-comparator\src')
    from TodaysGames import get_games_for_date
    print("✓ TodaysGames imported successfully")
except ImportError as e:
    print(f"⚠ Could not import TodaysGames: {e}")
    
    # Create a fallback function
    def get_games_for_date(date, include_live_scores=False):
        """Fallback function for getting games"""
        try:
            # Try to read from data directory
            data_dir = r'c:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting\data'
            games_file = os.path.join(data_dir, f'games_{date}.json')
            
            if os.path.exists(games_file):
                with open(games_file, 'r') as f:
                    return json.load(f)
            
            # Return empty list if no data found
            return []
            
        except Exception as e:
            print(f"⚠ Error in fallback get_games_for_date: {e}")
            return []

@app.route('/')
def index():
    """Main page with today's games"""
    try:
        today_date = datetime.now().strftime('%Y-%m-%d')
        games = get_games_for_date(today_date)
        
        # Get predictions for each game
        predictions = []
        if prediction_engine:
            for game in games:
                try:
                    pred = prediction_engine.get_fast_prediction(
                        game.get('away_team', ''),
                        game.get('home_team', '')
                    )
                    predictions.append({
                        'game': game,
                        'prediction': pred
                    })
                except Exception as e:
                    print(f"⚠ Error getting prediction for game: {e}")
                    predictions.append({
                        'game': game,
                        'prediction': None
                    })
        
        return render_template('index.html', 
                             predictions=predictions, 
                             today_date=today_date)
                             
    except Exception as e:
        print(f"❌ Error in index route: {e}")
        traceback.print_exc()
        return f"Error loading page: {str(e)}", 500

@app.route('/api/predictions/<date>')
def get_predictions_for_date(date):
    """API endpoint to get predictions for a specific date"""
    try:
        games = get_games_for_date(date)
        predictions = []
        
        if prediction_engine:
            for game in games:
                try:
                    pred = prediction_engine.get_fast_prediction(
                        game.get('away_team', ''),
                        game.get('home_team', '')
                    )
                    predictions.append({
                        'game': game,
                        'prediction': pred
                    })
                except Exception as e:
                    predictions.append({
                        'game': game,
                        'prediction': None,
                        'error': str(e)
                    })
        
        return jsonify({
            'date': date,
            'predictions': predictions,
            'total_games': len(games)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction')
def get_single_prediction():
    """API endpoint for single game prediction"""
    try:
        away_team = request.args.get('away_team')
        home_team = request.args.get('home_team')
        
        if not away_team or not home_team:
            return jsonify({'error': 'Missing away_team or home_team parameter'}), 400
        
        if not prediction_engine:
            return jsonify({'error': 'Prediction engine not available'}), 503
        
        prediction = prediction_engine.get_fast_prediction(away_team, home_team)
        
        return jsonify({
            'away_team': away_team,
            'home_team': home_team,
            'prediction': prediction
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'prediction_engine_available': prediction_engine is not None,
        'timestamp': datetime.now().isoformat()
    })

# Create basic templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Create basic index.html template if it doesn't exist
index_template_path = os.path.join(templates_dir, 'index.html')
if not os.path.exists(index_template_path):
    index_template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Prediction System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .game { border: 1px solid #ccc; margin: 10px 0; padding: 15px; }
        .prediction { background: #f0f8ff; padding: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>MLB Prediction System</h1>
    <h2>Games for {{ today_date }}</h2>
    
    {% if predictions %}
        {% for pred in predictions %}
        <div class="game">
            <h3>{{ pred.game.away_team }} @ {{ pred.game.home_team }}</h3>
            <p><strong>Status:</strong> {{ pred.game.status }}</p>
            {% if pred.game.game_time %}
                <p><strong>Game Time:</strong> {{ pred.game.game_time }}</p>
            {% endif %}
            
            {% if pred.prediction %}
            <div class="prediction">
                <h4>Prediction:</h4>
                <pre>{{ pred.prediction | tojson(indent=2) }}</pre>
            </div>
            {% else %}
                <p><em>No prediction available</em></p>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <p>No games found for today.</p>
    {% endif %}
</body>
</html>'''
    
    with open(index_template_path, 'w') as f:
        f.write(index_template_content)
    print(f"✓ Created basic index.html template at {index_template_path}")

if __name__ == '__main__':
    print("🚀 Starting Complete MLB Prediction Web App")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🧠 Prediction engine available: {prediction_engine is not None}")
    
    # Start the Flask app
    app.run(host='127.0.0.1', port=5000, debug=True)
