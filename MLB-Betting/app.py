# Simple import wrapper for Render deployment
# This ensures Render can find the app regardless of configuration
from render_app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
