#!/usr/bin/env python3
"""
Auto TBD Monitor and Refresh System
===================================

Automatically monitors for TBD pitcher updates and refreshes:
- Starting pitcher assignments
- Predictions
- Betting recommendations
"""

import json
import logging
import time
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Set

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoTBDMonitor:
    def __init__(self):
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.check_interval = 900  # 15 minutes
        self.last_pitcher_state = {}
        
    def get_current_tbd_games(self) -> Set[str]:
        """Get list of games that currently have TBD pitchers"""
        try:
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                data = json.load(f)
            
            today_data = data.get('predictions_by_date', {}).get(self.current_date, {})
            if 'games' not in today_data:
                return set()
            
            tbd_games = set()
            for game_key, game_data in today_data['games'].items():
                away_pitcher = game_data.get('away_pitcher', 'TBD')
                home_pitcher = game_data.get('home_pitcher', 'TBD')
                
                if away_pitcher == 'TBD' or home_pitcher == 'TBD':
                    tbd_games.add(game_key)
            
            return tbd_games
            
        except Exception as e:
            logger.error(f"Error getting TBD games: {e}")
            return set()
    
    def save_pitcher_state(self) -> Dict:
        """Save current pitcher state for comparison"""
        try:
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                data = json.load(f)
            
            today_data = data.get('predictions_by_date', {}).get(self.current_date, {})
            if 'games' not in today_data:
                return {}
            
            pitcher_state = {}
            for game_key, game_data in today_data['games'].items():
                pitcher_state[game_key] = {
                    'away_pitcher': game_data.get('away_pitcher', 'TBD'),
                    'home_pitcher': game_data.get('home_pitcher', 'TBD')
                }
            
            return pitcher_state
            
        except Exception as e:
            logger.error(f"Error saving pitcher state: {e}")
            return {}
    
    def check_for_pitcher_updates(self) -> bool:
        """Check if any pitchers have been updated from TBD"""
        logger.info("🔍 Checking for pitcher updates...")
        
        # Run the pitcher fetch script
        try:
            result = subprocess.run([
                'python', 'fetch_todays_starters.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                logger.error(f"Error fetching pitchers: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running pitcher fetch: {e}")
            return False
        
        # Check if anything changed
        new_pitcher_state = self.save_pitcher_state()
        
        if not self.last_pitcher_state:
            self.last_pitcher_state = new_pitcher_state
            return False
        
        changes_detected = False
        for game_key in new_pitcher_state:
            old_state = self.last_pitcher_state.get(game_key, {})
            new_state = new_pitcher_state[game_key]
            
            old_away = old_state.get('away_pitcher', 'TBD')
            old_home = old_state.get('home_pitcher', 'TBD')
            new_away = new_state['away_pitcher']
            new_home = new_state['home_pitcher']
            
            if (old_away == 'TBD' and new_away != 'TBD') or (old_home == 'TBD' and new_home != 'TBD'):
                logger.info(f"✅ Pitcher update detected for {game_key}:")
                if old_away != new_away:
                    logger.info(f"  Away: {old_away} → {new_away}")
                if old_home != new_home:
                    logger.info(f"  Home: {old_home} → {new_home}")
                changes_detected = True
        
        self.last_pitcher_state = new_pitcher_state
        return changes_detected
    
    def refresh_predictions_and_betting(self) -> bool:
        """Refresh predictions and betting recommendations"""
        logger.info("🔄 Refreshing predictions and betting recommendations...")
        
        try:
            # Step 1: Regenerate predictions
            logger.info("📊 Regenerating predictions...")
            result = subprocess.run([
                'python', 'generate_todays_predictions.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                logger.error(f"Error regenerating predictions: {result.stderr}")
                return False
            
            # Step 2: Generate new betting recommendations
            logger.info("🎯 Generating new betting recommendations...")
            result = subprocess.run([
                'python', 'betting_recommendations_engine.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                logger.error(f"Error generating betting recommendations: {result.stderr}")
                return False
            
            logger.info("✅ Predictions and betting recommendations refreshed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during refresh: {e}")
            return False
    
    def run_monitoring_cycle(self) -> None:
        """Run one monitoring cycle"""
        tbd_games = self.get_current_tbd_games()
        
        if not tbd_games:
            logger.info("✅ No TBD pitchers remaining - monitoring complete for today")
            return
        
        logger.info(f"🔍 Monitoring {len(tbd_games)} games with TBD pitchers:")
        for game in tbd_games:
            logger.info(f"  - {game}")
        
        # Check for updates
        if self.check_for_pitcher_updates():
            logger.info("🔄 Pitcher updates detected - refreshing system...")
            if self.refresh_predictions_and_betting():
                logger.info("✅ System refresh completed successfully!")
                
                # Log the update
                update_log = {
                    'timestamp': datetime.now().isoformat(),
                    'date': self.current_date,
                    'action': 'auto_refresh',
                    'reason': 'pitcher_updates_detected',
                    'remaining_tbds': len(self.get_current_tbd_games())
                }
                
                # Save update log
                log_file = f'data/auto_tbd_updates_{self.current_date.replace("-", "_")}.json'
                
                try:
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            logs = json.load(f)
                    else:
                        logs = []
                    
                    logs.append(update_log)
                    
                    with open(log_file, 'w') as f:
                        json.dump(logs, f, indent=2)
                        
                except Exception as e:
                    logger.error(f"Error saving update log: {e}")
            else:
                logger.error("❌ System refresh failed!")
        else:
            logger.info("ℹ️ No pitcher updates detected")
    
    def start_monitoring(self, max_cycles: int = 48) -> None:
        """Start the monitoring loop"""
        logger.info(f"🎯 Starting Auto TBD Monitor for {self.current_date}")
        logger.info(f"⏱️ Check interval: {self.check_interval/60:.1f} minutes")
        logger.info(f"🔄 Max cycles: {max_cycles}")
        
        # Initialize pitcher state
        self.last_pitcher_state = self.save_pitcher_state()
        
        cycle_count = 0
        while cycle_count < max_cycles:
            cycle_count += 1
            
            logger.info(f"🔄 Monitoring cycle {cycle_count}/{max_cycles}")
            
            try:
                self.run_monitoring_cycle()
                
                # Check if we're done
                remaining_tbds = self.get_current_tbd_games()
                if not remaining_tbds:
                    logger.info("✅ All TBDs resolved - monitoring complete!")
                    break
                
                # Wait for next cycle
                if cycle_count < max_cycles:
                    logger.info(f"⏱️ Waiting {self.check_interval/60:.1f} minutes for next check...")
                    time.sleep(self.check_interval)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("🏁 Auto TBD monitoring session ended")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto TBD Monitor')
    parser.add_argument('--cycles', type=int, default=48, help='Maximum monitoring cycles')
    parser.add_argument('--interval', type=int, default=900, help='Check interval in seconds')
    args = parser.parse_args()
    
    monitor = AutoTBDMonitor()
    monitor.check_interval = args.interval
    
    logger.info("🎯 Auto TBD Monitor Starting")
    monitor.start_monitoring(max_cycles=args.cycles)

if __name__ == "__main__":
    main()
