#!/usr/bin/env python3
"""
Complete Daily MLB Automation System
===================================

Comprehensive daily workflow:
1. Fetch starting pitchers
2. Generate predictions  
3. Create betting recommendations
4. Start TBD monitoring
5. Update dashboard
"""

import json
import logging
import subprocess
import os
import sys
from datetime import datetime
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DailyMLBAutomation:
    def __init__(self):
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.workflow_log = []
        
    def log_step(self, step: str, status: str, details: str = ""):
        """Log a workflow step"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'status': status,
            'details': details
        }
        self.workflow_log.append(entry)
        
        status_emoji = "✅" if status == "SUCCESS" else "❌" if status == "ERROR" else "🔄"
        logger.info(f"{status_emoji} {step}: {status} {details}")
    
    def run_script(self, script_name: str, description: str) -> bool:
        """Run a Python script and log results"""
        logger.info(f"🔄 {description}...")
        
        try:
            result = subprocess.run([
                'python', script_name
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                self.log_step(description, "SUCCESS", f"Script: {script_name}")
                return True
            else:
                self.log_step(description, "ERROR", f"Script: {script_name} - {result.stderr[:200]}")
                return False
                
        except Exception as e:
            self.log_step(description, "ERROR", f"Exception: {str(e)[:200]}")
            return False
    
    def step_1_fetch_pitchers(self) -> bool:
        """Step 1: Fetch starting pitchers"""
        return self.run_script('fetch_todays_starters.py', 'Fetch Starting Pitchers')
    
    def step_2_generate_predictions(self) -> bool:
        """Step 2: Generate predictions"""
        return self.run_script('generate_todays_predictions.py', 'Generate Predictions')
    
    def step_3_betting_recommendations(self) -> bool:
        """Step 3: Generate betting recommendations"""
        return self.run_script('betting_recommendations_engine.py', 'Generate Betting Recommendations')
    
    def step_4_update_historical_accuracy(self) -> bool:
        """Step 4: Update historical betting accuracy"""
        return self.run_script('fix_complete_betting_accuracy.py', 'Update Historical Accuracy')
    
    def step_5_check_tbd_status(self) -> Dict:
        """Step 5: Check for remaining TBDs"""
        try:
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                data = json.load(f)
            
            today_data = data.get('predictions_by_date', {}).get(self.current_date, {})
            if 'games' not in today_data:
                return {'tbd_count': 0, 'games': []}
            
            tbd_games = []
            for game_key, game_data in today_data['games'].items():
                away_pitcher = game_data.get('away_pitcher', 'TBD')
                home_pitcher = game_data.get('home_pitcher', 'TBD')
                
                if away_pitcher == 'TBD' or home_pitcher == 'TBD':
                    tbd_games.append({
                        'game': game_key,
                        'away_pitcher': away_pitcher,
                        'home_pitcher': home_pitcher
                    })
            
            tbd_status = {
                'tbd_count': len(tbd_games),
                'games': tbd_games
            }
            
            if tbd_games:
                self.log_step('Check TBD Status', 'PENDING', f"{len(tbd_games)} games with TBD pitchers")
            else:
                self.log_step('Check TBD Status', 'SUCCESS', 'All pitchers confirmed')
            
            return tbd_status
            
        except Exception as e:
            self.log_step('Check TBD Status', 'ERROR', str(e))
            return {'tbd_count': 0, 'games': []}
    
    def generate_daily_report(self) -> Dict:
        """Generate comprehensive daily report"""
        
        report = {
            'date': self.current_date,
            'generated_at': datetime.now().isoformat(),
            'workflow_log': self.workflow_log,
            'status': 'COMPLETE',
            'summary': {}
        }
        
        try:
            # Load betting recommendations
            rec_file = f'data/betting_recommendations_{self.current_date.replace("-", "_")}.json'
            if os.path.exists(rec_file):
                with open(rec_file, 'r') as f:
                    betting_data = json.load(f)
                
                report['betting_summary'] = betting_data.get('summary', {})
            
            # Load accuracy data
            acc_file = 'data/betting_accuracy_analysis.json'
            if os.path.exists(acc_file):
                with open(acc_file, 'r') as f:
                    accuracy_data = json.load(f)
                
                report['historical_accuracy'] = accuracy_data.get('betting_performance', {})
            
            # TBD status
            tbd_status = self.step_5_check_tbd_status()
            report['tbd_status'] = tbd_status
            
            # Overall status
            if any(step['status'] == 'ERROR' for step in self.workflow_log):
                report['status'] = 'PARTIAL'
            elif tbd_status['tbd_count'] > 0:
                report['status'] = 'MONITORING'
            else:
                report['status'] = 'COMPLETE'
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            report['status'] = 'ERROR'
        
        return report
    
    def save_daily_report(self, report: Dict) -> None:
        """Save the daily report"""
        filename = f'data/daily_automation_report_{self.current_date.replace("-", "_")}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"💾 Daily report saved: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving daily report: {e}")
    
    def display_summary(self, report: Dict) -> None:
        """Display workflow summary"""
        
        logger.info("=" * 60)
        logger.info(f"📊 DAILY MLB AUTOMATION SUMMARY - {self.current_date}")
        logger.info("=" * 60)
        
        # Workflow steps
        for step in self.workflow_log:
            status_emoji = "✅" if step['status'] == "SUCCESS" else "❌" if step['status'] == "ERROR" else "🔄"
            logger.info(f"{status_emoji} {step['step']}: {step['status']}")
        
        # Betting summary
        if 'betting_summary' in report:
            betting = report['betting_summary']
            logger.info(f"\n🎯 TODAY'S BETTING OPPORTUNITIES:")
            logger.info(f"   Total Games: {betting.get('total_games', 0)}")
            logger.info(f"   Moneyline Picks: {betting.get('moneyline_picks', 0)}")
            logger.info(f"   Over Picks: {betting.get('over_picks', 0)}")
            logger.info(f"   Under Picks: {betting.get('under_picks', 0)}")
            logger.info(f"   High Confidence: {betting.get('high_confidence_picks', 0)}")
        
        # Historical accuracy
        if 'historical_accuracy' in report:
            accuracy = report['historical_accuracy']
            logger.info(f"\n📈 HISTORICAL PERFORMANCE (97 games):")
            logger.info(f"   Winner Accuracy: {accuracy.get('winner_predictions_correct', 0)}/97 ({accuracy.get('winner_accuracy_pct', 0)}%)")
            logger.info(f"   Total Accuracy: {accuracy.get('total_predictions_correct', 0)}/97 ({accuracy.get('total_accuracy_pct', 0)}%)")
            logger.info(f"   Perfect Games: {accuracy.get('perfect_games', 0)}/97 ({accuracy.get('perfect_games_pct', 0)}%)")
        
        # TBD status
        tbd_status = report.get('tbd_status', {})
        if tbd_status.get('tbd_count', 0) > 0:
            logger.info(f"\n⏱️ TBD MONITORING:")
            logger.info(f"   Games with TBDs: {tbd_status['tbd_count']}")
            for game in tbd_status['games']:
                away_tbd = "TBD" if game['away_pitcher'] == 'TBD' else "✓"
                home_tbd = "TBD" if game['home_pitcher'] == 'TBD' else "✓"
                logger.info(f"   - {game['game']}: {away_tbd} vs {home_tbd}")
        else:
            logger.info(f"\n✅ ALL PITCHERS CONFIRMED")
        
        logger.info(f"\n🎯 OVERALL STATUS: {report['status']}")
        logger.info("=" * 60)
    
    def run_daily_workflow(self, start_monitoring: bool = False) -> Dict:
        """Run the complete daily workflow"""
        
        logger.info(f"🚀 Starting Daily MLB Automation for {self.current_date}")
        
        # Step 1: Fetch starting pitchers
        self.step_1_fetch_pitchers()
        
        # Step 2: Generate predictions
        self.step_2_generate_predictions()
        
        # Step 3: Generate betting recommendations
        self.step_3_betting_recommendations()
        
        # Step 4: Update historical accuracy
        self.step_4_update_historical_accuracy()
        
        # Step 5: Check TBD status
        tbd_status = self.step_5_check_tbd_status()
        
        # Generate and save report
        report = self.generate_daily_report()
        self.save_daily_report(report)
        
        # Display summary
        self.display_summary(report)
        
        # Optionally start TBD monitoring
        if start_monitoring and tbd_status['tbd_count'] > 0:
            logger.info(f"\n🔄 Starting TBD monitoring for {tbd_status['tbd_count']} games...")
            self.run_script('auto_tbd_monitor.py', 'Start TBD Monitoring')
        
        return report

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily MLB Automation')
    parser.add_argument('--monitor', action='store_true', help='Start TBD monitoring after workflow')
    args = parser.parse_args()
    
    automation = DailyMLBAutomation()
    report = automation.run_daily_workflow(start_monitoring=args.monitor)
    
    # Exit with appropriate code
    if report['status'] == 'ERROR':
        sys.exit(1)
    elif report['status'] == 'PARTIAL':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
