"""
Enhanced Master Predictions Service
Integrates Comprehensive Tuned Engine with cached predictions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from comprehensive_tuned_engine import ComprehensiveTunedEngine

class EnhancedMasterPredictionsService:
    """Enhanced service that combines cached predictions with comprehensive engine"""
    
    def __init__(self, master_file_path: Optional[str] = None):
        """Initialize with path to master predictions file and comprehensive engine"""
        if master_file_path is None:
            # Default to data directory in same folder
            master_file_path = os.path.join(
                os.path.dirname(__file__), 'data', 'master_predictions.json'
            )
        
        self.master_file_path = os.path.abspath(master_file_path)
        self.predictions_data = None
        self.games_data = None
        self.pitcher_stats = None
        self.last_loaded = None
        
        # Initialize comprehensive tuned engine for new predictions
        print("🚀 Initializing Enhanced Master Predictions Service...")
        try:
            self.comprehensive_engine = ComprehensiveTunedEngine()
            print("✅ Comprehensive Tuned Engine loaded successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not load Comprehensive Engine: {e}")
            print("   Falling back to cached predictions only")
            self.comprehensive_engine = None
        
        # Load cached predictions, games data, and pitcher stats
        self._load_predictions()
        self._load_games_data()
        self._load_pitcher_stats()
        
        print(f"📊 Enhanced service initialized with {self.get_status()['total_games']} cached predictions")
    
    def _load_predictions(self):
        """Load predictions from master_predictions.json"""
        try:
            if not os.path.exists(self.master_file_path):
                print(f"⚠️ Master predictions file not found: {self.master_file_path}")
                self.predictions_data = {"predictions_by_date": {}}
                return
            
            with open(self.master_file_path, 'r') as f:
                self.predictions_data = json.load(f)
            
            self.last_loaded = datetime.now()
            print(f"✅ Loaded predictions from {self.master_file_path}")
            
        except Exception as e:
            print(f"❌ Error loading predictions: {e}")
            self.predictions_data = {"predictions_by_date": {}}
    
    def _load_games_data(self):
        """Load games data for team name normalization"""
        try:
            games_path = os.path.join(os.path.dirname(self.master_file_path), 'games_data.json')
            if os.path.exists(games_path):
                with open(games_path, 'r') as f:
                    self.games_data = json.load(f)
                print(f"✅ Loaded games data from {games_path}")
            else:
                print(f"⚠️ Games data file not found: {games_path}")
                self.games_data = {}
        except Exception as e:
            print(f"❌ Error loading games data: {e}")
            self.games_data = {}
    
    def _load_pitcher_stats(self):
        """Load pitcher stats for factor calculations"""
        try:
            pitcher_path = os.path.join(os.path.dirname(self.master_file_path), 'pitcher_stats.json')
            if os.path.exists(pitcher_path):
                with open(pitcher_path, 'r') as f:
                    self.pitcher_stats = json.load(f)
                print(f"✅ Loaded pitcher stats from {pitcher_path}")
            else:
                print(f"⚠️ Pitcher stats file not found: {pitcher_path}")
                self.pitcher_stats = {}
        except Exception as e:
            print(f"❌ Error loading pitcher stats: {e}")
            self.pitcher_stats = {}
    
    def get_prediction_for_game(self, away_team: str, home_team: str, game_date: str,
                              away_pitcher: str = None, home_pitcher: str = None,
                              market_total: float = None) -> Optional[Dict]:
        """Get prediction for a specific game - enhanced with comprehensive engine"""
        
        print(f"🎯 ENHANCED SERVICE - get_prediction_for_game called for {away_team} @ {home_team}")
        print(f"   Game date: {game_date}")
        print(f"   Away pitcher: {away_pitcher}")
        print(f"   Home pitcher: {home_pitcher}")
        
        # First, try to get cached prediction
        cached_prediction = self._get_cached_prediction(away_team, home_team, game_date)
        print(f"   Cached prediction found: {cached_prediction is not None}")
        
        if cached_prediction:
            # Enhance cached prediction with comprehensive analysis if possible
            if self.comprehensive_engine:
                return self._enhance_cached_prediction(cached_prediction, away_team, home_team, game_date)
            else:
                return cached_prediction
        
        # If no cached prediction and we have comprehensive engine, generate new one
        if self.comprehensive_engine:
            print(f"🎯 Generating new comprehensive prediction: {away_team} @ {home_team}")
            return self._generate_comprehensive_prediction(away_team, home_team, game_date, away_pitcher, home_pitcher, market_total)
        
        # No prediction available
        print(f"❌ No prediction available for {away_team} @ {home_team} on {game_date}")
        return None
    
    def _get_cached_prediction(self, away_team: str, home_team: str, game_date: str) -> Optional[Dict]:
        """Get cached prediction from master data"""
        if not self.predictions_data:
            return None
        
        predictions_by_date = self.predictions_data.get('predictions_by_date', {})
        date_predictions = predictions_by_date.get(game_date, {})
        
        # Try different team name formats
        possible_keys = [
            f"{away_team} @ {home_team}",
            f"{away_team}@{home_team}",
            f"{away_team} vs {home_team}",
        ]
        
        for key in possible_keys:
            if key in date_predictions:
                return date_predictions[key]
        
        return None
    
    def _enhance_cached_prediction(self, cached_prediction: Dict, away_team: str, home_team: str, game_date: str) -> Dict:
        """Enhance cached prediction with comprehensive analysis"""
        try:
            # Get comprehensive analysis from new engine
            comprehensive_analysis = self.comprehensive_engine.get_comprehensive_prediction(
                away_team, home_team, game_date, prediction_type='full'
            )
            
            # Merge cached prediction with comprehensive analysis
            enhanced_prediction = cached_prediction.copy()
            
            # Add comprehensive enhancements
            enhanced_prediction.update({
                'comprehensive_analysis': comprehensive_analysis.get('total_runs_prediction', {}),
                'betting_recommendations': comprehensive_analysis.get('betting_recommendations', {}),
                'optimization_details': {
                    'enhanced': True,
                    'comprehensive_engine_used': True,
                    'cached_base_prediction': True
                },
                'ballpark_factor': comprehensive_analysis.get('optimization_details', {}).get('calculation_details', {}).get('ballpark_factor', 1.0)
            })
            
            return enhanced_prediction
            
        except Exception as e:
            print(f"⚠️ Could not enhance cached prediction: {e}")
            return cached_prediction
    
    def _generate_comprehensive_prediction(self, away_team: str, home_team: str, game_date: str,
                                         away_pitcher: str = None, home_pitcher: str = None,
                                         market_total: float = None) -> Dict:
        """Generate new prediction using comprehensive engine"""
        print(f"🎯 ENHANCED SERVICE - Generating comprehensive prediction for {away_team} @ {home_team}")
        print(f"   Away pitcher: {away_pitcher}")
        print(f"   Home pitcher: {home_pitcher}")
        print(f"   📊 DEBUG: Market total to pass to engine: {market_total}")
        try:
            comprehensive_prediction = self.comprehensive_engine.get_comprehensive_prediction(
                away_team, home_team, game_date, prediction_type='full',
                away_pitcher=away_pitcher, home_pitcher=home_pitcher, market_total=market_total
            )
            
            # Convert to format compatible with cached predictions
            # Safely extract scores
            predicted_score = comprehensive_prediction['winner_prediction'].get('predicted_score', '0 - 0')
            if ' - ' in predicted_score:
                away_score, home_score = predicted_score.split(' - ')
            else:
                away_score, home_score = '0', '0'
            
            converted_prediction = {
                'game_pk': f"new_{game_date}_{away_team}_{home_team}",
                'predicted_away_score': float(away_score),
                'predicted_home_score': float(home_score),
                'predicted_total_runs': float(comprehensive_prediction['total_runs_prediction'].get('predicted_total', 0)),
                'simulation_count': int(comprehensive_prediction['optimization_details'].get('simulation_count', 3000)),
                'home_win_probability': float(comprehensive_prediction['winner_prediction'].get('home_win_probability', 0.5)),
                'away_win_probability': float(comprehensive_prediction['winner_prediction'].get('away_win_probability', 0.5)),
                # Store the live pitcher information that was passed to the engine
                'away_pitcher': away_pitcher or 'TBD',
                'home_pitcher': home_pitcher or 'TBD',
                'away_pitcher_id': None,  # Could be enhanced later if we track pitcher IDs
                'home_pitcher_id': None,
                'comprehensive_prediction': comprehensive_prediction,
                'generated_live': True,
                'optimization_version': '3.0-comprehensive',
                # CRITICAL FIX: Include betting recommendations from comprehensive prediction
                'betting_recommendations': comprehensive_prediction.get('betting_recommendations', {})
            }
            
            return converted_prediction
            
        except Exception as e:
            print(f"❌ Error generating comprehensive prediction: {e}")
            return None
    
    def get_predictions_for_date(self, game_date: str) -> Dict[str, Dict]:
        """Get all predictions for a specific date"""
        if not self.predictions_data:
            return {}
        
        predictions_by_date = self.predictions_data.get('predictions_by_date', {})
        return predictions_by_date.get(game_date, {})
    
    def format_prediction_for_api(self, prediction: Dict, away_team: str, home_team: str, betting_data: Dict = None) -> Dict:
        """Format prediction for API response with comprehensive enhancements"""
        try:
            # Safely extract numeric values with proper fallbacks
            def safe_float(value, default=0.0):
                try:
                    if value is None:
                        return default
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            def safe_int(value, default=0):
                try:
                    if value is None:
                        return default
                    return int(value)
                except (ValueError, TypeError):
                    return default
            
            # Calculate win probabilities from simulations if missing
            home_win_prob = safe_float(prediction.get('home_win_probability'), None)
            away_win_prob = safe_float(prediction.get('away_win_probability'), None)
            
            # If probabilities are missing or both are 0.5, calculate from simulations
            if (home_win_prob is None or away_win_prob is None or 
                (home_win_prob == 0.5 and away_win_prob == 0.5)) and 'simulations' in prediction:
                simulations = prediction['simulations']
                if simulations:
                    home_wins = sum(1 for sim in simulations if sim.get('home_wins', False))
                    total_sims = len(simulations)
                    home_win_prob = home_wins / total_sims if total_sims > 0 else 0.5
                    away_win_prob = 1.0 - home_win_prob
                else:
                    home_win_prob = 0.5
                    away_win_prob = 0.5
            elif home_win_prob is None or away_win_prob is None:
                home_win_prob = 0.5
                away_win_prob = 0.5

            # Get calculation details for pitcher factors
            # Try multiple possible locations for calculation details
            calc_details = {}
            if 'comprehensive_prediction' in prediction:
                calc_details = prediction['comprehensive_prediction'].get('optimization_details', {}).get('calculation_details', {})
            elif 'comprehensive_details' in prediction:
                calc_details = prediction['comprehensive_details'].get('optimization_details', {}).get('calculation_details', {})
            elif 'calculation_details' in prediction:
                calc_details = prediction['calculation_details']
            
            away_pitcher_factor = calc_details.get('away_pitcher_factor', 1.0)
            home_pitcher_factor = calc_details.get('home_pitcher_factor', 1.0)

            base_format = {
                'away_team': away_team,
                'home_team': home_team,
                'predicted_away_score': safe_float(prediction.get('predicted_away_score')),
                'predicted_home_score': safe_float(prediction.get('predicted_home_score')),
                'predicted_total_runs': safe_float(prediction.get('predicted_total_runs')),
                'home_win_probability': home_win_prob,
                'away_win_probability': away_win_prob,
                'simulation_count': safe_int(prediction.get('simulation_count'), 3000),
                # Add short field names for frontend compatibility
                'home_win_prob': home_win_prob,
                'away_win_prob': away_win_prob,
                # Add pitcher information with default values
                'away_pitcher': prediction.get('away_pitcher', 'TBD'),
                'home_pitcher': prediction.get('home_pitcher', 'TBD'),
                'away_pitcher_id': prediction.get('away_pitcher_id'),
                'home_pitcher_id': prediction.get('home_pitcher_id'),
                # Add calculation details from comprehensive prediction
                'calculation_details': calc_details,
                # Add predictions object structure for frontend compatibility
                'predictions': {
                    'away_pitcher': {
                        'name': prediction.get('away_pitcher', 'TBD'),
                        'id': prediction.get('away_pitcher_id'),
                        'factor': away_pitcher_factor
                    },
                    'home_pitcher': {
                        'name': prediction.get('home_pitcher', 'TBD'),
                        'id': prediction.get('home_pitcher_id'),
                        'factor': home_pitcher_factor
                    }
                },
                # Add meta information for frontend compatibility
                'meta': {
                    'execution_time_ms': safe_float(prediction.get('execution_time_ms'), 0 if not prediction.get('generated_live', False) else 50),
                    'source': 'comprehensive_engine' if prediction.get('generated_live', False) else 'cached',
                    'enhanced': prediction.get('optimization_details', {}).get('enhanced', False) if isinstance(prediction.get('optimization_details'), dict) else False,
                    'simulations_run': safe_int(prediction.get('simulation_count'), 3000),
                    'data_source': 'comprehensive_engine' if prediction.get('generated_live', False) else 'cached_prediction'
                }
            }
            
            # Add comprehensive enhancements if available
            if 'comprehensive_analysis' in prediction:
                base_format['total_runs_analysis'] = prediction['comprehensive_analysis']
            
            # Add betting data if provided
            if betting_data:
                base_format['betting_data'] = betting_data
            
            # Generate enhanced betting recommendations if we have real betting data
            if betting_data or 'betting_data' in prediction:
                # Create temp prediction with betting data for analysis
                temp_prediction = prediction.copy()
                if betting_data:
                    temp_prediction['betting_data'] = betting_data
                
                betting_recs = self.generate_betting_recommendations(temp_prediction, home_win_prob, away_win_prob)
                if betting_recs:
                    base_format['betting_recommendations'] = betting_recs
                    
                    # Map to frontend expected format for compatibility
                    frontend_recs = []
                    for value_bet in betting_recs.get('value_bets', []):
                        frontend_recs.append({
                            'type': 'moneyline',
                            'side': value_bet['team'],
                            'expected_value': value_bet['edge'],
                            'kelly_bet_size': min(value_bet['edge'] * 10, 5.0),  # Conservative Kelly sizing
                            'confidence': value_bet['confidence'],
                            'reasoning': value_bet['recommendation']
                        })
                    
                    base_format['recommendations'] = frontend_recs
                    
            # Fallback to cached recommendations if no betting data
            elif 'betting_recommendations' in prediction:
                base_format['betting_recommendations'] = prediction['betting_recommendations']
            
            if 'comprehensive_prediction' in prediction:
                base_format['comprehensive_details'] = prediction['comprehensive_prediction']
            
            # Add optimization info
            try:
                base_format['optimization_info'] = {
                    'enhanced': prediction.get('optimization_details', {}).get('enhanced', False),
                    'comprehensive_engine': prediction.get('optimization_details', {}).get('comprehensive_engine_used', False),
                    'generated_live': prediction.get('generated_live', False)
                }
            except Exception as opt_error:
                print(f"⚠️ Error in optimization_info: {opt_error}")
                print(f"optimization_details type: {type(prediction.get('optimization_details'))}")
                print(f"optimization_details value: {prediction.get('optimization_details')}")
                base_format['optimization_info'] = {
                    'enhanced': False,
                    'comprehensive_engine': False,
                    'generated_live': False
                }
            
            # Add legacy format for compatibility with pitcher factors
            def get_pitcher_factor(pitcher_name: str) -> float:
                """Get pitcher factor from stats or calculate from performance"""
                if not self.pitcher_stats:
                    return 1.0
                
                # Search for pitcher by name (since data is keyed by ID)
                for pitcher_id, stats in self.pitcher_stats.items():
                    if not isinstance(stats, dict):
                        continue  # Skip non-dict entries like 'last_updated'
                    if stats.get('name') == pitcher_name:
                        # Calculate factor based on ERA and WHIP
                        era = safe_float(stats.get('era', 4.5), 4.5)
                        whip = safe_float(stats.get('whip', 1.3), 1.3)
                        games_started = safe_float(stats.get('games_started', 0), 0)
                        
                        # Only calculate for starting pitchers
                        if games_started < 5:
                            return 1.0  # Relief pitchers get neutral factor
                        
                        # Calculate factor: lower ERA and WHIP = lower factor (good pitchers hurt opposing offense)
                        # ERA scale: 3.0 = 0.8, 4.5 = 1.0, 6.0 = 1.2
                        era_factor = max(0.7, min(1.3, 1.0 + (era - 4.5) * 0.133))
                        
                        # WHIP scale: 1.0 = 0.85, 1.3 = 1.0, 1.6 = 1.15
                        whip_factor = max(0.7, min(1.3, 1.0 + (whip - 1.3) * 0.5))
                        
                        # Combine factors
                        final_factor = (era_factor + whip_factor) / 2
                        return round(final_factor, 2)
                
                return 1.0  # Default neutral factor if pitcher not found
            
            base_format['predictions'] = {
                'away_pitcher': {
                    'name': base_format['away_pitcher'],
                    'id': base_format['away_pitcher_id'],
                    'factor': get_pitcher_factor(base_format['away_pitcher'])
                },
                'home_pitcher': {
                    'name': base_format['home_pitcher'],
                    'id': base_format['home_pitcher_id'],
                    'factor': get_pitcher_factor(base_format['home_pitcher'])
                }
            }
            
            return base_format
            
        except Exception as e:
            print(f"⚠️ Error formatting prediction: {e}")
            return {
                'away_team': away_team,
                'home_team': home_team,
                'error': 'Could not format prediction',
                'predicted_away_score': 0.0,
                'predicted_home_score': 0.0,
                'predicted_total_runs': 0.0,
                'home_win_probability': 0.5,
                'away_win_probability': 0.5,
                'home_win_prob': 0.5,
                'away_win_prob': 0.5,
                'simulation_count': 3000,
                'away_pitcher': 'TBD',
                'home_pitcher': 'TBD',
                'meta': {
                    'execution_time_ms': 0.0,
                    'source': 'error',
                    'enhanced': False,
                    'simulations_run': 3000,
                    'data_source': 'error'
                },
                'predictions': {
                    'away_pitcher': {'name': 'TBD', 'id': None},
                    'home_pitcher': {'name': 'TBD', 'id': None}
                }
            }
    
    def generate_betting_recommendations(self, prediction: Dict, home_win_prob: float = None, away_win_prob: float = None) -> Dict:
        """Generate betting recommendations based on prediction data and betting lines"""
        try:
            betting_data = prediction.get('betting_data', {})
            if not betting_data:
                return None
            
            # Extract prediction probabilities
            if home_win_prob is None:
                home_win_prob = prediction.get('home_win_probability', 0.5)
            if away_win_prob is None:
                away_win_prob = prediction.get('away_win_probability', 0.5)
            
            # Extract betting lines
            moneyline = betting_data.get('moneyline', {})
            home_odds = moneyline.get('home')
            away_odds = moneyline.get('away')
            
            if not home_odds or not away_odds:
                return None
            
            # Convert American odds to implied probability
            def odds_to_prob(odds):
                if odds > 0:
                    return 100 / (odds + 100)
                else:
                    return abs(odds) / (abs(odds) + 100)
            
            home_implied_prob = odds_to_prob(home_odds)
            away_implied_prob = odds_to_prob(away_odds)
            
            # Calculate edges (our probability vs market probability)
            home_edge = home_win_prob - home_implied_prob
            away_edge = away_win_prob - away_implied_prob
            
            recommendations = {
                'analysis': {
                    'home_team': {
                        'predicted_prob': round(home_win_prob, 3),
                        'implied_prob': round(home_implied_prob, 3),
                        'edge': round(home_edge, 3),
                        'odds': home_odds
                    },
                    'away_team': {
                        'predicted_prob': round(away_win_prob, 3),
                        'implied_prob': round(away_implied_prob, 3),
                        'edge': round(away_edge, 3),
                        'odds': away_odds
                    }
                },
                'value_bets': [],
                'recommendations': []
            }
            
            # Check for value bets (minimum 2% edge)
            if away_edge > 0.02:
                recommendations['value_bets'].append({
                    'team': 'away',
                    'edge': round(away_edge, 3),
                    'confidence': 'high' if away_edge > 0.05 else 'medium',
                    'recommendation': f"Value bet on away team ({away_edge:.1%} edge)"
                })
            
            if home_edge > 0.02:
                recommendations['value_bets'].append({
                    'team': 'home',
                    'edge': round(home_edge, 3),
                    'confidence': 'high' if home_edge > 0.05 else 'medium',
                    'recommendation': f"Value bet on home team ({home_edge:.1%} edge)"
                })
            
            # Generate text recommendations
            if recommendations['value_bets']:
                best_bet = max(recommendations['value_bets'], key=lambda x: x['edge'])
                recommendations['recommendations'].append(best_bet['recommendation'])
                recommendations['best_bet'] = best_bet
            else:
                recommendations['recommendations'].append("No significant value bets identified")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating betting recommendations: {e}")
            return None

    def get_status(self) -> Dict:
        """Get service status"""
        if not self.predictions_data:
            return {
                'status': 'error',
                'total_games': 0,
                'comprehensive_engine': self.comprehensive_engine is not None
            }
        
        predictions_by_date = self.predictions_data.get('predictions_by_date', {})
        total_games = sum(len(games) for games in predictions_by_date.values())
        
        return {
            'status': 'active',
            'total_games': total_games,
            'date_range': self.predictions_data.get('date_range', {}),
            'comprehensive_engine': self.comprehensive_engine is not None,
            'last_loaded': self.last_loaded.isoformat() if self.last_loaded else None,
            'enhancement_capable': self.comprehensive_engine is not None
        }

# Enhanced compatibility class for the app
class EnhancedMasterPredictionEngine:
    """Enhanced drop-in replacement that uses comprehensive engine"""
    
    def __init__(self):
        self.service = EnhancedMasterPredictionsService()
        print(f"🚀 Enhanced Master Prediction Engine initialized")
        status = self.service.get_status()
        print(f"   Total games: {status['total_games']}")
        print(f"   Comprehensive engine: {'✅ Available' if status['comprehensive_engine'] else '❌ Not available'}")
        print(f"   Enhancement capable: {'✅ Yes' if status['enhancement_capable'] else '❌ No'}")
        
    def get_fast_prediction(self, away_team: str, home_team: str, 
                           sim_count: int = 3000, game_date: str = None,
                           away_pitcher: str = None, home_pitcher: str = None,
                           market_total: float = None) -> Dict:
        """Get prediction - enhanced with comprehensive engine"""
        print(f"🚀 ENHANCED ENGINE - get_fast_prediction called for {away_team} @ {home_team}")
        print(f"   Away pitcher: {away_pitcher}")
        print(f"   Home pitcher: {home_pitcher}")
        print(f"   📊 DEBUG: Market total parameter: {market_total}")
        
        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')
            
        prediction = self.service.get_prediction_for_game(away_team, home_team, game_date, away_pitcher, home_pitcher, market_total)
        
        if prediction:
            return self.service.format_prediction_for_api(prediction, away_team, home_team)
        else:
            return {
                'away_team': away_team,
                'home_team': home_team,
                'error': 'No prediction available',
                'predicted_away_score': 0,
                'predicted_home_score': 0,
                'comprehensive_engine_available': self.service.comprehensive_engine is not None
            }
    
    def get_games_for_today(self) -> List[Dict]:
        """Get list of games for today - enhanced version"""
        today = datetime.now().strftime('%Y-%m-%d')
        predictions = self.service.get_predictions_for_date(today)
        
        games = []
        for game_key, prediction in predictions.items():
            if '@' in game_key:
                away_team, home_team = game_key.split('@', 1)
                away_team = away_team.strip()
                home_team = home_team.strip()
                
                games.append({
                    'away_team': away_team,
                    'home_team': home_team,
                    'game_date': today,
                    'has_prediction': True,
                    'enhanced': prediction.get('optimization_details', {}).get('enhanced', False)
                })
        
        return games
