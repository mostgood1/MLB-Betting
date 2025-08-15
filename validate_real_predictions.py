#!/usr/bin/env python3
"""
Real Prediction Data Validation and Analysis
============================================

Comprehensive analysis of our newly generated REAL predictions
to confirm quality improvements and eliminate placeholder data.
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import statistics
import sys

def load_prediction_cache():
    """Load the unified predictions cache"""
    cache_path = "unified_predictions_cache.json"
    if not os.path.exists(cache_path):
        print(f"❌ Cache file not found: {cache_path}")
        return None
    
    with open(cache_path, 'r') as f:
        return json.load(f)

def analyze_score_distribution(data):
    """Analyze score distribution to detect patterns"""
    print("\n📊 SCORE DISTRIBUTION ANALYSIS")
    print("=" * 50)
    
    all_away_scores = []
    all_home_scores = []
    score_pairs = []
    
    for date_key, date_data in data.items():
        if isinstance(date_data, dict) and 'games' in date_data:
            games = date_data['games']
            print(f"\n📅 {date_key}: {len(games)} games")
            
            date_away_scores = []
            date_home_scores = []
            
            for game in games:
                if 'away_score' in game and 'home_score' in game:
                    away_score = float(game['away_score'])
                    home_score = float(game['home_score'])
                    
                    all_away_scores.append(away_score)
                    all_home_scores.append(home_score)
                    date_away_scores.append(away_score)
                    date_home_scores.append(home_score)
                    
                    score_pair = f"{away_score:.1f}-{home_score:.1f}"
                    score_pairs.append(score_pair)
            
            # Date-specific stats
            if date_away_scores:
                print(f"  📈 Away scores: {min(date_away_scores):.1f} to {max(date_away_scores):.1f} (avg: {statistics.mean(date_away_scores):.1f})")
                print(f"  📈 Home scores: {min(date_home_scores):.1f} to {max(date_home_scores):.1f} (avg: {statistics.mean(date_home_scores):.1f})")
                
                # Check for suspicious patterns
                unique_away = len(set(date_away_scores))
                unique_home = len(set(date_home_scores))
                print(f"  🎯 Score variety: {unique_away} unique away, {unique_home} unique home")
                
                if unique_away == 1 and unique_home == 1:
                    print(f"  ⚠️  SUSPICIOUS: All games have identical scores!")
                elif unique_away <= 2 and unique_home <= 2:
                    print(f"  ⚠️  WARNING: Very low score variety")
    
    # Overall statistics
    if all_away_scores:
        print(f"\n🎯 OVERALL STATISTICS")
        print(f"  📊 Total games analyzed: {len(all_away_scores)}")
        print(f"  📈 Away scores: {min(all_away_scores):.1f} to {max(all_away_scores):.1f} (avg: {statistics.mean(all_away_scores):.1f})")
        print(f"  📈 Home scores: {min(all_home_scores):.1f} to {max(all_home_scores):.1f} (avg: {statistics.mean(all_home_scores):.1f})")
        
        # Score pair frequency
        score_counter = Counter(score_pairs)
        most_common = score_counter.most_common(5)
        print(f"\n🔍 MOST COMMON SCORE PAIRS:")
        for score_pair, count in most_common:
            percentage = (count / len(score_pairs)) * 100
            print(f"  {score_pair}: {count} times ({percentage:.1f}%)")
            
        # Check for problematic patterns
        if score_counter.most_common(1)[0][1] > len(score_pairs) * 0.5:
            print(f"  ⚠️  WARNING: Over 50% of games have the same score!")
        elif score_counter.most_common(1)[0][1] > len(score_pairs) * 0.3:
            print(f"  ⚠️  CAUTION: Over 30% of games have the same score")
        else:
            print(f"  ✅ Good score distribution - no dominant patterns")

def analyze_pitcher_data(data):
    """Analyze starting pitcher data quality"""
    print("\n🥎 STARTING PITCHER ANALYSIS")
    print("=" * 50)
    
    total_games = 0
    games_with_pitchers = 0
    unique_pitchers = set()
    pitcher_frequencies = Counter()
    
    for date_key, date_data in data.items():
        if isinstance(date_data, dict) and 'games' in date_data:
            games = date_data['games']
            print(f"\n📅 {date_key}: {len(games)} games")
            
            date_pitchers = []
            
            for game in games:
                total_games += 1
                
                away_pitcher = game.get('away_pitcher', '').strip()
                home_pitcher = game.get('home_pitcher', '').strip()
                
                if away_pitcher and home_pitcher:
                    games_with_pitchers += 1
                    unique_pitchers.add(away_pitcher)
                    unique_pitchers.add(home_pitcher)
                    pitcher_frequencies[away_pitcher] += 1
                    pitcher_frequencies[home_pitcher] += 1
                    date_pitchers.extend([away_pitcher, home_pitcher])
                    
                    teams = f"{game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}"
                    print(f"  🏈 {teams}")
                    print(f"    Pitchers: {away_pitcher} vs {home_pitcher}")
                else:
                    print(f"  ❌ Missing pitcher data: {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}")
    
    print(f"\n🎯 PITCHER DATA SUMMARY")
    print(f"  📊 Total games: {total_games}")
    print(f"  ✅ Games with pitcher data: {games_with_pitchers} ({(games_with_pitchers/total_games*100):.1f}%)")
    print(f"  👥 Unique pitchers: {len(unique_pitchers)}")
    
    # Check for realistic pitcher names
    realistic_pitchers = [p for p in unique_pitchers if ' ' in p and len(p) > 5]
    print(f"  🎯 Realistic pitcher names: {len(realistic_pitchers)} ({(len(realistic_pitchers)/len(unique_pitchers)*100):.1f}%)")
    
    # Most frequent pitchers (could indicate repeats across dates)
    print(f"\n🔄 MOST FREQUENT PITCHERS:")
    for pitcher, count in pitcher_frequencies.most_common(10):
        print(f"  {pitcher}: {count} appearances")

def analyze_win_probabilities(data):
    """Analyze win probability distributions"""
    print("\n🎲 WIN PROBABILITY ANALYSIS")
    print("=" * 50)
    
    all_away_probs = []
    all_home_probs = []
    
    for date_key, date_data in data.items():
        if isinstance(date_data, dict) and 'games' in date_data:
            games = date_data['games']
            
            for game in games:
                if 'away_win_prob' in game and 'home_win_prob' in game:
                    away_prob = float(game['away_win_prob'])
                    home_prob = float(game['home_win_prob'])
                    
                    all_away_probs.append(away_prob)
                    all_home_probs.append(home_prob)
                    
                    # Check if probabilities sum to ~100%
                    total_prob = away_prob + home_prob
                    if abs(total_prob - 100) > 1:
                        teams = f"{game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}"
                        print(f"  ⚠️  Probability sum error: {teams} = {total_prob:.1f}%")
    
    if all_away_probs:
        print(f"\n📊 PROBABILITY STATISTICS")
        print(f"  📈 Away win prob: {min(all_away_probs):.1f}% to {max(all_away_probs):.1f}% (avg: {statistics.mean(all_away_probs):.1f}%)")
        print(f"  📈 Home win prob: {min(all_home_probs):.1f}% to {max(all_home_probs):.1f}% (avg: {statistics.mean(all_home_probs):.1f}%)")
        
        # Check for realistic distribution
        balanced_games = sum(1 for p in all_away_probs if 40 <= p <= 60)
        print(f"  ⚖️  Balanced games (40-60% prob): {balanced_games}/{len(all_away_probs)} ({(balanced_games/len(all_away_probs)*100):.1f}%)")

def check_data_authenticity(data):
    """Check for signs of synthetic vs real data"""
    print("\n🔍 DATA AUTHENTICITY CHECK")
    print("=" * 50)
    
    # Check for obviously synthetic patterns
    suspicious_patterns = []
    
    for date_key, date_data in data.items():
        if isinstance(date_data, dict) and 'games' in date_data:
            games = date_data['games']
            
            # Check for identical scores
            scores = [(float(g.get('away_score', 0)), float(g.get('home_score', 0))) for g in games if 'away_score' in g]
            if len(set(scores)) == 1 and len(scores) > 1:
                suspicious_patterns.append(f"{date_key}: All {len(scores)} games have identical scores {scores[0]}")
            
            # Check for obviously fake scores (like exactly 4.0-4.0)
            perfect_fours = [s for s in scores if s == (4.0, 4.0)]
            if len(perfect_fours) > len(scores) * 0.5:
                suspicious_patterns.append(f"{date_key}: {len(perfect_fours)}/{len(scores)} games are exactly 4.0-4.0")
            
            # Check for placeholder pitcher names
            placeholder_pitchers = 0
            for game in games:
                away_pitcher = game.get('away_pitcher', '')
                home_pitcher = game.get('home_pitcher', '')
                if 'placeholder' in away_pitcher.lower() or 'placeholder' in home_pitcher.lower():
                    placeholder_pitchers += 1
                if away_pitcher == 'N/A' or home_pitcher == 'N/A':
                    placeholder_pitchers += 1
            
            if placeholder_pitchers > 0:
                suspicious_patterns.append(f"{date_key}: {placeholder_pitchers} games have placeholder pitchers")
    
    if suspicious_patterns:
        print("⚠️  SUSPICIOUS PATTERNS DETECTED:")
        for pattern in suspicious_patterns:
            print(f"  {pattern}")
    else:
        print("✅ No obvious synthetic data patterns detected!")

def main():
    """Run comprehensive prediction data analysis"""
    print("🎯 REAL PREDICTION DATA VALIDATION")
    print("=" * 60)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    data = load_prediction_cache()
    if not data:
        return
    
    print(f"\n📊 Loaded {len(data)} date entries")
    
    # Run all analyses
    analyze_score_distribution(data)
    analyze_pitcher_data(data)
    analyze_win_probabilities(data)
    check_data_authenticity(data)
    
    print(f"\n🎯 ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
