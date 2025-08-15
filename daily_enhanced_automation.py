#!/usr/bin/env python3
"""
Daily Enhanced MLB Data Automation

This script ensures your MLB prediction system has the most accurate data daily.
It integrates enhanced pitcher data fetching into your daily refresh routine.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_enhanced_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DailyEnhancedAutomation')

class DailyMLBAutomation:
    def __init__(self):
        """Initialize the daily automation system"""
        self.root_dir = Path(__file__).parent
        self.enhanced_dir = self.root_dir / "mlb-clean-deploy"
        self.mlb_betting_dir = self.root_dir / "MLB-Betting"
        
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Starting daily MLB automation for {self.today}")
        
    def run_script(self, script_path: Path, description: str, change_dir: Path = None) -> bool:
        """Run a Python script with error handling"""
        try:
            logger.info(f"📊 {description}")
            
            if change_dir:
                original_cwd = os.getcwd()
                os.chdir(change_dir)
                
            result = subprocess.run([sys.executable, str(script_path)], 
                                  capture_output=True, text=True, timeout=300)
            
            if change_dir:
                os.chdir(original_cwd)
                
            if result.returncode == 0:
                logger.info(f"✅ {description} - SUCCESS")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ {description} - FAILED")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {description} - TIMEOUT")
            return False
        except Exception as e:
            logger.error(f"💥 {description} - EXCEPTION: {e}")
            return False
    
    def fetch_standard_games(self) -> bool:
        """Fetch today's games using the standard fetcher"""
        script_path = self.root_dir / "fetch_today_games.py"
        return self.run_script(script_path, "Fetching standard today's games")
    
    def fetch_enhanced_data(self) -> bool:
        """Fetch enhanced game data with real pitcher information"""
        script_path = self.enhanced_dir / "update_todays_data.py"
        return self.run_script(script_path, "Fetching enhanced pitcher data", self.enhanced_dir)
    
    def validate_enhanced_integration(self) -> bool:
        """Validate that enhanced data integration is working"""
        script_path = self.enhanced_dir / "test_direct_integration.py"
        return self.run_script(script_path, "Validating enhanced data integration", self.enhanced_dir)
    
    def fetch_betting_lines(self) -> bool:
        """Fetch betting lines from OddsAPI"""
        script_path = self.root_dir / "fetch_odds_api.py"
        # Run with today's date parameters
        try:
            logger.info("💰 Fetching betting lines from OddsAPI")
            result = subprocess.run([sys.executable, str(script_path), self.today, self.today], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Betting lines fetch - SUCCESS")
                return True
            else:
                logger.error(f"❌ Betting lines fetch - FAILED: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"💥 Betting lines fetch - EXCEPTION: {e}")
            return False
    
    def run_daily_automation(self) -> bool:
        """Run the complete daily automation sequence"""
        logger.info("🎯 Starting Enhanced Daily MLB Data Automation")
        logger.info("=" * 60)
        
        steps = [
            ("Standard Games", self.fetch_standard_games),
            ("Enhanced Pitcher Data", self.fetch_enhanced_data),
            ("Enhanced Integration Validation", self.validate_enhanced_integration),
            ("Betting Lines", self.fetch_betting_lines)
        ]
        
        results = {}
        all_success = True
        
        for step_name, step_function in steps:
            logger.info(f"\n🔄 Step: {step_name}")
            success = step_function()
            results[step_name] = success
            all_success = all_success and success
            
        # Summary report
        logger.info("\n" + "=" * 60)
        logger.info("📈 DAILY AUTOMATION SUMMARY")
        logger.info("=" * 60)
        
        for step_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{step_name}: {status}")
        
        if all_success:
            logger.info("\n🏆 ALL STEPS COMPLETED SUCCESSFULLY!")
            logger.info("🎯 Your MLB prediction system is ready for optimal performance!")
            logger.info(f"📊 Enhanced pitcher data available for {self.today}")
        else:
            logger.warning("\n⚠️  SOME STEPS FAILED - Check logs for details")
            
        return all_success

def main():
    """Main entry point"""
    automation = DailyMLBAutomation()
    success = automation.run_daily_automation()
    
    if success:
        print("\n🎯 Daily automation completed successfully!")
        print("Your MLB prediction system is ready with enhanced accuracy!")
    else:
        print("\n⚠️  Daily automation encountered issues - check logs")
        sys.exit(1)

if __name__ == "__main__":
    main()
