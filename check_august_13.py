#!/usr/bin/env python3
"""
Quick check for August 13th
"""

from mlb_schedule_duplicate_checker import MLBScheduleDuplicateChecker

def check_august_13():
    checker = MLBScheduleDuplicateChecker()
    report = checker.compare_schedules('2025-08-13')
    
    print(f'August 13th Results:')
    print(f'Official games: {report["official_count"]}')
    print(f'Local games: {report["local_count"]}')
    print(f'Duplicates: {len(report["duplicates_found"])}')
    print(f'Missing: {len(report["missing_from_local"])}')
    print(f'Extra: {len(report["extra_in_local"])}')
    
    if report['duplicates_found']:
        print('\nDuplicates found:')
        for dup in report['duplicates_found']:
            print(f'  Game PK {dup["game_pk"]}: {dup["count"]} copies')
    
    if report['extra_in_local']:
        print('\nExtra games in local:')
        for game in report['extra_in_local']:
            print(f'  {game.get("game_pk")}: {game.get("away_team")} @ {game.get("home_team")}')
    
    if report['missing_from_local']:
        print('\nMissing from local:')
        for game in report['missing_from_local']:
            print(f'  {game["game_pk"]}: {game["away_team"]} @ {game["home_team"]}')

if __name__ == "__main__":
    check_august_13()
