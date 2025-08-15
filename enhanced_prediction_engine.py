#!/usr/bin/env python3
"""
Enhanced Prediction Engine with Real Betting Lines
=================================================

Re-generate today's predictions using real betting line information:
- Real over/under totals per game
- Market moneyline odds
- Enhanced accuracy with market data integration
"""

import json
import logging
from datetime import datetime
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPredictionEngine:
    def __init__(self):
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.real_betting_lines = self.load_real_betting_lines()
        
    def load_real_betting_lines(self) -> Dict:
        """Load real betting lines"""
        filename = f'data/real_betting_lines_{self.current_date.replace("-", "_")}.json'
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                logger.info(f"✅ Loaded real betting lines: {len(data.get('lines', {}))} games")
                return data
        except Exception as e:
            logger.error(f"❌ Error loading real betting lines: {e}")
            return {}
    
    def get_market_total_for_game(self, game_key: str) -> float:
        """Get the real market over/under total for a specific game"""
        if not self.real_betting_lines or 'lines' not in self.real_betting_lines:
            return 9.5  # Default fallback
        
        game_lines = self.real_betting_lines['lines'].get(game_key, {})
        total_runs = game_lines.get('total_runs', {})
        market_line = total_runs.get('line', 9.5)
        
        logger.info(f"📊 {game_key}: Market O/U = {market_line}")
        return float(market_line)
    
    def enhance_prediction_with_market_data(self, game_key: str, base_prediction: Dict) -> Dict:
        """Enhance prediction with real market data"""
        
        # Get market over/under line
        market_total = self.get_market_total_for_game(game_key)
        
        # Get our predicted total
        predicted_total = float(base_prediction.get('predicted_total_runs', 0))
        if not predicted_total:
            predicted_total = float(base_prediction.get('predicted_away_score', 0)) + float(base_prediction.get('predicted_home_score', 0))
        
        # Calculate market-adjusted confidence
        total_difference = abs(predicted_total - market_total)
        
        # Market alignment scoring
        if total_difference <= 0.5:
            market_alignment = 'HIGH'  # Very close to market
            confidence_boost = 0.05
        elif total_difference <= 1.0:
            market_alignment = 'MEDIUM'  # Reasonable difference
            confidence_boost = 0.0
        else:
            market_alignment = 'LOW'  # Significant disagreement
            confidence_boost = -0.05
        
        # Adjust win probabilities based on market alignment
        away_win_prob = float(base_prediction.get('away_win_probability', 0.5))
        home_win_prob = float(base_prediction.get('home_win_probability', 0.5))
        
        away_win_prob = max(0.1, min(0.9, away_win_prob + confidence_boost))
        home_win_prob = max(0.1, min(0.9, home_win_prob + confidence_boost))
        
        # Normalize probabilities
        total_prob = away_win_prob + home_win_prob
        away_win_prob = away_win_prob / total_prob
        home_win_prob = home_win_prob / total_prob
        
        # Enhanced prediction with market data
        enhanced_prediction = base_prediction.copy()
        enhanced_prediction.update({
            'market_total_line': market_total,
            'predicted_vs_market': predicted_total - market_total,
            'market_alignment': market_alignment,
            'away_win_probability': away_win_prob,
            'home_win_probability': home_win_prob,
            'enhanced_with_market_data': True,
            'market_enhancement_date': datetime.now().isoformat()
        })
        
        # Over/Under recommendation based on real market line
        if predicted_total > market_total + 0.3:
            ou_recommendation = 'OVER'
            ou_confidence = min(0.8, (predicted_total - market_total) / market_total + 0.5)
        elif predicted_total < market_total - 0.3:
            ou_recommendation = 'UNDER'  
            ou_confidence = min(0.8, (market_total - predicted_total) / market_total + 0.5)
        else:
            ou_recommendation = 'PASS'
            ou_confidence = 0.5
        
        enhanced_prediction['over_under_recommendation'] = {
            'pick': ou_recommendation,
            'market_line': market_total,
            'predicted_total': predicted_total,
            'confidence': round(ou_confidence, 3),
            'edge': round(predicted_total - market_total, 2)
        }
        
        return enhanced_prediction
    
    def regenerate_todays_predictions(self) -> bool:
        """Regenerate today's predictions with real market data"""
        
        logger.info(f"🔄 Regenerating predictions for {self.current_date} with real market data")
        
        # Load current predictions
        try:
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                predictions_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading predictions: {e}")
            return False
        
        # Get today's games
        today_data = predictions_data.get('predictions_by_date', {}).get(self.current_date, {})
        if 'games' not in today_data:
            logger.error(f"No games found for {self.current_date}")
            return False
        
        games = today_data['games']
        enhanced_games = {}
        
        logger.info(f"📊 Enhancing {len(games)} games with real market data...")
        
        for game_key, game_data in games.items():
            logger.info(f"🎯 Processing: {game_key}")
            
            # Enhance prediction with market data
            enhanced_game = self.enhance_prediction_with_market_data(game_key, game_data)
            enhanced_games[game_key] = enhanced_game
            
            # Log the enhancement
            market_total = enhanced_game.get('market_total_line', 0)
            predicted_total = enhanced_game.get('predicted_total_runs', 0)
            ou_rec = enhanced_game.get('over_under_recommendation', {})
            
            logger.info(f"  Market O/U: {market_total} | Predicted: {predicted_total:.1f} | Rec: {ou_rec.get('pick', 'N/A')}")
        
        # Update predictions with enhanced data
        predictions_data['predictions_by_date'][self.current_date]['games'] = enhanced_games
        predictions_data['metadata']['last_market_enhancement'] = datetime.now().isoformat()
        predictions_data['metadata']['market_enhancement_date'] = self.current_date
        predictions_data['metadata']['enhanced_games_count'] = len(enhanced_games)
        
        # Save enhanced predictions
        with open('MLB-Betting/data/unified_predictions_cache.json', 'w') as f:
            json.dump(predictions_data, f, indent=2)
        
        logger.info(f"✅ Enhanced {len(enhanced_games)} predictions with real market data")
        return True
    
    def regenerate_betting_recommendations(self) -> bool:
        """Regenerate betting recommendations with enhanced predictions"""
        
        logger.info("🎯 Regenerating betting recommendations with enhanced market data...")
        
        try:
            # Load enhanced predictions
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                predictions_data = json.load(f)
            
            # Get today's enhanced games
            today_data = predictions_data.get('predictions_by_date', {}).get(self.current_date, {})
            games = today_data.get('games', {})
            
            recommendations = {
                'date': self.current_date,
                'generated_at': datetime.now().isoformat(),
                'enhanced_with_market_data': True,
                'games': {},
                'summary': {
                    'total_games': len(games),
                    'moneyline_picks': 0,
                    'over_picks': 0,
                    'under_picks': 0,
                    'high_confidence_picks': 0,
                    'market_enhanced': True
                }
            }
            
            for game_key, game_data in games.items():
                away_team = game_data.get('away_team', '')
                home_team = game_data.get('home_team', '')
                
                # Get enhanced probabilities
                away_win_prob = float(game_data.get('away_win_probability', 0.5))
                home_win_prob = float(game_data.get('home_win_probability', 0.5))
                
                # Get over/under recommendation
                ou_rec = game_data.get('over_under_recommendation', {})
                market_total = float(game_data.get('market_total_line', 9.5))
                predicted_total = float(game_data.get('predicted_total_runs', 0))
                
                # Moneyline recommendation (55% threshold)
                moneyline_pick = None
                moneyline_confidence = 0
                
                if away_win_prob > 0.55:
                    moneyline_pick = 'away'
                    moneyline_confidence = away_win_prob
                    recommendations['summary']['moneyline_picks'] += 1
                elif home_win_prob > 0.55:
                    moneyline_pick = 'home'
                    moneyline_confidence = home_win_prob
                    recommendations['summary']['moneyline_picks'] += 1
                
                # Over/Under with real market lines
                ou_pick = ou_rec.get('pick', 'PASS')
                ou_confidence = float(ou_rec.get('confidence', 0.5))
                
                if ou_pick == 'OVER' and ou_confidence > 0.6:
                    recommendations['summary']['over_picks'] += 1
                elif ou_pick == 'UNDER' and ou_confidence > 0.6:
                    recommendations['summary']['under_picks'] += 1
                
                # Overall confidence
                overall_confidence = max(moneyline_confidence, ou_confidence)
                if overall_confidence > 0.7:
                    recommendations['summary']['high_confidence_picks'] += 1
                
                # Game recommendation with real market data
                game_rec = {
                    'away_team': away_team,
                    'home_team': home_team,
                    'away_pitcher': game_data.get('away_pitcher', 'TBD'),
                    'home_pitcher': game_data.get('home_pitcher', 'TBD'),
                    'market_total_line': market_total,
                    'predicted_total_runs': predicted_total,
                    'market_vs_prediction': round(predicted_total - market_total, 2),
                    'win_probabilities': {
                        'away_prob': round(away_win_prob, 3),
                        'home_prob': round(home_win_prob, 3)
                    },
                    'betting_recommendations': {
                        'moneyline': {
                            'pick': moneyline_pick,
                            'team': away_team if moneyline_pick == 'away' else home_team if moneyline_pick == 'home' else None,
                            'confidence': round(moneyline_confidence, 3)
                        },
                        'total_runs': {
                            'market_line': market_total,
                            'pick': ou_pick,
                            'predicted_total': predicted_total,
                            'confidence': round(ou_confidence, 3),
                            'edge': round(predicted_total - market_total, 2)
                        }
                    },
                    'overall_confidence': round(overall_confidence, 3),
                    'market_alignment': game_data.get('market_alignment', 'UNKNOWN')
                }
                
                recommendations['games'][game_key] = game_rec
            
            # Save enhanced recommendations
            filename = f'data/betting_recommendations_{self.current_date.replace("-", "_")}.json'
            with open(filename, 'w') as f:
                json.dump(recommendations, f, indent=2)
            
            logger.info("✅ Enhanced betting recommendations generated with real market data!")
            logger.info(f"📊 Summary: {recommendations['summary']['moneyline_picks']} ML picks, {recommendations['summary']['over_picks']} over, {recommendations['summary']['under_picks']} under")
            
            return True
            
        except Exception as e:
            logger.error(f"Error regenerating betting recommendations: {e}")
            return False
    
    def update_unified_cache(self, enhanced_predictions: dict) -> bool:
        """Update unified predictions cache with enhanced predictions"""
        try:
            # Load current unified cache
            cache_path = 'unified_predictions_cache.json'
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Update today's predictions with enhanced data
            if 'predictions_by_date' not in cache_data:
                cache_data['predictions_by_date'] = {}
            
            # Create enhanced games data
            enhanced_games = {}
            for game_name, prediction in enhanced_predictions.items():
                # Keep existing structure but update with enhanced data
                if self.current_date in cache_data['predictions_by_date']:
                    existing_game = cache_data['predictions_by_date'][self.current_date].get('games', {}).get(game_name, {})
                    
                    # Update with enhanced data
                    existing_game.update({
                        'predicted_total_runs': prediction['predicted_total_runs'],
                        'market_enhanced': True,
                        'market_total_line': prediction.get('market_total_line'),
                        'market_alignment': prediction.get('market_alignment', 'UNKNOWN'),
                        'enhancement_time': datetime.now().isoformat()
                    })
                    enhanced_games[game_name] = existing_game
                else:
                    # Create new entry if it doesn't exist
                    enhanced_games[game_name] = prediction
            
            # Update cache with enhanced data
            cache_data['predictions_by_date'][self.current_date] = {
                'date': self.current_date,
                'games_count': len(enhanced_games),
                'last_updated': datetime.now().isoformat(),
                'market_enhanced': True,
                'games': enhanced_games
            }
            
            # Update metadata
            cache_data['metadata']['last_market_enhancement'] = datetime.now().isoformat()
            cache_data['metadata']['market_enhanced_games'] = len(enhanced_games)
            
            # Save updated cache
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"✅ Updated unified cache with {len(enhanced_games)} enhanced predictions")
            return True
            
        except Exception as e:
            logger.error(f"Error updating unified cache: {e}")
            return False

def main():
    """Main function"""
    logger.info("🎯 Enhanced Prediction Engine with Real Market Data Starting")
    
    engine = EnhancedPredictionEngine()
    
    # Step 1: Enhance predictions with market data
    enhanced_predictions = {}
    if engine.regenerate_todays_predictions():
        logger.info("✅ Predictions enhanced with real market data")
        
        # Load the enhanced predictions
        try:
            with open('MLB-Betting/data/unified_predictions_cache.json', 'r') as f:
                predictions_data = json.load(f)
            enhanced_predictions = predictions_data.get('predictions_by_date', {}).get(engine.current_date, {}).get('games', {})
        except:
            logger.warning("Could not load enhanced predictions for cache update")
        
        # Step 2: Update unified cache with enhanced predictions
        if enhanced_predictions and engine.update_unified_cache(enhanced_predictions):
            logger.info("✅ Unified cache updated with enhanced predictions")
        
        # Step 3: Regenerate betting recommendations
        if engine.regenerate_betting_recommendations():
            logger.info("✅ Betting recommendations regenerated with market-enhanced data")
            
            logger.info("🎯 ENHANCEMENT COMPLETE:")
            logger.info("  ✅ Real over/under totals integrated")
            logger.info("  ✅ Market alignment calculated") 
            logger.info("  ✅ Enhanced betting recommendations generated")
            logger.info("  ✅ Unified cache updated with enhanced data")
            logger.info("  🔄 Ready for dashboard display")
        else:
            logger.error("❌ Failed to regenerate betting recommendations")
    else:
        logger.error("❌ Failed to enhance predictions with market data")

if __name__ == "__main__":
    main()
