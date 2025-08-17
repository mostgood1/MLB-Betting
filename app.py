from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "MLB Betting System - Debug Mode",
        "message": "Simple Flask app working correctly",
        "timestamp": datetime.now().isoformat(),
        "port": os.environ.get('PORT', 'Not set'),
        "env": os.environ.get('FLASK_ENV', 'Not set')
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
