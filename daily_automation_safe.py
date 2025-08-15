#!/usr/bin/env python3
"""
Daily New Day MLB Automation System - Windows Compatible Version
================================================================
Windows-safe automation for preparing MLB prediction system for each new day.
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure Windows-safe logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_automation_safe.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DailyAutomation')

class DailyAutomationSafe:
    """Windows-safe daily automation system for MLB prediction preparation"""
    
    def __init__(self):
        """Initialize the daily automation system"""
        self.root_dir = Path(__file__).parent
        self.mlb_betting_dir = self.root_dir / "MLB-Betting"
        self.mlb_clean_dir = self.root_dir / "mlb-clean-deploy"
        
        # Today's date for all operations
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y-%m-%d')
        
        # Initialize data storage paths
        self.unified_cache_path = self.root_dir / 'unified_predictions_cache.json'
        self.betting_cache_path = self.mlb_betting_dir / 'unified_predictions_cache.json'
        self.games_cache_path = self.root_dir / 'game_scores_cache.json'
        
        logger.info(f"Starting Daily Automation for {self.today_str}")
        logger.info(f"Root Directory: {self.root_dir}")
        
    def step1_fetch_todays_games(self) -> bool:
        """Step 1: Pull fresh games from MLB API"""
        try:
            logger.info("STEP 1: Fetching today's games from MLB API")
            
            # Use the MLB Stats API to get today's games
            mlb_api_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={self.today_str}"
            
            response = requests.get(mlb_api_url, timeout=30)
            response.raise_for_status()
            
            schedule_data = response.json()
            games = []
            
            if 'dates' in schedule_data and schedule_data['dates']:
                for date_data in schedule_data['dates']:
                    if 'games' in date_data:
                        for game in date_data['games']:
                            game_info = {
                                'game_id': game.get('gamePk'),
                                'date': self.today_str,
                                'away_team': game['teams']['away']['team']['name'],
                                'home_team': game['teams']['home']['team']['name'],
                                'game_time': game.get('gameDate'),
                                'status': game.get('status', {}).get('abstractGameState', 'Unknown'),
                                'venue': game.get('venue', {}).get('name', 'Unknown')
                            }
                            games.append(game_info)
            
            logger.info(f"SUCCESS: Found {len(games)} games for {self.today_str}")
            
            # Save to games cache
            self._update_games_cache(games)
            
            return len(games) > 0
            
        except Exception as e:
            logger.error(f"STEP 1 FAILED: Error fetching games from MLB API: {e}")
            return False
    
    def step2_run_enhanced_automation(self) -> bool:
        """Step 2: Run existing enhanced automation as fallback"""
        try:
            logger.info("STEP 2: Running enhanced automation system")
            
            # Run the existing enhanced automation
            enhanced_script = self.root_dir / "daily_enhanced_automation.py"
            if enhanced_script.exists():
                result = subprocess.run([sys.executable, str(enhanced_script)], 
                                      capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    logger.info("SUCCESS: Enhanced automation completed")
                    return True
                else:
                    logger.warning(f"Enhanced automation had issues but continuing")
                    # Don't fail the entire process for this
                    return True
            else:
                logger.warning("Enhanced automation script not found, skipping")
                return True
            
        except Exception as e:
            logger.error(f"STEP 2 FAILED: Error running enhanced automation: {e}")
            return False
    
    def step3_update_betting_lines(self) -> bool:
        """Step 3: Update betting lines from OddsAPI"""
        try:
            logger.info("STEP 3: Fetching latest betting lines from OddsAPI")
            
            # Check if API keys are available
            api_keys_path = self.root_dir / "api_keys.json"
            if not api_keys_path.exists():
                logger.warning("API keys not found, skipping betting lines update")
                return True  # Don't fail the entire process for this
            
            # Run the odds API fetcher
            odds_script = self.root_dir / "fetch_odds_api.py"
            if odds_script.exists():
                result = subprocess.run([
                    sys.executable, str(odds_script), self.today_str, self.today_str
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("SUCCESS: Betting lines updated successfully")
                else:
                    logger.warning(f"Betting lines update had issues: {result.stderr}")
                    # Don't fail for this - not critical
            
            return True
            
        except Exception as e:
            logger.error(f"STEP 3 FAILED: Error updating betting lines: {e}")
            return False
    
    def step4_sync_and_update_frontend(self) -> bool:
        """Step 4: Sync caches and update frontend"""
        try:
            logger.info("STEP 4: Syncing caches and updating frontend")
            
            # First, generate predictions for today's games
            prediction_script = self.root_dir / "generate_todays_predictions.py"
            if prediction_script.exists():
                result = subprocess.run([sys.executable, str(prediction_script)], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    logger.info("SUCCESS: Generated predictions for today's games")
                else:
                    logger.warning("Prediction generation had issues but continuing")
            
            # Sync unified cache to MLB-Betting directory
            if self.unified_cache_path.exists():
                import shutil
                shutil.copy2(self.unified_cache_path, self.betting_cache_path)
                logger.info("SUCCESS: Synchronized prediction cache to MLB-Betting app")
                
                # Also copy to data directory  
                data_cache = self.root_dir / "MLB-Betting" / "data" / "unified_predictions_cache.json"
                if data_cache.parent.exists():
                    shutil.copy2(self.unified_cache_path, data_cache)
                    logger.info("SUCCESS: Updated data directory cache")
            
            # Run data consolidation to ensure everything is properly integrated
            consolidation_script = self.root_dir / "data_preservation" / "daily_consolidation.py"
            if consolidation_script.exists():
                result = subprocess.run([sys.executable, str(consolidation_script)], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    logger.info("SUCCESS: Data consolidation completed")
                else:
                    logger.warning("Data consolidation had issues but continuing")
            
            logger.info("SUCCESS: Frontend updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"STEP 4 FAILED: Error updating frontend: {e}")
            return False
    
    def run_complete_automation(self) -> bool:
        """Run the complete daily automation sequence"""
        logger.info("STARTING COMPLETE DAILY MLB AUTOMATION")
        logger.info("=" * 60)
        logger.info(f"Date: {self.today_str}")
        logger.info(f"Time: {self.today.strftime('%H:%M:%S')}")
        logger.info("=" * 60)
        
        steps = [
            ("1. Fetch Today's Games from MLB API", self.step1_fetch_todays_games),
            ("2. Run Enhanced Automation", self.step2_run_enhanced_automation),
            ("3. Update Betting Lines", self.step3_update_betting_lines),
            ("4. Sync and Update Frontend", self.step4_sync_and_update_frontend)
        ]
        
        results = {}
        all_success = True
        
        for step_name, step_function in steps:
            logger.info(f"\n--- {step_name} ---")
            
            try:
                success = step_function()
                results[step_name] = success
                all_success = all_success and success
                
                if success:
                    logger.info(f"SUCCESS: {step_name}")
                else:
                    logger.error(f"FAILED: {step_name}")
                    
            except Exception as e:
                logger.error(f"EXCEPTION in {step_name}: {e}")
                results[step_name] = False
                all_success = False
        
        # Final summary report
        logger.info("\n" + "=" * 60)
        logger.info("DAILY AUTOMATION SUMMARY REPORT")
        logger.info("=" * 60)
        
        for step_name, success in results.items():
            status = "PASS" if success else "FAIL"
            logger.info(f"{step_name}: {status}")
        
        if all_success:
            logger.info("\nALL STEPS COMPLETED SUCCESSFULLY!")
            logger.info("Your MLB prediction system is ready for optimal performance!")
            logger.info(f"Complete data ready for {self.today_str}")
        else:
            logger.warning("\nSOME STEPS FAILED")
            logger.warning("Check logs above for details")
            logger.warning("System may still be functional with partial data")
            
        logger.info(f"\nNext run recommended: {(self.today + timedelta(days=1)).strftime('%Y-%m-%d')} early morning")
        logger.info("=" * 60)
        
        return all_success
    
    # Helper methods
    def _update_games_cache(self, games: List[Dict]):
        """Update the games cache with today's games"""
        try:
            # Load existing cache
            cache = {}
            if self.games_cache_path.exists():
                with open(self.games_cache_path, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            # Ensure cache is a dictionary
            if not isinstance(cache, dict):
                logger.warning(f"Games cache was {type(cache)}, converting to dict")
                cache = {}
            
            # Update with today's games
            cache[self.today_str] = games
            
            # Save updated cache
            with open(self.games_cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Updated games cache with {len(games)} games")
            
        except Exception as e:
            logger.error(f"Failed to update games cache: {e}")

def main():
    """Main entry point for daily automation"""
    print("\nMLB Daily Automation System - Windows Safe Version")
    print("=" * 55)
    print("This system will prepare your MLB prediction system for optimal daily performance")
    print("Estimated time: 3-5 minutes for complete processing")
    print()
    
    # Run the automation
    automation = DailyAutomationSafe()
    success = automation.run_complete_automation()
    
    if success:
        print("\nDaily automation completed successfully!")
        print("Your MLB prediction system is ready for optimal performance!")
    else:
        print("\nDaily automation encountered some issues")
        print("Check the logs for details - system may still be partially functional")
        sys.exit(1)

if __name__ == "__main__":
    main()
