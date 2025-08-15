#!/usr/bin/env python3
"""
Daily UltraFastSimEngine Prediction Generator
===========================================
Runs UltraFastSimEngine once per day to generate hardcoded predictions.
These predictions are then used for betting recommendations and frontend display.

Usage: python daily_ultrafastengine_predictions.py
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path

# Add the MLB-Betting engines to path
sys.path.append(str(Path(__file__).parent / "MLB-Betting"))
from engines.ultra_fast_engine import UltraFastSimEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'daily_predictions_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyPredictionGenerator:
    """Daily prediction generator using UltraFastSimEngine"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.base_dir = Path(__file__).parent
        self.mlb_betting_dir = self.base_dir / "MLB-Betting"
        
        # Initialize UltraFastSimEngine
        try:
            self.engine = UltraFastSimEngine()
            logger.info("✅ UltraFastSimEngine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize UltraFastSimEngine: {e}")
            raise
        
        # File paths
        self.unified_cache_path = self.mlb_betting_dir / "data" / "unified_predictions_cache.json"
        self.betting_lines_path = self.mlb_betting_dir / "data" / f"real_betting_lines_{self.today.replace('-', '_')}.json"
        self.betting_recs_path = self.mlb_betting_dir / "data" / f"betting_recommendations_{self.today.replace('-', '_')}.json"
    
    def fetch_todays_games(self):
        """Fetch today's games from MLB API with starting pitchers"""
        logger.info(f"🔄 Fetching games for {self.today}")
        
        url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={self.today}&hydrate=team,probablePitcher'
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            games = []
            if 'dates' in data and data['dates']:
                for game in data['dates'][0]['games']:
                    away_team = game['teams']['away']['team']['name']
                    home_team = game['teams']['home']['team']['name']
                    
                    # Get starting pitchers
                    away_pitcher = 'TBD'
                    home_pitcher = 'TBD'
                    
                    if 'probablePitcher' in game['teams']['away']:
                        away_pitcher = game['teams']['away']['probablePitcher']['fullName']
                    if 'probablePitcher' in game['teams']['home']:
                        home_pitcher = game['teams']['home']['probablePitcher']['fullName']
                    
                    game_info = {
                        'game_id': game.get('gamePk'),
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_pitcher': away_pitcher,
                        'home_pitcher': home_pitcher,
                        'game_time': game.get('gameDate'),
                        'date': self.today
                    }
                    games.append(game_info)
            
            logger.info(f"✅ Found {len(games)} games for {self.today}")
            return games
            
        except Exception as e:
            logger.error(f"❌ Error fetching games: {e}")
            return []
    
    def generate_predictions(self, games):
        """Generate predictions using UltraFastSimEngine"""
        logger.info(f"🎯 Generating predictions for {len(games)} games")
        
        predictions = {}
        
        for game in games:
            away_team = game['away_team']
            home_team = game['home_team']
            away_pitcher = game['away_pitcher']
            home_pitcher = game['home_pitcher']
            
            logger.info(f"  🎲 Simulating: {away_team} ({away_pitcher}) @ {home_team} ({home_pitcher})")
            
            try:
                # Run 5000 simulations for this game
                results, metadata = self.engine.simulate_game_vectorized(
                    away_team=away_team,
                    home_team=home_team,
                    sim_count=5000,
                    game_date=self.today,
                    away_pitcher=away_pitcher,
                    home_pitcher=home_pitcher
                )
                
                # Calculate statistics
                away_wins = sum(1 for r in results if not r.home_wins)
                total_sims = len(results)
                away_win_prob = away_wins / total_sims
                home_win_prob = 1 - away_win_prob
                
                avg_away_score = sum(r.away_score for r in results) / total_sims
                avg_home_score = sum(r.home_score for r in results) / total_sims
                avg_total_runs = sum(r.total_runs for r in results) / total_sims
                
                # Determine winner
                if away_win_prob > home_win_prob:
                    predicted_winner = away_team
                    confidence = round(away_win_prob * 100, 1)
                else:
                    predicted_winner = home_team
                    confidence = round(home_win_prob * 100, 1)
                
                # Build prediction
                game_key = f"{away_team} @ {home_team}"
                prediction = {
                    'away_team': away_team,
                    'home_team': home_team,
                    'predicted_away_score': round(avg_away_score, 1),
                    'predicted_home_score': round(avg_home_score, 1),
                    'predicted_total_runs': round(avg_total_runs, 1),
                    'away_win_probability': round(away_win_prob, 3),
                    'home_win_probability': round(home_win_prob, 3),
                    'away_pitcher': away_pitcher,
                    'home_pitcher': home_pitcher,
                    'model_version': 'UltraFastSimEngine_5000sims',
                    'source': 'daily_hardcoded',
                    'prediction_time': datetime.now().isoformat(),
                    'game_id': str(game['game_id']),
                    'game_time': game['game_time'],
                    'date': self.today,
                    'has_real_results': False,
                    'comprehensive_details': {
                        'winner_prediction': {
                            'predicted_winner': predicted_winner,
                            'confidence': confidence
                        },
                        'score_prediction': {
                            'away_score': round(avg_away_score, 1),
                            'home_score': round(avg_home_score, 1),
                            'total_runs': round(avg_total_runs, 1)
                        },
                        'betting_analysis': {
                            'recommendation': 'Generated',
                            'confidence_level': 'High' if confidence > 60 else 'Medium'
                        }
                    }
                }
                
                predictions[game_key] = prediction
                logger.info(f"    ✅ {predicted_winner} ({confidence}%) - {avg_away_score:.1f} vs {avg_home_score:.1f}")
                
            except Exception as e:
                logger.error(f"    ❌ Error simulating {away_team} @ {home_team}: {e}")
                continue
        
        logger.info(f"✅ Generated {len(predictions)} predictions")
        return predictions
    
    def update_unified_cache(self, predictions):
        """Update the unified predictions cache"""
        logger.info(f"📝 Updating unified cache with {len(predictions)} predictions")
        
        try:
            # Load existing cache
            cache = {}
            if self.unified_cache_path.exists():
                with open(self.unified_cache_path, 'r') as f:
                    cache = json.load(f)
            
            # Ensure structure exists
            if 'predictions_by_date' not in cache:
                cache['predictions_by_date'] = {}
            
            # Update metadata
            cache['metadata'] = {
                'last_updated': datetime.now().isoformat(),
                'last_daily_generation': datetime.now().isoformat(),
                'daily_generation_date': self.today,
                'daily_generation_games': len(predictions),
                'model_version': 'UltraFastSimEngine_5000sims',
                'source': 'daily_hardcoded_predictions'
            }
            
            # Add today's predictions
            cache['predictions_by_date'][self.today] = {
                'date': self.today,
                'games_count': len(predictions),
                'last_updated': datetime.now().isoformat(),
                'games': predictions
            }
            
            # Save updated cache
            with open(self.unified_cache_path, 'w') as f:
                json.dump(cache, f, indent=2)
            
            logger.info(f"✅ Unified cache updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error updating unified cache: {e}")
            raise
    
    def generate_betting_recommendations(self, predictions):
        """Generate betting recommendations based on predictions"""
        logger.info(f"💰 Generating betting recommendations")
        
        try:
            # Load real betting lines if available
            real_lines = {}
            if self.betting_lines_path.exists():
                with open(self.betting_lines_path, 'r') as f:
                    betting_data = json.load(f)
                    real_lines = betting_data.get('lines', {})
            
            recommendations = {
                'generation_date': datetime.now().isoformat(),
                'date': self.today,
                'total_games': len(predictions),
                'betting_recommendations': {
                    'moneyline': [],
                    'total_runs': []
                }
            }
            
            for game_key, prediction in predictions.items():
                # Moneyline recommendations
                away_prob = prediction['away_win_probability']
                home_prob = prediction['home_win_probability']
                
                if away_prob > 0.6:
                    recommendations['betting_recommendations']['moneyline'].append({
                        'game': game_key,
                        'pick': prediction['away_team'],
                        'confidence': round(away_prob * 100, 1),
                        'type': 'Moneyline'
                    })
                elif home_prob > 0.6:
                    recommendations['betting_recommendations']['moneyline'].append({
                        'game': game_key,
                        'pick': prediction['home_team'],
                        'confidence': round(home_prob * 100, 1),
                        'type': 'Moneyline'
                    })
                
                # Total runs recommendations
                predicted_total = prediction['predicted_total_runs']
                if game_key in real_lines:
                    market_total = real_lines[game_key].get('total_runs', {}).get('line', 9.5)
                    if abs(predicted_total - market_total) > 0.5:
                        pick = 'Over' if predicted_total > market_total else 'Under'
                        recommendations['betting_recommendations']['total_runs'].append({
                            'game': game_key,
                            'pick': f"{pick} {market_total}",
                            'predicted_total': predicted_total,
                            'market_line': market_total,
                            'edge': abs(predicted_total - market_total),
                            'type': 'Total'
                        })
            
            # Save recommendations
            with open(self.betting_recs_path, 'w') as f:
                json.dump(recommendations, f, indent=2)
            
            ml_count = len(recommendations['betting_recommendations']['moneyline'])
            total_count = len(recommendations['betting_recommendations']['total_runs'])
            logger.info(f"✅ Generated {ml_count} ML picks and {total_count} total picks")
            
        except Exception as e:
            logger.error(f"❌ Error generating betting recommendations: {e}")
    
    def run_daily_predictions(self):
        """Main function to run daily predictions"""
        logger.info(f"🚀 Starting daily prediction generation for {self.today}")
        
        try:
            # Step 1: Fetch today's games
            games = self.fetch_todays_games()
            if not games:
                logger.error("❌ No games found, aborting")
                return False
            
            # Step 2: Generate predictions using UltraFastSimEngine
            predictions = self.generate_predictions(games)
            if not predictions:
                logger.error("❌ No predictions generated, aborting")
                return False
            
            # Step 3: Update unified cache
            self.update_unified_cache(predictions)
            
            # Step 4: Generate betting recommendations
            self.generate_betting_recommendations(predictions)
            
            logger.info(f"🎉 Daily prediction generation complete!")
            logger.info(f"   Generated: {len(predictions)} predictions")
            logger.info(f"   Cache updated: {self.unified_cache_path}")
            logger.info(f"   Recommendations: {self.betting_recs_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Daily prediction generation failed: {e}")
            return False

if __name__ == "__main__":
    generator = DailyPredictionGenerator()
    success = generator.run_daily_predictions()
    sys.exit(0 if success else 1)
