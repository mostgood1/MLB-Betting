#!/usr/bin/env python3
"""
Fix betting recommendations by generating proper format for today's games
"""

import json
import os
from datetime import datetime

def generate_betting_recommendations():
    """Generate proper betting recommendations for today's games"""
    
    # Load today's games from cache
    cache_file = "data/unified_predictions_cache.json"
    if not os.path.exists(cache_file):
        print(f"❌ Cache file not found: {cache_file}")
        return
    
    with open(cache_file, 'r') as f:
        cache = json.load(f)
    
    print(f"🔍 Available cache keys: {list(cache.keys())[:10]}")
    
    # Check if 2025-08-15 is in predictions_by_date or at top level
    today = "2025-08-15"
    if today in cache:
        games_data = cache[today]
    elif "predictions_by_date" in cache and today in cache["predictions_by_date"]:
        games_data = cache["predictions_by_date"][today]
    else:
        print(f"❌ No games found for {today}")
        print(f"🔍 Available dates: {[k for k in cache.keys() if '2025' in str(k)]}")
        if "predictions_by_date" in cache:
            print(f"🔍 Dates in predictions_by_date: {list(cache['predictions_by_date'].keys())}")
        return
    games = games_data.get("games", {})
    print(f"📅 Found {len(games)} games for {today}")
    
    # Create new format betting recommendations
    betting_recommendations = {
        "games": {},
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "format_version": "2.0",
            "description": "Dynamic betting recommendations with proper team names"
        }
    }
    
    for game_key, game in games.items():
        away_team = game.get('away_team', '')
        home_team = game.get('home_team', '')
        
        # Get win probabilities (convert to percentage)
        away_prob = game.get('away_win_probability', 0.5) * 100
        home_prob = game.get('home_win_probability', 0.5) * 100
        
        # Determine which team to recommend based on probability
        if away_prob > home_prob:
            recommended_team = away_team
            confidence = min(away_prob, 85.0)  # Cap at 85% for realism
        else:
            recommended_team = home_team
            confidence = min(home_prob, 85.0)
        
        # Only recommend if confidence is above 55%
        moneyline_rec = None
        if confidence > 55:
            moneyline_rec = {
                "pick": "away" if away_prob > home_prob else "home",
                "team": recommended_team,
                "confidence": round(confidence, 1),
                "reason": f"Model predicts {recommended_team} with {confidence:.1f}% confidence",
                "odds": f"+{int((100/(confidence/100)) - 100)}" if confidence < 70 else f"-{int(((confidence/100)/(1-confidence/100)) * 100)}"
            }
        
        # Create total runs recommendation
        predicted_total = game.get('predicted_total_runs', 8.5)
        market_total = game.get('market_total_line', 8.5)  # Use actual market line if available
        
        total_rec = None
        if abs(predicted_total - market_total) > 0.5:
            pick = "over" if predicted_total > market_total else "under"
            total_confidence = min(65 + abs(predicted_total - market_total) * 10, 80)
            total_rec = {
                "pick": pick,
                "line": market_total,
                "confidence": round(total_confidence, 1),
                "predicted_total": round(predicted_total, 1),
                "reason": f"Model predicts {predicted_total:.1f} runs vs market {market_total}"
            }
        
        # Build game recommendations
        game_betting = {
            "away_team": away_team,
            "home_team": home_team,
            "away_pitcher": game.get('away_pitcher', 'TBD'),
            "home_pitcher": game.get('home_pitcher', 'TBD'),
            "market_total_line": market_total,
            "predicted_total_runs": round(predicted_total, 1),
            "market_vs_prediction": round(predicted_total - market_total, 1),
            "win_probabilities": {
                "away": round(away_prob, 1),
                "home": round(home_prob, 1)
            },
            "betting_recommendations": {
                "moneyline": moneyline_rec,
                "total_runs": total_rec
            },
            "overall_confidence": round(max(confidence if moneyline_rec else 0, total_confidence if total_rec else 0), 1),
            "market_alignment": "favorable" if (moneyline_rec or total_rec) else "neutral"
        }
        
        betting_recommendations["games"][game_key] = game_betting
        print(f"✅ Generated recommendations for {game_key}")
        if moneyline_rec:
            print(f"   🎯 Moneyline: {moneyline_rec['team']} ({moneyline_rec['confidence']}%)")
        if total_rec:
            print(f"   📊 Total: {total_rec['pick']} {total_rec['line']} ({total_rec['confidence']}%)")
    
    # Save the new betting recommendations
    output_file = f"data/betting_recommendations_{today.replace('-', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump(betting_recommendations, f, indent=2)
    
    print(f"\n🎉 Generated {len(betting_recommendations['games'])} game recommendations")
    print(f"💾 Saved to {output_file}")
    
    # Also remove the backup file to prevent confusion
    backup_file = f"{output_file}.backup"
    if os.path.exists(backup_file):
        os.remove(backup_file)
        print(f"🗑️  Removed problematic backup file")

if __name__ == "__main__":
    print("🔧 Fixing betting recommendations...")
    generate_betting_recommendations()
    print("✅ Done!")
