# Minimal Flask app for Render deployment testing
from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "MLB Betting System Live",
        "timestamp": datetime.now().isoformat(),
        "message": "Deployment successful! Full features loading..."
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "mlb-betting"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
