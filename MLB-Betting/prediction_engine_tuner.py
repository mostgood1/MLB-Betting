"""
MLB Prediction Engine Tuning System
===================================

This system analyzes historical predictions vs actual results to optimize
prediction engine parameters and improve accuracy.

Features:
- Historical prediction accuracy analysis
- Parameter optimization using machine learning
- Model performance scoring and validation
- Automated parameter tuning recommendations
- Betting recommendation effectiveness analysis
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Container for prediction vs actual result comparison"""
    date: str
    away_team: str
    home_team: str
    predicted_away_score: float
    predicted_home_score: float
    actual_away_score: Optional[int]
    actual_home_score: Optional[int]
    predicted_total: float
    actual_total: Optional[int]
    predicted_home_win_prob: float
    actual_home_win: Optional[bool]
    away_pitcher: str
    home_pitcher: str
    prediction_confidence: str
    betting_recommendations: List[Dict]

@dataclass
class TuningMetrics:
    """Container for tuning performance metrics"""
    score_mae: float  # Mean Absolute Error for scores
    score_rmse: float  # Root Mean Square Error for scores
    total_mae: float  # Mean Absolute Error for totals
    win_probability_accuracy: float  # Win probability accuracy
    betting_roi: float  # Return on Investment for betting recommendations
    confidence_calibration: float  # How well confidence matches actual accuracy

class MLBPredictionTuner:
    """
    Advanced tuning system for MLB prediction engine
    """
    
    def __init__(self, data_dir: str = "MLB-Betting/data"):
        self.data_dir = data_dir
        self.historical_data = []
        self.tuning_results = {}
        self.optimal_parameters = {}
        
    def load_historical_data(self) -> List[PredictionResult]:
        """Load and parse historical prediction data"""
        logger.info("Loading historical prediction data...")
        
        try:
            # Load unified predictions cache
            with open('unified_predictions_cache.json', 'r') as f:
                predictions_data = json.load(f)
            
            # Load actual game results
            with open('game_scores_cache.json', 'r') as f:
                actual_results = json.load(f)
            
            results = []
            
            # Process predictions by date
            predictions_by_date = predictions_data.get('predictions_by_date', {})
            
            for date, date_data in predictions_by_date.items():
                if date == 'metadata':
                    continue
                    
                games = date_data.get('games', {})
                actual_games = actual_results.get(date, {}).get('games', [])
                
                # Convert actual games list to dict for easier lookup
                actual_games_dict = {}
                if isinstance(actual_games, list):
                    for game in actual_games:
                        key = f"{game.get('away_team', '')} @ {game.get('home_team', '')}"
                        actual_games_dict[key] = game
                elif isinstance(actual_games, dict):
                    actual_games_dict = actual_games
                
                for game_key, prediction in games.items():
                    # Find matching actual result
                    actual_game = None
                    for actual_key, actual_data in actual_games_dict.items():
                        if (prediction.get('away_team', '').lower() in actual_key.lower() and 
                            prediction.get('home_team', '').lower() in actual_key.lower()):
                            actual_game = actual_data
                            break
                    
                    # Create prediction result
                    result = PredictionResult(
                        date=date,
                        away_team=prediction.get('away_team', ''),
                        home_team=prediction.get('home_team', ''),
                        predicted_away_score=prediction.get('predicted_away_score', 0),
                        predicted_home_score=prediction.get('predicted_home_score', 0),
                        actual_away_score=actual_game.get('away_score') if actual_game else None,
                        actual_home_score=actual_game.get('home_score') if actual_game else None,
                        predicted_total=prediction.get('predicted_total_runs', 0),
                        actual_total=actual_game.get('total_score') if actual_game else None,
                        predicted_home_win_prob=prediction.get('home_win_probability', 0.5),
                        actual_home_win=actual_game.get('home_score', 0) > actual_game.get('away_score', 0) if actual_game else None,
                        away_pitcher=prediction.get('away_pitcher', 'TBD'),
                        home_pitcher=prediction.get('home_pitcher', 'TBD'),
                        prediction_confidence=prediction.get('confidence_level', 'MEDIUM'),
                        betting_recommendations=prediction.get('comprehensive_details', {}).get('betting_recommendations', [])
                    )
                    
                    results.append(result)
            
            logger.info(f"Loaded {len(results)} historical predictions")
            completed_games = len([r for r in results if r.actual_away_score is not None])
            logger.info(f"Found {completed_games} completed games for analysis")
            
            self.historical_data = results
            return results
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return []
    
    def analyze_prediction_accuracy(self) -> TuningMetrics:
        """Analyze accuracy of historical predictions"""
        logger.info("Analyzing prediction accuracy...")
        
        completed_games = [r for r in self.historical_data if r.actual_away_score is not None]
        
        if not completed_games:
            logger.warning("No completed games found for analysis")
            return TuningMetrics(0, 0, 0, 0, 0, 0)
        
        # Score prediction accuracy
        predicted_away_scores = [r.predicted_away_score for r in completed_games if r.predicted_away_score is not None and not np.isnan(r.predicted_away_score)]
        actual_away_scores = [r.actual_away_score for r in completed_games if r.actual_away_score is not None and not np.isnan(r.actual_away_score)]
        predicted_home_scores = [r.predicted_home_score for r in completed_games if r.predicted_home_score is not None and not np.isnan(r.predicted_home_score)]
        actual_home_scores = [r.actual_home_score for r in completed_games if r.actual_home_score is not None and not np.isnan(r.actual_home_score)]
        
        # Only use games where we have both predicted and actual scores
        valid_games = [r for r in completed_games if (
            r.predicted_away_score is not None and not np.isnan(r.predicted_away_score) and
            r.actual_away_score is not None and not np.isnan(r.actual_away_score) and
            r.predicted_home_score is not None and not np.isnan(r.predicted_home_score) and
            r.actual_home_score is not None and not np.isnan(r.actual_home_score)
        )]
        
        if not valid_games:
            logger.warning("No valid games with complete score data found")
            return TuningMetrics(0, 0, 0, 0, 0, 0)
        
        # Combine away and home scores for overall accuracy
        all_predicted_scores = []
        all_actual_scores = []
        
        for game in valid_games:
            all_predicted_scores.extend([game.predicted_away_score, game.predicted_home_score])
            all_actual_scores.extend([game.actual_away_score, game.actual_home_score])
        
        score_mae = mean_absolute_error(all_actual_scores, all_predicted_scores)
        score_rmse = np.sqrt(mean_squared_error(all_actual_scores, all_predicted_scores))
        
        # Total runs accuracy
        total_games_with_data = []
        for game in valid_games:
            if (game.predicted_total is not None and not np.isnan(game.predicted_total) and
                game.actual_total is not None and not np.isnan(game.actual_total)):
                total_games_with_data.append(game)
        
        if total_games_with_data:
            predicted_totals = [r.predicted_total for r in total_games_with_data]
            actual_totals = [r.actual_total for r in total_games_with_data]
            total_mae = mean_absolute_error(actual_totals, predicted_totals)
        else:
            total_mae = 0
        
        # Win probability accuracy
        predicted_home_wins = [r.predicted_home_win_prob > 0.5 for r in valid_games if r.predicted_home_win_prob is not None]
        actual_home_wins = [r.actual_home_win for r in valid_games if r.actual_home_win is not None]
        
        # Align the lists
        min_len = min(len(predicted_home_wins), len(actual_home_wins))
        if min_len > 0:
            predicted_home_wins = predicted_home_wins[:min_len]
            actual_home_wins = actual_home_wins[:min_len]
            win_accuracy = accuracy_score(actual_home_wins, predicted_home_wins)
        else:
            win_accuracy = 0
        
        # Betting ROI (simplified calculation)
        betting_roi = self._calculate_betting_roi(completed_games)
        
        # Confidence calibration
        confidence_calibration = self._calculate_confidence_calibration(completed_games)
        
        metrics = TuningMetrics(
            score_mae=score_mae,
            score_rmse=score_rmse,
            total_mae=total_mae,
            win_probability_accuracy=win_accuracy,
            betting_roi=betting_roi,
            confidence_calibration=confidence_calibration
        )
        
        logger.info(f"Prediction Accuracy Metrics:")
        logger.info(f"  Score MAE: {score_mae:.2f}")
        logger.info(f"  Score RMSE: {score_rmse:.2f}")
        logger.info(f"  Total Runs MAE: {total_mae:.2f}")
        logger.info(f"  Win Probability Accuracy: {win_accuracy:.3f}")
        logger.info(f"  Betting ROI: {betting_roi:.2f}%")
        logger.info(f"  Confidence Calibration: {confidence_calibration:.3f}")
        
        return metrics
    
    def optimize_parameters(self) -> Dict:
        """Use machine learning to optimize prediction parameters"""
        logger.info("Optimizing prediction parameters...")
        
        completed_games = [r for r in self.historical_data if r.actual_away_score is not None]
        
        if len(completed_games) < 10:
            logger.warning("Insufficient data for parameter optimization")
            return {}
        
        # Prepare features for ML model
        features = []
        targets_away = []
        targets_home = []
        targets_total = []
        
        for game in completed_games:
            # Create feature vector
            feature_vector = [
                hash(game.away_team) % 1000,  # Team encoding
                hash(game.home_team) % 1000,
                hash(game.away_pitcher) % 1000 if game.away_pitcher != 'TBD' else 0,
                hash(game.home_pitcher) % 1000 if game.home_pitcher != 'TBD' else 0,
                datetime.strptime(game.date, '%Y-%m-%d').weekday(),  # Day of week
                int(game.date.split('-')[1])  # Month
            ]
            
            features.append(feature_vector)
            targets_away.append(game.actual_away_score)
            targets_home.append(game.actual_home_score)
            targets_total.append(game.actual_total)
        
        # Train models for different prediction types
        models = {}
        
        # Away score model
        rf_away = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_away.fit(features, targets_away)
        models['away_score'] = rf_away
        
        # Home score model
        rf_home = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_home.fit(features, targets_home)
        models['home_score'] = rf_home
        
        # Total runs model
        rf_total = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_total.fit(features, targets_total)
        models['total_runs'] = rf_total
        
        # Extract optimal parameters
        optimal_params = {
            'away_score_factors': rf_away.feature_importances_.tolist(),
            'home_score_factors': rf_home.feature_importances_.tolist(),
            'total_runs_factors': rf_total.feature_importances_.tolist(),
            'pitcher_weight': np.mean([rf_away.feature_importances_[2], rf_home.feature_importances_[3]]),
            'team_weight': np.mean([rf_away.feature_importances_[0], rf_home.feature_importances_[1]]),
            'seasonal_adjustment': np.mean([rf_away.feature_importances_[5], rf_home.feature_importances_[5]])
        }
        
        self.optimal_parameters = optimal_params
        logger.info("Parameter optimization complete")
        
        return optimal_params
    
    def generate_tuning_recommendations(self) -> Dict:
        """Generate specific recommendations for improving prediction accuracy"""
        logger.info("Generating tuning recommendations...")
        
        metrics = self.analyze_prediction_accuracy()
        recommendations = {
            'immediate_actions': [],
            'parameter_adjustments': {},
            'data_improvements': [],
            'model_enhancements': []
        }
        
        # Score accuracy recommendations
        if metrics.score_mae > 1.5:
            recommendations['immediate_actions'].append(
                f"Score predictions have high error (MAE: {metrics.score_mae:.2f}). Consider adjusting team strength factors."
            )
            recommendations['parameter_adjustments']['score_variance_reduction'] = 0.8
        
        # Total runs recommendations
        if metrics.total_mae > 1.2:
            recommendations['immediate_actions'].append(
                f"Total runs predictions need improvement (MAE: {metrics.total_mae:.2f}). Review pitcher impact factors."
            )
            recommendations['parameter_adjustments']['pitcher_impact_weight'] = 1.3
        
        # Win probability recommendations
        if metrics.win_probability_accuracy < 0.6:
            recommendations['immediate_actions'].append(
                f"Win probability accuracy is low ({metrics.win_probability_accuracy:.3f}). Recalibrate probability model."
            )
            recommendations['parameter_adjustments']['win_prob_calibration'] = 1.2
        
        # Data improvement suggestions
        completed_ratio = len([r for r in self.historical_data if r.actual_away_score is not None]) / len(self.historical_data)
        if completed_ratio < 0.7:
            recommendations['data_improvements'].append(
                "Increase historical data coverage. Only {:.1%} of predictions have actual results.".format(completed_ratio)
            )
        
        # Model enhancement suggestions
        if metrics.confidence_calibration < 0.7:
            recommendations['model_enhancements'].append(
                "Improve confidence calibration by implementing uncertainty quantification."
            )
        
        if metrics.betting_roi < 5:
            recommendations['model_enhancements'].append(
                "Enhance betting recommendation algorithms to improve ROI."
            )
        
        logger.info(f"Generated {len(recommendations['immediate_actions'])} immediate action items")
        return recommendations
    
    def create_tuning_report(self) -> str:
        """Create comprehensive tuning report"""
        logger.info("Creating tuning report...")
        
        metrics = self.analyze_prediction_accuracy()
        recommendations = self.generate_tuning_recommendations()
        
        report = f"""
# MLB Prediction Engine Tuning Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report analyzes the performance of your MLB prediction engine using {len(self.historical_data)} historical predictions and provides optimization recommendations.

## Current Performance Metrics

### Prediction Accuracy
- **Score Prediction Error**: {metrics.score_mae:.2f} runs (MAE), {metrics.score_rmse:.2f} runs (RMSE)
- **Total Runs Error**: {metrics.total_mae:.2f} runs (MAE)
- **Win Probability Accuracy**: {metrics.win_probability_accuracy:.1%}
- **Betting ROI**: {metrics.betting_roi:.2f}%
- **Confidence Calibration**: {metrics.confidence_calibration:.3f}

### Performance Grade
"""
        
        # Calculate overall grade
        grade_score = (
            (100 - metrics.score_mae * 20) * 0.3 +
            (100 - metrics.total_mae * 25) * 0.3 +
            (metrics.win_probability_accuracy * 100) * 0.4
        )
        
        if grade_score >= 85:
            grade = "A - Excellent"
        elif grade_score >= 75:
            grade = "B - Good"
        elif grade_score >= 65:
            grade = "C - Average"
        elif grade_score >= 55:
            grade = "D - Below Average"
        else:
            grade = "F - Needs Major Improvement"
        
        report += f"**Overall Grade: {grade}** (Score: {grade_score:.1f}/100)\n\n"
        
        # Add recommendations
        report += "## Immediate Action Items\n"
        for action in recommendations['immediate_actions']:
            report += f"- {action}\n"
        
        report += "\n## Parameter Adjustment Recommendations\n"
        for param, value in recommendations['parameter_adjustments'].items():
            report += f"- **{param}**: Adjust to {value}\n"
        
        report += "\n## Data Quality Improvements\n"
        for improvement in recommendations['data_improvements']:
            report += f"- {improvement}\n"
        
        report += "\n## Model Enhancement Opportunities\n"
        for enhancement in recommendations['model_enhancements']:
            report += f"- {enhancement}\n"
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"tuning_report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Tuning report saved to {report_file}")
        return report
    
    def _calculate_betting_roi(self, completed_games: List[PredictionResult]) -> float:
        """Calculate ROI for betting recommendations (simplified)"""
        total_bet = 0
        total_return = 0
        
        for game in completed_games:
            if not game.betting_recommendations:
                continue
            
            # Simplified ROI calculation based on win accuracy
            for rec in game.betting_recommendations:
                if isinstance(rec, dict) and rec.get('confidence') == 'HIGH':
                    bet_amount = 100  # Standard bet size
                    total_bet += bet_amount
                    
                    # Simplified win/loss calculation
                    if game.actual_home_win and 'home' in rec.get('recommendation', '').lower():
                        total_return += bet_amount * 1.9  # Assume -110 odds
                    elif not game.actual_home_win and 'away' in rec.get('recommendation', '').lower():
                        total_return += bet_amount * 1.9
        
        if total_bet == 0:
            return 0
        
        roi = ((total_return - total_bet) / total_bet) * 100
        return roi
    
    def _calculate_confidence_calibration(self, completed_games: List[PredictionResult]) -> float:
        """Calculate how well confidence levels match actual accuracy"""
        confidence_accuracy = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
        
        for game in completed_games:
            if game.actual_home_win is None:
                continue
            
            predicted_home_win = game.predicted_home_win_prob > 0.5
            correct = predicted_home_win == game.actual_home_win
            
            confidence_accuracy[game.prediction_confidence].append(correct)
        
        # Calculate accuracy by confidence level
        calibration_score = 0
        for confidence, results in confidence_accuracy.items():
            if results:
                accuracy = sum(results) / len(results)
                expected_accuracy = {'HIGH': 0.8, 'MEDIUM': 0.6, 'LOW': 0.5}[confidence]
                calibration_score += 1 - abs(accuracy - expected_accuracy)
        
        return calibration_score / 3 if calibration_score > 0 else 0

def main():
    """Main tuning execution"""
    print("🎯 MLB Prediction Engine Tuning System")
    print("="*50)
    
    # Initialize tuner
    tuner = MLBPredictionTuner()
    
    # Load historical data
    historical_data = tuner.load_historical_data()
    
    if not historical_data:
        print("❌ No historical data found. Please ensure prediction and game result files exist.")
        return
    
    # Analyze current performance
    print("\n📊 Analyzing current performance...")
    metrics = tuner.analyze_prediction_accuracy()
    
    # Optimize parameters
    print("\n🔧 Optimizing parameters...")
    optimal_params = tuner.optimize_parameters()
    
    # Generate recommendations
    print("\n💡 Generating recommendations...")
    recommendations = tuner.generate_tuning_recommendations()
    
    # Create comprehensive report
    print("\n📋 Creating tuning report...")
    report = tuner.create_tuning_report()
    
    print("\n✅ Tuning analysis complete!")
    print(f"📄 Report saved with {len(recommendations['immediate_actions'])} action items")
    print(f"🎯 Current performance grade: {report.split('Overall Grade: ')[1].split('**')[0]}")

if __name__ == "__main__":
    main()
