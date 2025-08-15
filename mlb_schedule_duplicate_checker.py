#!/usr/bin/env python3
"""
MLB Schedule Duplicate Checker
=============================

Fetches MLB schedule from official MLB API and compares with local database
to identify duplicate games and discrepancies.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mlb_schedule_check.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MLBScheduleChecker')

class MLBScheduleDuplicateChecker:
    """Check for duplicate games by comparing MLB API with local database"""
    
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_file = os.path.join(self.root_dir, 'game_scores_cache.json')
        self.backup_cache = os.path.join(self.root_dir, 'MLB-Betting', 'game_scores_cache.json')
        
    def fetch_mlb_schedule(self, date_str: str) -> List[Dict[str, Any]]:
        """Fetch official MLB schedule for a specific date"""
        try:
            url = f"{self.base_url}/schedule"
            params = {
                'sportId': 1,
                'date': date_str,
                'hydrate': 'game(content(editorial(preview,recap)),decisions,person,probablePitcher,stats,homeRuns,previousPlay,team),linescore(runners),xrefId,story'
            }
            
            logger.info(f"Fetching MLB schedule for {date_str}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            games = []
            
            for date_entry in data.get('dates', []):
                for game in date_entry.get('games', []):
                    game_data = self._parse_mlb_game(game, date_str)
                    games.append(game_data)
            
            logger.info(f"Found {len(games)} official games for {date_str}")
            return games
            
        except Exception as e:
            logger.error(f"Error fetching MLB schedule for {date_str}: {e}")
            return []
    
    def _parse_mlb_game(self, game: Dict, date_str: str) -> Dict[str, Any]:
        """Parse MLB API game data into standardized format"""
        try:
            # Extract team information
            away_team = game['teams']['away']['team']['name']
            home_team = game['teams']['home']['team']['name']
            away_team_id = game['teams']['away']['team']['id']
            home_team_id = game['teams']['home']['team']['id']
            
            # Extract probable pitchers
            away_pitcher = "TBD"
            home_pitcher = "TBD"
            
            if 'probablePitcher' in game['teams']['away']:
                away_pitcher = game['teams']['away']['probablePitcher']['fullName']
            if 'probablePitcher' in game['teams']['home']:
                home_pitcher = game['teams']['home']['probablePitcher']['fullName']
            
            # Extract scores if final
            away_score = None
            home_score = None
            is_final = False
            
            if game['status']['abstractGameState'] == 'Final':
                is_final = True
                away_score = game['teams']['away'].get('score')
                home_score = game['teams']['home'].get('score')
            
            return {
                'game_pk': game['gamePk'],
                'date': date_str,
                'away_team': away_team,
                'away_team_id': away_team_id,
                'home_team': home_team,
                'home_team_id': home_team_id,
                'away_pitcher': away_pitcher,
                'home_pitcher': home_pitcher,
                'status': game['status']['detailedState'],
                'status_code': game['status']['statusCode'],
                'game_time': game.get('gameDate'),
                'venue': game.get('venue', {}).get('name', 'Unknown'),
                'is_final': is_final,
                'away_score': away_score,
                'home_score': home_score,
                'data_source': 'MLB API Official'
            }
            
        except Exception as e:
            logger.error(f"Error parsing game data: {e}")
            return {}
    
    def load_local_cache(self, date_str: str) -> List[Dict[str, Any]]:
        """Load games from local cache for specified date"""
        try:
            # Try main cache first
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if date_str in cache_data:
                    games = cache_data[date_str].get('games', [])
                    logger.info(f"Found {len(games)} games in main cache for {date_str}")
                    return games
            
            # Try backup cache
            if os.path.exists(self.backup_cache):
                with open(self.backup_cache, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if date_str in cache_data:
                    games = cache_data[date_str].get('games', [])
                    logger.info(f"Found {len(games)} games in backup cache for {date_str}")
                    return games
            
            logger.warning(f"No local data found for {date_str}")
            return []
            
        except Exception as e:
            logger.error(f"Error loading local cache for {date_str}: {e}")
            return []
    
    def compare_schedules(self, date_str: str) -> Dict[str, Any]:
        """Compare MLB API schedule with local cache for discrepancies"""
        
        # Fetch official schedule
        official_games = self.fetch_mlb_schedule(date_str)
        
        # Load local cache
        local_games = self.load_local_cache(date_str)
        
        # Create comparison report
        report = {
            'date': date_str,
            'official_count': len(official_games),
            'local_count': len(local_games),
            'official_games': official_games,
            'local_games': local_games,
            'duplicates_found': [],
            'missing_from_local': [],
            'extra_in_local': [],
            'discrepancies': []
        }
        
        # Create lookup dictionaries
        official_by_pk = {g['game_pk']: g for g in official_games if g.get('game_pk')}
        local_by_pk = {g.get('game_pk'): g for g in local_games if g.get('game_pk')}
        
        # Find missing games (in official but not in local)
        for game_pk, game in official_by_pk.items():
            if game_pk not in local_by_pk:
                report['missing_from_local'].append(game)
        
        # Find extra games (in local but not in official)
        for game_pk, game in local_by_pk.items():
            if game_pk not in official_by_pk:
                report['extra_in_local'].append(game)
        
        # Check for duplicates within local cache
        local_pks = [g.get('game_pk') for g in local_games if g.get('game_pk')]
        duplicate_pks = [pk for pk in set(local_pks) if local_pks.count(pk) > 1]
        
        for pk in duplicate_pks:
            duplicates = [g for g in local_games if g.get('game_pk') == pk]
            report['duplicates_found'].append({
                'game_pk': pk,
                'count': len(duplicates),
                'duplicates': duplicates
            })
        
        # Check for data discrepancies in matching games
        for game_pk in set(official_by_pk.keys()) & set(local_by_pk.keys()):
            official = official_by_pk[game_pk]
            local = local_by_pk[game_pk]
            
            discrepancies = []
            
            # Compare team names
            if official['away_team'] != local.get('away_team'):
                discrepancies.append({
                    'field': 'away_team',
                    'official': official['away_team'],
                    'local': local.get('away_team')
                })
            
            if official['home_team'] != local.get('home_team'):
                discrepancies.append({
                    'field': 'home_team',
                    'official': official['home_team'],
                    'local': local.get('home_team')
                })
            
            # Compare pitcher names
            if official['away_pitcher'] != local.get('away_pitcher'):
                discrepancies.append({
                    'field': 'away_pitcher',
                    'official': official['away_pitcher'],
                    'local': local.get('away_pitcher')
                })
            
            if official['home_pitcher'] != local.get('home_pitcher'):
                discrepancies.append({
                    'field': 'home_pitcher',
                    'official': official['home_pitcher'],
                    'local': local.get('home_pitcher')
                })
            
            if discrepancies:
                report['discrepancies'].append({
                    'game_pk': game_pk,
                    'matchup': f"{official['away_team']} @ {official['home_team']}",
                    'discrepancies': discrepancies
                })
        
        return report
    
    def check_date_range(self, start_date: str, end_date: str = None) -> Dict[str, Any]:
        """Check multiple dates for duplicates and discrepancies"""
        
        if end_date is None:
            end_date = start_date
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        summary_report = {
            'date_range': f"{start_date} to {end_date}",
            'total_dates_checked': 0,
            'dates_with_issues': 0,
            'total_duplicates': 0,
            'total_missing': 0,
            'total_extra': 0,
            'daily_reports': {}
        }
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            logger.info(f"\n{'='*50}")
            logger.info(f"Checking date: {date_str}")
            logger.info(f"{'='*50}")
            
            report = self.compare_schedules(date_str)
            summary_report['daily_reports'][date_str] = report
            summary_report['total_dates_checked'] += 1
            
            # Count issues
            has_issues = False
            if report['duplicates_found']:
                summary_report['total_duplicates'] += len(report['duplicates_found'])
                has_issues = True
            
            if report['missing_from_local']:
                summary_report['total_missing'] += len(report['missing_from_local'])
                has_issues = True
            
            if report['extra_in_local']:
                summary_report['total_extra'] += len(report['extra_in_local'])
                has_issues = True
            
            if has_issues:
                summary_report['dates_with_issues'] += 1
            
            # Print daily summary
            logger.info(f"Official games: {report['official_count']}")
            logger.info(f"Local games: {report['local_count']}")
            logger.info(f"Duplicates: {len(report['duplicates_found'])}")
            logger.info(f"Missing from local: {len(report['missing_from_local'])}")
            logger.info(f"Extra in local: {len(report['extra_in_local'])}")
            logger.info(f"Data discrepancies: {len(report['discrepancies'])}")
            
            current_dt += timedelta(days=1)
        
        return summary_report
    
    def fix_duplicates(self, date_str: str, dry_run: bool = True) -> bool:
        """Remove duplicate games from local cache"""
        try:
            # Load current cache
            if not os.path.exists(self.cache_file):
                logger.error(f"Cache file not found: {self.cache_file}")
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if date_str not in cache_data:
                logger.info(f"No data found for {date_str}")
                return True
            
            original_games = cache_data[date_str].get('games', [])
            original_count = len(original_games)
            
            # Remove duplicates by game_pk
            seen_pks = set()
            unique_games = []
            
            for game in original_games:
                game_pk = game.get('game_pk')
                if game_pk and game_pk not in seen_pks:
                    seen_pks.add(game_pk)
                    unique_games.append(game)
                elif game_pk:
                    logger.warning(f"Removing duplicate game: {game_pk}")
            
            # Update cache data
            cache_data[date_str]['games'] = unique_games
            cache_data[date_str]['last_update'] = datetime.now().isoformat()
            
            final_count = len(unique_games)
            removed_count = original_count - final_count
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} duplicate games for {date_str}")
                
                if not dry_run:
                    # Save updated cache
                    with open(self.cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Updated cache file saved")
                else:
                    logger.info("DRY RUN - No changes saved")
            else:
                logger.info(f"No duplicates found for {date_str}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing duplicates for {date_str}: {e}")
            return False
    
    def generate_report(self, summary_report: Dict[str, Any], output_file: str = None) -> str:
        """Generate detailed text report"""
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"mlb_schedule_check_report_{timestamp}.txt"
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("MLB SCHEDULE DUPLICATE CHECKER REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Date Range: {summary_report['date_range']}")
        report_lines.append("")
        
        # Summary
        report_lines.append("SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total dates checked: {summary_report['total_dates_checked']}")
        report_lines.append(f"Dates with issues: {summary_report['dates_with_issues']}")
        report_lines.append(f"Total duplicates found: {summary_report['total_duplicates']}")
        report_lines.append(f"Total missing games: {summary_report['total_missing']}")
        report_lines.append(f"Total extra games: {summary_report['total_extra']}")
        report_lines.append("")
        
        # Daily details
        for date_str, report in summary_report['daily_reports'].items():
            report_lines.append(f"DATE: {date_str}")
            report_lines.append("-" * 40)
            report_lines.append(f"Official games: {report['official_count']}")
            report_lines.append(f"Local games: {report['local_count']}")
            
            if report['duplicates_found']:
                report_lines.append(f"\n🔄 DUPLICATES FOUND ({len(report['duplicates_found'])}):")
                for dup in report['duplicates_found']:
                    report_lines.append(f"  Game PK {dup['game_pk']}: {dup['count']} copies")
            
            if report['missing_from_local']:
                report_lines.append(f"\n❌ MISSING FROM LOCAL ({len(report['missing_from_local'])}):")
                for game in report['missing_from_local']:
                    report_lines.append(f"  {game['game_pk']}: {game['away_team']} @ {game['home_team']}")
            
            if report['extra_in_local']:
                report_lines.append(f"\n➕ EXTRA IN LOCAL ({len(report['extra_in_local'])}):")
                for game in report['extra_in_local']:
                    report_lines.append(f"  {game.get('game_pk')}: {game.get('away_team')} @ {game.get('home_team')}")
            
            if report['discrepancies']:
                report_lines.append(f"\n⚠️  DATA DISCREPANCIES ({len(report['discrepancies'])}):")
                for disc in report['discrepancies']:
                    report_lines.append(f"  {disc['game_pk']}: {disc['matchup']}")
                    for d in disc['discrepancies']:
                        report_lines.append(f"    {d['field']}: '{d['local']}' → '{d['official']}'")
            
            report_lines.append("")
        
        # Save report
        report_content = "\n".join(report_lines)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
        
        return report_content

def main():
    """Main function to run the duplicate checker"""
    
    checker = MLBScheduleDuplicateChecker()
    
    # Check yesterday (August 14th) by default
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n🔍 MLB Schedule Duplicate Checker")
    print(f"Checking date: {yesterday}")
    print("=" * 50)
    
    # Run the check
    summary = checker.check_date_range(yesterday)
    
    # Generate and display report
    report_content = checker.generate_report(summary)
    print("\n" + "=" * 50)
    print("SUMMARY RESULTS:")
    print("=" * 50)
    print(f"Total duplicates found: {summary['total_duplicates']}")
    print(f"Total missing games: {summary['total_missing']}")
    print(f"Total extra games: {summary['total_extra']}")
    
    # Offer to fix duplicates
    if summary['total_duplicates'] > 0:
        print(f"\n⚠️  Found {summary['total_duplicates']} duplicate games!")
        response = input("Would you like to fix the duplicates? (y/n): ")
        if response.lower() == 'y':
            print("Fixing duplicates...")
            checker.fix_duplicates(yesterday, dry_run=False)
            print("Duplicates fixed!")
    
    print(f"\n📝 Detailed report saved to the generated report file.")

if __name__ == "__main__":
    main()
