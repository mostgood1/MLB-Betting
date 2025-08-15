#!/usr/bin/env python3
"""
Daily MLB Schedule Monitor
=========================

Daily monitoring script to ensure MLB game data stays synchronized
with the official MLB API. Can be run as part of daily automation.
"""

import sys
import json
import logging
from datetime import datetime, timedelta
from mlb_schedule_duplicate_checker import MLBScheduleDuplicateChecker

def setup_logging():
    """Setup logging for daily monitoring"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('daily_mlb_monitor.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('DailyMLBMonitor')

def daily_monitor(date_str=None, days_back=3):
    """
    Monitor MLB schedule for the specified date and previous days
    
    Args:
        date_str: Date to check (YYYY-MM-DD). If None, uses yesterday.
        days_back: Number of additional days to check backwards
    """
    
    logger = setup_logging()
    checker = MLBScheduleDuplicateChecker()
    
    if date_str is None:
        # Default to yesterday
        target_date = datetime.now() - timedelta(days=1)
        date_str = target_date.strftime('%Y-%m-%d')
    else:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    logger.info(f"🔍 Daily MLB Schedule Monitor")
    logger.info(f"Target date: {date_str}")
    logger.info(f"Checking {days_back + 1} days back")
    
    issues_found = []
    total_checked = 0
    
    # Check target date and days back
    for i in range(days_back + 1):
        check_date = target_date - timedelta(days=i)
        check_date_str = check_date.strftime('%Y-%m-%d')
        
        try:
            logger.info(f"\nChecking {check_date_str}...")
            report = checker.compare_schedules(check_date_str)
            total_checked += 1
            
            # Check for issues
            has_issues = False
            issue_summary = {
                'date': check_date_str,
                'official_count': report['official_count'],
                'local_count': report['local_count'],
                'issues': []
            }
            
            if report['duplicates_found']:
                has_issues = True
                issue_summary['issues'].append(f"Duplicates: {len(report['duplicates_found'])}")
                logger.warning(f"🔄 Found {len(report['duplicates_found'])} duplicates")
            
            if report['missing_from_local']:
                has_issues = True
                issue_summary['issues'].append(f"Missing: {len(report['missing_from_local'])}")
                logger.warning(f"❌ Missing {len(report['missing_from_local'])} games from local")
            
            if report['extra_in_local']:
                has_issues = True
                issue_summary['issues'].append(f"Extra: {len(report['extra_in_local'])}")
                logger.warning(f"➕ Found {len(report['extra_in_local'])} extra games in local")
            
            if report['official_count'] != report['local_count']:
                has_issues = True
                issue_summary['issues'].append(f"Count mismatch: {report['official_count']} vs {report['local_count']}")
                logger.warning(f"📊 Game count mismatch: Official={report['official_count']}, Local={report['local_count']}")
            
            if has_issues:
                issues_found.append(issue_summary)
                logger.error(f"❌ Issues found for {check_date_str}")
            else:
                logger.info(f"✅ {check_date_str}: OK (Official={report['official_count']}, Local={report['local_count']})")
        
        except Exception as e:
            logger.error(f"❌ Error checking {check_date_str}: {e}")
            issues_found.append({
                'date': check_date_str,
                'error': str(e)
            })
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info(f"DAILY MONITOR SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total dates checked: {total_checked}")
    logger.info(f"Dates with issues: {len(issues_found)}")
    
    if issues_found:
        logger.warning(f"\n⚠️  ISSUES DETECTED:")
        for issue in issues_found:
            if 'error' in issue:
                logger.error(f"  {issue['date']}: ERROR - {issue['error']}")
            else:
                logger.warning(f"  {issue['date']}: {', '.join(issue['issues'])}")
        
        # Save issues to file for investigation
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        issues_file = f"mlb_monitor_issues_{timestamp}.json"
        
        with open(issues_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'target_date': date_str,
                'days_checked': days_back + 1,
                'issues': issues_found
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📝 Issues saved to: {issues_file}")
        return False
    else:
        logger.info(f"✅ All dates are synchronized correctly!")
        return True

def auto_fix_issues(date_str=None):
    """Automatically fix common issues like duplicates"""
    
    logger = setup_logging()
    checker = MLBScheduleDuplicateChecker()
    
    if date_str is None:
        # Default to yesterday
        target_date = datetime.now() - timedelta(days=1)
        date_str = target_date.strftime('%Y-%m-%d')
    
    logger.info(f"🔧 Auto-fixing issues for {date_str}")
    
    try:
        # Check for duplicates and fix them
        success = checker.fix_duplicates(date_str, dry_run=False)
        
        if success:
            logger.info(f"✅ Auto-fix completed for {date_str}")
            return True
        else:
            logger.error(f"❌ Auto-fix failed for {date_str}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error during auto-fix: {e}")
        return False

def main():
    """Main function - can be called from command line or other scripts"""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--fix":
            # Auto-fix mode
            date_arg = sys.argv[2] if len(sys.argv) > 2 else None
            return auto_fix_issues(date_arg)
        else:
            # Monitor specific date
            date_arg = sys.argv[1]
            days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            return daily_monitor(date_arg, days_back)
    else:
        # Default monitor mode
        return daily_monitor()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
