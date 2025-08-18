from flask import Flask, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Ultra minimal test page"""
    try:
        # Try to load any betting file
        games_count = 0
        if os.path.exists('data/betting_recommendations_2025_08_16.json'):
            with open('data/betting_recommendations_2025_08_16.json', 'r') as f:
                data = json.load(f)
                if 'games' in data:
                    games_count = len(data['games'])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>MLB Test Deploy</title></head>
        <body>
            <h1>MLB Deployment Test - WORKING v3.0</h1>
            <p>Timestamp: {datetime.now().isoformat()}</p>
            <p>Games found: {games_count}</p>
            <p>Data directory exists: {os.path.exists('data')}</p>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {e}"

@app.route('/test')
def test():
    return jsonify({
        "status": "DEPLOYMENT WORKING v3.0",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
