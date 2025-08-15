#!/usr/bin/env python3
"""
Historical Analysis Completeness Checker
========================================

Ensure all historical analysis cards are fully updated and complete
through yesterday, including performance analysis and final scores.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_analysis_completeness.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HistoricalAnalysisChecker')

class HistoricalAnalysisCompletenessChecker:
    """Check completeness of historical analysis data"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
    def check_date_range_completeness(self, start_date: str, end_date: str = None) -> Dict[str, Any]:
        """Check historical analysis completeness for a date range"""
        
        if end_date is None:
            end_date = start_date
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        logger.info(f"Checking historical analysis completeness from {start_date} to {end_date}")
        
        report = {
            'date_range': f"{start_date} to {end_date}",
            'dates_checked': 0,
            'dates_complete': 0,
            'dates_incomplete': 0,
            'dates_missing': 0,
            'total_games_found': 0,
            'total_games_with_analysis': 0,
            'daily_reports': {},
            'issues_found': [],
            'recommendations': []
        }
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            logger.info(f"Checking {date_str}...")
            daily_report = self._check_single_date(date_str)
            
            report['daily_reports'][date_str] = daily_report
            report['dates_checked'] += 1
            
            if daily_report['status'] == 'complete':
                report['dates_complete'] += 1
            elif daily_report['status'] == 'incomplete':
                report['dates_incomplete'] += 1
            else:
                report['dates_missing'] += 1
            
            report['total_games_found'] += daily_report['total_games']
            report['total_games_with_analysis'] += daily_report['games_with_analysis']
            
            if daily_report['issues']:
                report['issues_found'].extend([
                    {
                        'date': date_str,
                        'issue': issue
                    } for issue in daily_report['issues']
                ])
            
            current_dt += timedelta(days=1)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _check_single_date(self, date_str: str) -> Dict[str, Any]:
        """Check completeness for a single date"""
        
        daily_report = {
            'date': date_str,
            'status': 'missing',
            'total_games': 0,
            'games_with_analysis': 0,
            'games_with_final_scores': 0,
            'games_pending': 0,
            'api_success': False,
            'data_quality': {},
            'issues': [],
            'games_detail': []
        }
        
        try:
            # Try the historical recap endpoint first
            url = f"{self.base_url}/api/historical-recap/{date_str}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('games'):
                    daily_report['api_success'] = True
                    games = data['games']
                    daily_report['total_games'] = len(games)
                    
                    # Analyze each game
                    for game in games:
                        game_analysis = self._analyze_game_completeness(game)
                        daily_report['games_detail'].append(game_analysis)
                        
                        if game_analysis['has_performance_analysis']:
                            daily_report['games_with_analysis'] += 1
                        
                        if game_analysis['has_final_scores']:
                            daily_report['games_with_final_scores'] += 1
                        
                        if game_analysis['is_pending']:
                            daily_report['games_pending'] += 1
                        
                        # Collect issues
                        daily_report['issues'].extend(game_analysis['issues'])
                    
                    # Determine overall status
                    if daily_report['games_with_final_scores'] == daily_report['total_games']:
                        if daily_report['games_with_analysis'] == daily_report['games_with_final_scores']:
                            daily_report['status'] = 'complete'
                        else:
                            daily_report['status'] = 'incomplete'
                    else:
                        daily_report['status'] = 'incomplete'
                    
                    # Data quality metrics
                    daily_report['data_quality'] = {
                        'completion_rate': (daily_report['games_with_final_scores'] / daily_report['total_games']) * 100 if daily_report['total_games'] > 0 else 0,
                        'analysis_rate': (daily_report['games_with_analysis'] / daily_report['total_games']) * 100 if daily_report['total_games'] > 0 else 0,
                        'prediction_completeness': self._calculate_prediction_completeness(games),
                        'pitcher_data_completeness': self._calculate_pitcher_completeness(games)
                    }
                
                else:
                    daily_report['issues'].append("API returned no games or unsuccessful response")
            
            else:
                daily_report['issues'].append(f"API returned HTTP {response.status_code}")
        
        except Exception as e:
            daily_report['issues'].append(f"API error: {str(e)}")
        
        return daily_report
    
    def _analyze_game_completeness(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze completeness of a single game"""
        
        analysis = {
            'matchup': f"{game.get('away_team', 'Unknown')} @ {game.get('home_team', 'Unknown')}",
            'has_prediction': False,
            'has_final_scores': False,
            'has_performance_analysis': False,
            'is_pending': False,
            'prediction_quality': 'none',
            'issues': []
        }
        
        # Check prediction data
        prediction = game.get('prediction', {})
        if prediction:
            analysis['has_prediction'] = True
            
            # Check prediction completeness
            required_pred_fields = ['predicted_away_score', 'predicted_home_score', 'away_win_probability', 'home_win_probability']
            missing_pred_fields = [field for field in required_pred_fields if prediction.get(field) is None]
            
            if not missing_pred_fields:
                analysis['prediction_quality'] = 'complete'
            elif len(missing_pred_fields) < len(required_pred_fields):
                analysis['prediction_quality'] = 'partial'
                analysis['issues'].append(f"Missing prediction fields: {', '.join(missing_pred_fields)}")
            else:
                analysis['prediction_quality'] = 'minimal'
                analysis['issues'].append("Most prediction fields missing")
        else:
            analysis['issues'].append("No prediction data")
        
        # Check final scores
        result = game.get('result', {})
        if result and result.get('is_final'):
            analysis['has_final_scores'] = True
            
            # Validate score data
            if result.get('away_score') is None or result.get('home_score') is None:
                analysis['issues'].append("Final game missing score data")
        else:
            analysis['is_pending'] = True
            if result.get('status'):
                analysis['issues'].append(f"Game status: {result['status']}")
        
        # Check performance analysis
        perf_analysis = game.get('performance_analysis', {})
        if perf_analysis and perf_analysis.get('overall_grade') != 'N/A':
            analysis['has_performance_analysis'] = True
            
            # Check analysis completeness
            if not perf_analysis.get('grade_percentage'):
                analysis['issues'].append("Performance analysis missing grade percentage")
        elif analysis['has_final_scores']:
            analysis['issues'].append("Final game missing performance analysis")
        
        return analysis
    
    def _calculate_prediction_completeness(self, games: List[Dict]) -> float:
        """Calculate overall prediction data completeness percentage"""
        if not games:
            return 0.0
        
        total_fields = 0
        complete_fields = 0
        
        required_fields = ['predicted_away_score', 'predicted_home_score', 'away_win_probability', 'home_win_probability']
        
        for game in games:
            prediction = game.get('prediction', {})
            for field in required_fields:
                total_fields += 1
                if prediction.get(field) is not None:
                    complete_fields += 1
        
        return (complete_fields / total_fields) * 100 if total_fields > 0 else 0.0
    
    def _calculate_pitcher_completeness(self, games: List[Dict]) -> float:
        """Calculate pitcher data completeness percentage"""
        if not games:
            return 0.0
        
        total_pitcher_slots = len(games) * 2  # away and home pitcher for each game
        complete_pitcher_slots = 0
        
        for game in games:
            prediction = game.get('prediction', {})
            
            away_pitcher = prediction.get('away_pitcher')
            home_pitcher = prediction.get('home_pitcher')
            
            if away_pitcher and away_pitcher != 'TBD':
                complete_pitcher_slots += 1
            
            if home_pitcher and home_pitcher != 'TBD':
                complete_pitcher_slots += 1
        
        return (complete_pitcher_slots / total_pitcher_slots) * 100 if total_pitcher_slots > 0 else 0.0
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on the analysis"""
        
        recommendations = []
        
        # Check overall completion rate
        if report['dates_incomplete'] > 0:
            recommendations.append(f"📊 {report['dates_incomplete']} dates have incomplete analysis data")
        
        if report['dates_missing'] > 0:
            recommendations.append(f"❌ {report['dates_missing']} dates have no data available")
        
        # Check for specific issues
        issue_types = {}
        for issue in report['issues_found']:
            issue_text = issue['issue']
            if issue_text not in issue_types:
                issue_types[issue_text] = []
            issue_types[issue_text].append(issue['date'])
        
        for issue_type, dates in issue_types.items():
            if len(dates) > 1:
                recommendations.append(f"🔧 '{issue_type}' affects {len(dates)} dates: {', '.join(dates[:3])}{'...' if len(dates) > 3 else ''}")
        
        # Performance recommendations
        total_games = report['total_games_found']
        games_with_analysis = report['total_games_with_analysis']
        
        if total_games > 0:
            analysis_rate = (games_with_analysis / total_games) * 100
            if analysis_rate < 90:
                recommendations.append(f"📈 Only {analysis_rate:.1f}% of final games have performance analysis")
        
        if not recommendations:
            recommendations.append("✅ All historical analysis appears complete and up to date!")
        
        return recommendations
    
    def update_missing_analysis(self, date_str: str, dry_run: bool = True) -> Dict[str, Any]:
        """Update missing performance analysis for a specific date"""
        
        # This would trigger reprocessing of the historical data
        logger.info(f"Updating missing analysis for {date_str} (dry_run={dry_run})")
        
        # Implementation would call the backend to regenerate analysis
        # For now, return a placeholder result
        
        return {
            'date': date_str,
            'action': 'update_analysis',
            'dry_run': dry_run,
            'status': 'not_implemented',
            'message': 'Analysis update functionality would be implemented here'
        }
    
    def generate_report(self, analysis_report: Dict[str, Any], output_file: str = None) -> str:
        """Generate a detailed completeness report"""
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"historical_analysis_completeness_report_{timestamp}.txt"
        
        lines = []
        lines.append("=" * 80)
        lines.append("HISTORICAL ANALYSIS COMPLETENESS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Date Range: {analysis_report['date_range']}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Dates checked: {analysis_report['dates_checked']}")
        lines.append(f"Complete dates: {analysis_report['dates_complete']}")
        lines.append(f"Incomplete dates: {analysis_report['dates_incomplete']}")
        lines.append(f"Missing dates: {analysis_report['dates_missing']}")
        lines.append(f"Total games found: {analysis_report['total_games_found']}")
        lines.append(f"Games with analysis: {analysis_report['total_games_with_analysis']}")
        
        if analysis_report['total_games_found'] > 0:
            analysis_rate = (analysis_report['total_games_with_analysis'] / analysis_report['total_games_found']) * 100
            lines.append(f"Analysis completion rate: {analysis_rate:.1f}%")
        
        lines.append("")
        
        # Daily breakdown
        lines.append("DAILY BREAKDOWN")
        lines.append("-" * 40)
        
        for date_str, daily_report in analysis_report['daily_reports'].items():
            status_emoji = "✅" if daily_report['status'] == 'complete' else "⚠️" if daily_report['status'] == 'incomplete' else "❌"
            
            lines.append(f"{date_str}: {status_emoji} {daily_report['status'].upper()}")
            lines.append(f"  Games: {daily_report['total_games']}")
            lines.append(f"  With analysis: {daily_report['games_with_analysis']}")
            lines.append(f"  Final scores: {daily_report['games_with_final_scores']}")
            lines.append(f"  Pending: {daily_report['games_pending']}")
            
            if daily_report['data_quality']:
                dq = daily_report['data_quality']
                lines.append(f"  Completion: {dq['completion_rate']:.1f}%")
                lines.append(f"  Analysis: {dq['analysis_rate']:.1f}%")
                lines.append(f"  Predictions: {dq['prediction_completeness']:.1f}%")
                lines.append(f"  Pitchers: {dq['pitcher_data_completeness']:.1f}%")
            
            if daily_report['issues']:
                lines.append(f"  Issues: {len(daily_report['issues'])}")
                for issue in daily_report['issues'][:3]:  # Show first 3 issues
                    lines.append(f"    - {issue}")
                if len(daily_report['issues']) > 3:
                    lines.append(f"    ... and {len(daily_report['issues']) - 3} more")
            
            lines.append("")
        
        # Recommendations
        if analysis_report['recommendations']:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 40)
            for rec in analysis_report['recommendations']:
                lines.append(f"• {rec}")
            lines.append("")
        
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
    """Main function to run historical analysis completeness check"""
    
    checker = HistoricalAnalysisCompletenessChecker()
    
    # Check last 7 days through yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
    
    print(f"\n📊 Historical Analysis Completeness Checker")
    print(f"Checking dates: {week_ago} to {yesterday}")
    print("=" * 60)
    
    # Note: This requires the Flask app to be running
    print("⚠️  Note: Make sure your Flask app is running on localhost:5000")
    print("")
    
    try:
        # Run the check
        report = checker.check_date_range_completeness(week_ago, yesterday)
        
        # Generate and display report
        report_content = checker.generate_report(report)
        
        print("\n" + "=" * 60)
        print("SUMMARY RESULTS:")
        print("=" * 60)
        
        # Display key findings
        print(f"Dates checked: {report['dates_checked']}")
        print(f"Complete dates: {report['dates_complete']}")
        print(f"Incomplete dates: {report['dates_incomplete']}")
        print(f"Missing dates: {report['dates_missing']}")
        
        if report['total_games_found'] > 0:
            analysis_rate = (report['total_games_with_analysis'] / report['total_games_found']) * 100
            print(f"Overall analysis rate: {analysis_rate:.1f}%")
        
        # Show recommendations
        if report['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['recommendations'][:5]:  # Show first 5
                print(f"  {rec}")
        
        print(f"\n📝 Detailed report saved.")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        logger.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()
