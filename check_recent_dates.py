#!/usr/bin/env python3
"""
Check multiple dates for game count discrepancies
"""

from mlb_schedule_duplicate_checker import MLBScheduleDuplicateChecker
from datetime import datetime, timedelta

def check_recent_dates():
    checker = MLBScheduleDuplicateChecker()
    
    # Check last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print("Checking last 7 days for game count discrepancies...")
    print("=" * 60)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            report = checker.compare_schedules(date_str)
            
            status = "✅ OK"
            if report['duplicates_found'] or report['missing_from_local'] or report['extra_in_local']:
                status = "⚠️  ISSUES"
            
            print(f"{date_str}: Official={report['official_count']:2d}, Local={report['local_count']:2d}, Dups={len(report['duplicates_found'])}, Missing={len(report['missing_from_local'])}, Extra={len(report['extra_in_local'])} {status}")
            
            # Show details for problematic dates
            if report['duplicates_found']:
                for dup in report['duplicates_found']:
                    print(f"    🔄 Duplicate: Game PK {dup['game_pk']} ({dup['count']} copies)")
            
            if report['extra_in_local']:
                for game in report['extra_in_local']:
                    print(f"    ➕ Extra: {game.get('game_pk')} - {game.get('away_team')} @ {game.get('home_team')}")
            
            if report['missing_from_local']:
                for game in report['missing_from_local']:
                    print(f"    ❌ Missing: {game['game_pk']} - {game['away_team']} @ {game['home_team']}")
        
        except Exception as e:
            print(f"{date_str}: ERROR - {e}")
        
        current_date += timedelta(days=1)

if __name__ == "__main__":
    check_recent_dates()
