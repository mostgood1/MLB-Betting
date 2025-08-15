#!/usr/bin/env python3
"""
Daily Dashboard Update Automation
================================

Script to automatically update dashboard statistics daily.
Can be scheduled with Windows Task Scheduler or run manually.
"""

import json
import requests
import sys
from datetime import datetime
import logging

# Set up logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_dashboard_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def update_dashboard_stats():
    """Update dashboard statistics via API call"""
    
    try:
        # API endpoint for dashboard update
        api_url = "http://127.0.0.1:5000/api/update-dashboard-stats"
        
        logging.info("🔄 Starting daily dashboard statistics update...")
        
        # Make API call to update dashboard stats
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('status') == 'success':
                stats = result.get('stats', {})
                
                logging.info("✅ Dashboard statistics updated successfully!")
                logging.info(f"📊 Total Games Analyzed: {stats.get('total_games_analyzed', 0)}")
                logging.info(f"📅 Date Range: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}")
                logging.info(f"🎯 Total Winner Predictions: {stats.get('betting_performance', {}).get('total_winner_predictions', 0)} ({stats.get('betting_performance', {}).get('winner_accuracy_pct', 0)}% accurate)")
                logging.info(f"📈 Total Total Predictions: {stats.get('betting_performance', {}).get('total_total_predictions', 0)} ({stats.get('betting_performance', {}).get('total_accuracy_pct', 0)}% accurate)")
                logging.info(f"⭐ Perfect Games: {stats.get('betting_performance', {}).get('perfect_games', 0)} ({stats.get('betting_performance', {}).get('perfect_games_pct', 0)}%)")
                
                # Save update log
                update_log = {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'stats_summary': {
                        'total_games': stats.get('total_games_analyzed', 0),
                        'premium_predictions': stats.get('prediction_quality', {}).get('premium_predictions', 0),
                        'date_range': stats.get('date_range', {}),
                        'data_sources': stats.get('data_sources', {})
                    }
                }
                
                with open('daily_dashboard_update_log.json', 'w') as f:
                    json.dump(update_log, f, indent=2)
                
                return True
                
            else:
                logging.error(f"❌ API returned error: {result.get('message', 'Unknown error')}")
                return False
                
        else:
            logging.error(f"❌ API call failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logging.error("❌ Could not connect to Flask application. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        logging.error(f"❌ Error updating dashboard stats: {e}")
        return False

def check_flask_status():
    """Check if Flask application is running"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/stats", timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """Main execution function"""
    logging.info("🚀 Daily Dashboard Update Automation Starting")
    logging.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if Flask app is running
    if not check_flask_status():
        logging.error("❌ Flask application is not running. Please start the Flask app first.")
        sys.exit(1)
    
    # Update dashboard statistics
    success = update_dashboard_stats()
    
    if success:
        logging.info("🎉 Daily dashboard update completed successfully!")
        sys.exit(0)
    else:
        logging.error("💥 Daily dashboard update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
