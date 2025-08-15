#!/usr/bin/env python3
"""
Comprehensive Dashboard Data Generator
====================================

Generate comprehensive statistics from all our prediction data
starting from August 7th for the main dashboard.
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

def generate_comprehensive_dashboard_stats():
    """Generate comprehensive dashboard statistics from all data"""
    
    print("📊 GENERATING COMPREHENSIVE DASHBOARD STATISTICS")
    print("=" * 60)
    
    # Load the unified cache
    with open('unified_predictions_cache.json', 'r') as f:
        data = json.load(f)
    
    predictions_data = data.get('predictions_by_date', data)
    
    # Initialize comprehensive stats
    total_games = 0
    total_dates = 0
    premium_predictions = 0
    high_confidence_games = 0
    
    # Score and performance tracking
    all_scores = []
    win_probabilities = []
    sources = Counter()
    dates_with_data = []
    
    # Team performance tracking
    team_stats = defaultdict(lambda: {'games': 0, 'avg_score': 0, 'total_score': 0})
    pitcher_stats = Counter()  # Use Counter instead of defaultdict
    
    # Date range analysis
    start_date = datetime(2025, 8, 7)  # Our data starts from Aug 7th
    
    print(f"📅 Processing data from August 7th onwards...")
    
    for date_str, date_data in predictions_data.items():
        if 'games' not in date_data:
            continue
            
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj < start_date:
                continue  # Skip dates before Aug 7th
        except:
            continue
        
        dates_with_data.append(date_str)
        total_dates += 1
        
        games = date_data['games']
        games_list = []
        
        # Handle both dict and list formats
        if isinstance(games, dict):
            games_list = list(games.values())
        elif isinstance(games, list):
            games_list = games
        
        date_games = len(games_list)
        total_games += date_games
        
        print(f"   📅 {date_str}: {date_games} games")
        
        # Process each game
        for game in games_list:
            if not isinstance(game, dict):
                continue
                
            # Count sources
            source = game.get('source', 'unknown')
            sources[source] += 1
            
            # Score analysis
            if 'predicted_away_score' in game and 'predicted_home_score' in game:
                away_score = float(game['predicted_away_score'])
                home_score = float(game['predicted_home_score'])
                total_score = away_score + home_score
                all_scores.append(total_score)
                
                # Team stats
                away_team = game.get('away_team', '').replace('_', ' ')
                home_team = game.get('home_team', '').replace('_', ' ')
                
                if away_team:
                    team_stats[away_team]['games'] += 1
                    team_stats[away_team]['total_score'] += away_score
                    team_stats[away_team]['avg_score'] = team_stats[away_team]['total_score'] / team_stats[away_team]['games']
                
                if home_team:
                    team_stats[home_team]['games'] += 1
                    team_stats[home_team]['total_score'] += home_score
                    team_stats[home_team]['avg_score'] = team_stats[home_team]['total_score'] / team_stats[home_team]['games']
            
            # Win probability analysis
            if 'away_win_probability' in game:
                away_prob = float(game['away_win_probability'])
                home_prob = float(game.get('home_win_probability', 100 - away_prob))
                
                # Convert to 0-100 scale if needed
                if away_prob <= 1:
                    away_prob *= 100
                if home_prob <= 1:
                    home_prob *= 100
                
                max_prob = max(away_prob, home_prob)
                win_probabilities.append(max_prob)
                
                # Count premium predictions
                if max_prob > 60:
                    premium_predictions += 1
                if max_prob > 70:
                    high_confidence_games += 1
            
            # Pitcher tracking
            away_pitcher = game.get('away_pitcher', '')
            home_pitcher = game.get('home_pitcher', '')
            if away_pitcher and away_pitcher != 'TBD':
                pitcher_stats[away_pitcher] += 1
            if home_pitcher and home_pitcher != 'TBD':
                pitcher_stats[home_pitcher] += 1
    
    # Calculate comprehensive statistics
    print(f"\n📊 COMPREHENSIVE STATISTICS SUMMARY")
    print("-" * 40)
    
    dashboard_stats = {
        'total_games': total_games,
        'total_dates': total_dates,
        'date_range': {
            'start': '2025-08-07',
            'end': max(dates_with_data) if dates_with_data else '2025-08-07',
            'dates_with_data': len(dates_with_data)
        },
        'prediction_quality': {
            'premium_predictions': premium_predictions,
            'high_confidence_games': high_confidence_games,
            'premium_percentage': round((premium_predictions / total_games * 100), 1) if total_games > 0 else 0,
            'high_confidence_percentage': round((high_confidence_games / total_games * 100), 1) if total_games > 0 else 0
        },
        'score_analysis': {
            'avg_total_runs': round(statistics.mean(all_scores), 1) if all_scores else 0,
            'min_total_runs': round(min(all_scores), 1) if all_scores else 0,
            'max_total_runs': round(max(all_scores), 1) if all_scores else 0,
            'games_with_scores': len(all_scores)
        },
        'data_sources': dict(sources),
        'team_coverage': len(team_stats),
        'unique_pitchers': len(pitcher_stats),
        'top_teams_by_games': sorted([(team, stats['games']) for team, stats in team_stats.items()], 
                                   key=lambda x: x[1], reverse=True)[:10],
        'most_common_pitchers': [(pitcher, count) for pitcher, count in pitcher_stats.most_common(10)],
        'data_freshness': {
            'last_update': datetime.now().isoformat(),
            'days_of_data': len(dates_with_data),
            'most_recent_date': max(dates_with_data) if dates_with_data else 'N/A'
        }
    }
    
    # Print summary
    print(f"📊 Total Games: {dashboard_stats['total_games']}")
    print(f"📅 Date Range: {dashboard_stats['date_range']['start']} to {dashboard_stats['date_range']['end']}")
    print(f"🎯 Premium Predictions: {dashboard_stats['prediction_quality']['premium_predictions']} ({dashboard_stats['prediction_quality']['premium_percentage']}%)")
    print(f"⚡ High Confidence: {dashboard_stats['prediction_quality']['high_confidence_games']} ({dashboard_stats['prediction_quality']['high_confidence_percentage']}%)")
    print(f"📈 Avg Total Runs: {dashboard_stats['score_analysis']['avg_total_runs']}")
    print(f"🏟️ Teams Covered: {dashboard_stats['team_coverage']}")
    print(f"⚾ Unique Pitchers: {dashboard_stats['unique_pitchers']}")
    
    print(f"\n📊 Data Sources:")
    for source, count in dashboard_stats['data_sources'].items():
        print(f"   {source}: {count} games")
    
    # Save dashboard stats
    with open('dashboard_comprehensive_stats.json', 'w') as f:
        json.dump(dashboard_stats, f, indent=2)
    
    print(f"\n💾 Dashboard stats saved to: dashboard_comprehensive_stats.json")
    return dashboard_stats

if __name__ == "__main__":
    generate_comprehensive_dashboard_stats()
