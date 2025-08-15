#!/usr/bin/env python3
"""
Historical Frontend Duplicate Checker
=====================================

Check the historical analysis frontend and backend APIs for duplicate games
that might be showing up in the display.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_frontend_check.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HistoricalFrontendChecker')

class HistoricalFrontendDuplicateChecker:
    """Check historical frontend for duplicate games"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"  # Assuming Flask app runs on port 5000
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
    def check_frontend_apis(self, date_str: str) -> Dict[str, Any]:
        """Check all frontend API endpoints for duplicates"""
        
        logger.info(f"Checking frontend APIs for date: {date_str}")
        
        report = {
            'date': date_str,
            'endpoints': {},
            'duplicate_analysis': {},
            'cross_endpoint_comparison': {}
        }
        
        # Test all the endpoints the frontend uses
        endpoints_to_test = [
            f"/api/historical-recap/{date_str}",
            f"/api/historical/{date_str}",
            f"/api/today-games?date={date_str}"
        ]
        
        for endpoint in endpoints_to_test:
            endpoint_report = self._test_endpoint(endpoint, date_str)
            report['endpoints'][endpoint] = endpoint_report
        
        # Analyze duplicates within each endpoint
        report['duplicate_analysis'] = self._analyze_duplicates(report['endpoints'])
        
        # Compare data across endpoints
        report['cross_endpoint_comparison'] = self._compare_endpoints(report['endpoints'])
        
        return report
    
    def _test_endpoint(self, endpoint: str, date_str: str) -> Dict[str, Any]:
        """Test a specific API endpoint"""
        
        try:
            logger.info(f"Testing endpoint: {endpoint}")
            url = self.base_url + endpoint
            
            response = requests.get(url, timeout=30)
            
            endpoint_report = {
                'url': url,
                'status_code': response.status_code,
                'success': False,
                'games': [],
                'game_count': 0,
                'error': None,
                'duplicate_games': [],
                'unique_identifiers': []
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get('success') and data.get('games'):
                        games = data['games']
                        endpoint_report['success'] = True
                        endpoint_report['games'] = games
                        endpoint_report['game_count'] = len(games)
                        
                        # Check for duplicates within this endpoint
                        duplicates = self._find_duplicates_in_games(games)
                        endpoint_report['duplicate_games'] = duplicates
                        
                        # Extract unique identifiers
                        identifiers = self._extract_game_identifiers(games)
                        endpoint_report['unique_identifiers'] = identifiers
                        
                        logger.info(f"✅ {endpoint}: {len(games)} games, {len(duplicates)} duplicates")
                        
                    else:
                        endpoint_report['error'] = data.get('error', 'No games found')
                        logger.warning(f"⚠️  {endpoint}: {endpoint_report['error']}")
                
                except json.JSONDecodeError as e:
                    endpoint_report['error'] = f"JSON decode error: {e}"
                    logger.error(f"❌ {endpoint}: JSON decode error")
            
            else:
                endpoint_report['error'] = f"HTTP {response.status_code}"
                logger.error(f"❌ {endpoint}: HTTP {response.status_code}")
            
            return endpoint_report
            
        except Exception as e:
            logger.error(f"❌ Error testing {endpoint}: {e}")
            return {
                'url': endpoint,
                'success': False,
                'error': str(e),
                'games': [],
                'game_count': 0,
                'duplicate_games': [],
                'unique_identifiers': []
            }
    
    def _find_duplicates_in_games(self, games: List[Dict]) -> List[Dict]:
        """Find duplicate games within a single endpoint's response"""
        
        # Track games by different potential duplicate keys
        duplicate_trackers = {
            'matchup': defaultdict(list),  # away_team + home_team
            'game_id': defaultdict(list),   # game_id if available
            'game_pk': defaultdict(list),   # game_pk if available
            'time_matchup': defaultdict(list)  # game_time + teams
        }
        
        for i, game in enumerate(games):
            # Create matchup key
            away_team = game.get('away_team', '').strip()
            home_team = game.get('home_team', '').strip()
            matchup_key = f"{away_team} @ {home_team}"
            duplicate_trackers['matchup'][matchup_key].append((i, game))
            
            # Game ID key
            game_id = game.get('game_id')
            if game_id:
                duplicate_trackers['game_id'][game_id].append((i, game))
            
            # Game PK key
            game_pk = game.get('game_pk')
            if game_pk:
                duplicate_trackers['game_pk'][game_pk].append((i, game))
            
            # Time + matchup key
            game_time = game.get('game_time', game.get('date', ''))
            time_matchup_key = f"{game_time}|{matchup_key}"
            duplicate_trackers['time_matchup'][time_matchup_key].append((i, game))
        
        # Find duplicates
        duplicates = []
        
        for tracker_name, tracker in duplicate_trackers.items():
            for key, game_list in tracker.items():
                if len(game_list) > 1:
                    duplicates.append({
                        'type': tracker_name,
                        'key': key,
                        'count': len(game_list),
                        'games': [game for _, game in game_list],
                        'indices': [i for i, _ in game_list]
                    })
        
        return duplicates
    
    def _extract_game_identifiers(self, games: List[Dict]) -> List[str]:
        """Extract unique identifiers from games"""
        identifiers = set()
        
        for game in games:
            # Try different identifier combinations
            away = game.get('away_team', '').strip()
            home = game.get('home_team', '').strip()
            
            if away and home:
                identifiers.add(f"{away} @ {home}")
            
            # Add game IDs if available
            if game.get('game_id'):
                identifiers.add(f"ID:{game['game_id']}")
            
            if game.get('game_pk'):
                identifiers.add(f"PK:{game['game_pk']}")
        
        return sorted(list(identifiers))
    
    def _analyze_duplicates(self, endpoints: Dict) -> Dict[str, Any]:
        """Analyze duplicates across all endpoints"""
        
        analysis = {
            'total_endpoints_tested': len(endpoints),
            'endpoints_with_duplicates': 0,
            'total_duplicates_found': 0,
            'duplicate_details': []
        }
        
        for endpoint, data in endpoints.items():
            if data.get('duplicate_games'):
                analysis['endpoints_with_duplicates'] += 1
                analysis['total_duplicates_found'] += len(data['duplicate_games'])
                
                analysis['duplicate_details'].append({
                    'endpoint': endpoint,
                    'duplicates': data['duplicate_games'],
                    'game_count': data.get('game_count', 0)
                })
        
        return analysis
    
    def _compare_endpoints(self, endpoints: Dict) -> Dict[str, Any]:
        """Compare data consistency across different endpoints"""
        
        comparison = {
            'game_count_consistency': {},
            'data_overlap': {},
            'inconsistencies': []
        }
        
        # Count games per endpoint
        game_counts = {}
        all_identifiers = {}
        
        for endpoint, data in endpoints.items():
            if data.get('success'):
                game_counts[endpoint] = data.get('game_count', 0)
                all_identifiers[endpoint] = set(data.get('unique_identifiers', []))
        
        comparison['game_count_consistency'] = game_counts
        
        # Check for overlaps and differences
        if len(all_identifiers) > 1:
            endpoint_names = list(all_identifiers.keys())
            for i in range(len(endpoint_names)):
                for j in range(i + 1, len(endpoint_names)):
                    ep1, ep2 = endpoint_names[i], endpoint_names[j]
                    set1, set2 = all_identifiers[ep1], all_identifiers[ep2]
                    
                    overlap = set1 & set2
                    only_in_1 = set1 - set2
                    only_in_2 = set2 - set1
                    
                    comparison['data_overlap'][f"{ep1} vs {ep2}"] = {
                        'overlap_count': len(overlap),
                        'only_in_first': len(only_in_1),
                        'only_in_second': len(only_in_2),
                        'overlap_items': sorted(list(overlap)),
                        'only_in_first_items': sorted(list(only_in_1)),
                        'only_in_second_items': sorted(list(only_in_2))
                    }
        
        return comparison
    
    def generate_report(self, report: Dict[str, Any], output_file: str = None) -> str:
        """Generate a detailed report"""
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"historical_frontend_duplicate_report_{timestamp}.txt"
        
        lines = []
        lines.append("=" * 80)
        lines.append("HISTORICAL FRONTEND DUPLICATE CHECKER REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Date Analyzed: {report['date']}")
        lines.append("")
        
        # Endpoint Summary
        lines.append("API ENDPOINT SUMMARY")
        lines.append("-" * 40)
        
        for endpoint, data in report['endpoints'].items():
            status = "✅ SUCCESS" if data.get('success') else "❌ FAILED"
            game_count = data.get('game_count', 0)
            duplicate_count = len(data.get('duplicate_games', []))
            
            lines.append(f"{endpoint}")
            lines.append(f"  Status: {status}")
            lines.append(f"  Game Count: {game_count}")
            lines.append(f"  Duplicates: {duplicate_count}")
            
            if data.get('error'):
                lines.append(f"  Error: {data['error']}")
            
            lines.append("")
        
        # Duplicate Analysis
        dup_analysis = report['duplicate_analysis']
        lines.append("DUPLICATE ANALYSIS")
        lines.append("-" * 40)
        lines.append(f"Endpoints with duplicates: {dup_analysis['endpoints_with_duplicates']}")
        lines.append(f"Total duplicates found: {dup_analysis['total_duplicates_found']}")
        
        if dup_analysis['duplicate_details']:
            lines.append("\nDuplicate Details:")
            for detail in dup_analysis['duplicate_details']:
                lines.append(f"  {detail['endpoint']}:")
                for dup in detail['duplicates']:
                    lines.append(f"    - {dup['type']}: '{dup['key']}' ({dup['count']} copies)")
        else:
            lines.append("\n✅ No duplicates found in any endpoint!")
        
        lines.append("")
        
        # Cross-endpoint comparison
        comparison = report['cross_endpoint_comparison']
        lines.append("CROSS-ENDPOINT COMPARISON")
        lines.append("-" * 40)
        
        # Game count consistency
        lines.append("Game Counts:")
        for endpoint, count in comparison['game_count_consistency'].items():
            lines.append(f"  {endpoint}: {count} games")
        
        # Data overlap
        if comparison['data_overlap']:
            lines.append("\nData Overlap Analysis:")
            for comparison_key, overlap_data in comparison['data_overlap'].items():
                lines.append(f"  {comparison_key}:")
                lines.append(f"    Overlap: {overlap_data['overlap_count']} games")
                lines.append(f"    Only in first: {overlap_data['only_in_first']}")
                lines.append(f"    Only in second: {overlap_data['only_in_second']}")
        
        # Save report
        report_content = "\n".join(lines)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
        
        return report_content

def main():
    """Main function to run the historical frontend checker"""
    
    checker = HistoricalFrontendDuplicateChecker()
    
    # Check yesterday by default
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n🔍 Historical Frontend Duplicate Checker")
    print(f"Checking date: {yesterday}")
    print(f"Base URL: {checker.base_url}")
    print("=" * 60)
    
    # Note: This requires the Flask app to be running
    print("⚠️  Note: Make sure your Flask app is running on localhost:5000")
    print("   You can start it with: python app.py")
    print("")
    
    try:
        # Run the check
        report = checker.check_frontend_apis(yesterday)
        
        # Generate and display report
        report_content = checker.generate_report(report)
        
        print("\n" + "=" * 60)
        print("SUMMARY RESULTS:")
        print("=" * 60)
        
        # Display key findings
        dup_analysis = report['duplicate_analysis']
        print(f"Endpoints tested: {dup_analysis['total_endpoints_tested']}")
        print(f"Endpoints with duplicates: {dup_analysis['endpoints_with_duplicates']}")
        print(f"Total duplicates found: {dup_analysis['total_duplicates_found']}")
        
        # Game count summary
        comparison = report['cross_endpoint_comparison']
        print(f"\nGame counts by endpoint:")
        for endpoint, count in comparison['game_count_consistency'].items():
            print(f"  {endpoint}: {count} games")
        
        if dup_analysis['total_duplicates_found'] > 0:
            print(f"\n⚠️  Found duplicates! Check the detailed report for more info.")
        else:
            print(f"\n✅ No duplicates found in the frontend APIs!")
        
        print(f"\n📝 Detailed report saved.")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        logger.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()
