#!/usr/bin/env python3
"""
MLB Betting Recommendations Engine
=================================

Generates comprehensive betting recommendations including:
- Moneyline picks
- Over/Under total runs recommendations
- Confidence ratings
- Auto-refresh when TBDs are resolved
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BettingRecommendationsEngine:
    def __init__(self):
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.betting_lines = {}
        self.recommendations = {}
        
    def fetch_current_betting_lines(self) -> Dict:
        """Fetch current betting lines (mock data - replace with real API)"""
        # This would typically connect to a sportsbook API
        # For now, using common lines
        
        default_lines = {
            'total_runs_line': 9.5,  # Common O/U line
            'moneyline_threshold': 0.55,  # Confidence threshold for picks
            'total_runs_threshold': 0.60,  # Confidence threshold for O/U
        }
        
        logger.info(f"🎯 Using betting lines: O/U {default_lines['total_runs_line']}")
        return default_lines
    
    def calculate_win_probability(self, predicted_away: float, predicted_home: float) -> Dict:
        """Calculate win probabilities from predicted scores"""
        total_score = predicted_away + predicted_home
        
        if total_score == 0:
            return {'away_prob': 0.5, 'home_prob': 0.5}
        
        away_prob = predicted_away / total_score
        home_prob = predicted_home / total_score
        
        # Apply sigmoid transformation for more realistic probabilities
        import math
        
        score_diff = predicted_away - predicted_home
        win_prob = 1 / (1 + math.exp(-score_diff * 0.5))
        
        return {
            'away_prob': round(win_prob, 3),
            'home_prob': round(1 - win_prob, 3)
        }
    
    def generate_betting_recommendations(self) -> Dict:
        """Generate comprehensive betting recommendations"""
        
        logger.info(f"🎯 Generating betting recommendations for {self.current_date}")
        
        # Load current predictions
        try:
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                predictions_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading predictions: {e}")
            return {}
        
        # Get betting lines
        lines = self.fetch_current_betting_lines()
        
        # Get today's games
        today_data = predictions_data.get('predictions_by_date', {}).get(self.current_date, {})
        if 'games' not in today_data:
            logger.warning(f"No games found for {self.current_date}")
            return {}
        
        games = today_data['games']
        recommendations = {
            'date': self.current_date,
            'generated_at': datetime.now().isoformat(),
            'betting_lines': lines,
            'games': {},
            'summary': {
                'total_games': len(games),
                'moneyline_picks': 0,
                'over_picks': 0,
                'under_picks': 0,
                'high_confidence_picks': 0
            }
        }
        
        logger.info(f"📊 Analyzing {len(games)} games for betting opportunities...")
        
        for game_key, game_data in games.items():
            away_team = game_data.get('away_team', '')
            home_team = game_data.get('home_team', '')
            away_pitcher = game_data.get('away_pitcher', 'TBD')
            home_pitcher = game_data.get('home_pitcher', 'TBD')
            
            pred_away_score = float(game_data.get('predicted_away_score', 0))
            pred_home_score = float(game_data.get('predicted_home_score', 0))
            pred_total_runs = float(game_data.get('predicted_total_runs', pred_away_score + pred_home_score))
            
            # Calculate win probabilities
            win_probs = self.calculate_win_probability(pred_away_score, pred_home_score)
            
            # Moneyline recommendation
            moneyline_pick = None
            moneyline_confidence = 0
            
            if win_probs['away_prob'] > lines['moneyline_threshold']:
                moneyline_pick = 'away'
                moneyline_confidence = win_probs['away_prob']
                recommendations['summary']['moneyline_picks'] += 1
            elif win_probs['home_prob'] > lines['moneyline_threshold']:
                moneyline_pick = 'home'
                moneyline_confidence = win_probs['home_prob']
                recommendations['summary']['moneyline_picks'] += 1
            
            # Over/Under recommendation
            total_runs_line = lines['total_runs_line']
            ou_pick = None
            ou_confidence = 0
            
            if pred_total_runs > total_runs_line:
                ou_pick = 'over'
                ou_confidence = min(0.95, (pred_total_runs - total_runs_line) / total_runs_line + 0.5)
                if ou_confidence > lines['total_runs_threshold']:
                    recommendations['summary']['over_picks'] += 1
            else:
                ou_pick = 'under'
                ou_confidence = min(0.95, (total_runs_line - pred_total_runs) / total_runs_line + 0.5)
                if ou_confidence > lines['total_runs_threshold']:
                    recommendations['summary']['under_picks'] += 1
            
            # Overall confidence rating
            has_tbds = (away_pitcher == 'TBD' or home_pitcher == 'TBD')
            confidence_penalty = 0.1 if has_tbds else 0
            
            overall_confidence = max(moneyline_confidence, ou_confidence) - confidence_penalty
            
            if overall_confidence > 0.7:
                recommendations['summary']['high_confidence_picks'] += 1
            
            # Game recommendation
            game_rec = {
                'away_team': away_team,
                'home_team': home_team,
                'away_pitcher': away_pitcher,
                'home_pitcher': home_pitcher,
                'has_tbd_pitchers': has_tbds,
                'predicted_score': f"{pred_away_score}-{pred_home_score}",
                'predicted_total_runs': pred_total_runs,
                'win_probabilities': win_probs,
                'betting_recommendations': {
                    'moneyline': {
                        'pick': moneyline_pick,
                        'team': away_team if moneyline_pick == 'away' else home_team if moneyline_pick == 'home' else None,
                        'confidence': round(moneyline_confidence, 3)
                    },
                    'total_runs': {
                        'line': total_runs_line,
                        'pick': ou_pick,
                        'predicted_total': pred_total_runs,
                        'confidence': round(ou_confidence, 3)
                    }
                },
                'overall_confidence': round(overall_confidence, 3),
                'recommendation_quality': 'HIGH' if overall_confidence > 0.7 else 'MEDIUM' if overall_confidence > 0.5 else 'LOW'
            }
            
            recommendations['games'][game_key] = game_rec
            
            # Log recommendation
            ml_text = f"{moneyline_pick.upper()} ({moneyline_confidence:.1%})" if moneyline_pick else "PASS"
            ou_text = f"{ou_pick.upper()} {total_runs_line} ({ou_confidence:.1%})" if ou_pick else "PASS"
            tbd_warning = " [TBD PITCHERS]" if has_tbds else ""
            
            logger.info(f"{away_team} @ {home_team}: ML={ml_text}, O/U={ou_text}{tbd_warning}")
        
        # Save recommendations
        with open(f'data/betting_recommendations_{self.current_date.replace("-", "_")}.json', 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        logger.info("📈 BETTING RECOMMENDATIONS SUMMARY:")
        logger.info(f"Total Games: {recommendations['summary']['total_games']}")
        logger.info(f"Moneyline Picks: {recommendations['summary']['moneyline_picks']}")
        logger.info(f"Over Picks: {recommendations['summary']['over_picks']}")
        logger.info(f"Under Picks: {recommendations['summary']['under_picks']}")
        logger.info(f"High Confidence: {recommendations['summary']['high_confidence_picks']}")
        
        return recommendations

def main():
    """Main function"""
    logger.info("🎯 MLB Betting Recommendations Engine Starting")
    
    engine = BettingRecommendationsEngine()
    recommendations = engine.generate_betting_recommendations()
    
    if recommendations:
        logger.info("✅ Betting recommendations generated successfully!")
        logger.info(f"💾 Saved to data/betting_recommendations_{engine.current_date.replace('-', '_')}.json")
    else:
        logger.error("❌ Failed to generate betting recommendations")

if __name__ == "__main__":
    main()
