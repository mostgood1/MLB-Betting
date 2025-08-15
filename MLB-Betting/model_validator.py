"""
Model Validation and Backtesting System
======================================

This system validates prediction models against historical data and provides
comprehensive backtesting capabilities for strategy optimization.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from sklearn.metrics import mean_absolute_error, mean_squared_error, classification_report
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Results from model validation"""
    model_name: str
    validation_period: str
    mae_score: float
    rmse_score: float
    win_accuracy: float
    total_accuracy: float
    betting_roi: float
    sharpe_ratio: float
    max_drawdown: float
    prediction_count: int

@dataclass
class BacktestResult:
    """Results from backtesting strategy"""
    strategy_name: str
    total_bets: int
    winning_bets: int
    total_profit: float
    roi_percentage: float
    win_rate: float
    average_odds: float
    profit_factor: float
    largest_win: float
    largest_loss: float

class ModelValidator:
    """Advanced model validation and backtesting system"""
    
    def __init__(self, data_dir: str = "MLB-Betting/data"):
        self.data_dir = data_dir
        self.historical_predictions = []
        self.actual_results = []
        self.validation_results = []
        self.backtest_results = []
    
    def load_validation_data(self) -> bool:
        """Load historical data for validation"""
        try:
            # Load predictions
            with open('unified_predictions_cache.json', 'r') as f:
                predictions_data = json.load(f)
            
            # Load actual results
            with open('game_scores_cache.json', 'r') as f:
                actual_data = json.load(f)
            
            # Process and align data
            self._process_validation_data(predictions_data, actual_data)
            
            logger.info(f"Loaded {len(self.historical_predictions)} predictions for validation")
            return True
            
        except Exception as e:
            logger.error(f"Error loading validation data: {e}")
            return False
    
    def _process_validation_data(self, predictions_data: Dict, actual_data: Dict):
        """Process and align prediction and actual data"""
        predictions_by_date = predictions_data.get('predictions_by_date', {})
        
        aligned_data = []
        
        for date, date_predictions in predictions_by_date.items():
            if date == 'metadata':
                continue
            
            games = date_predictions.get('games', {})
            actual_games = actual_data.get(date, {}).get('games', [])
            
            # Convert actual games to dict for easier lookup
            actual_dict = {}
            if isinstance(actual_games, list):
                for game in actual_games:
                    key = f"{game.get('away_team', '')} @ {game.get('home_team', '')}"
                    actual_dict[key] = game
            
            for game_key, prediction in games.items():
                # Find matching actual result
                actual_game = None
                for actual_key, actual in actual_dict.items():
                    if (prediction.get('away_team', '').lower() in actual_key.lower() and 
                        prediction.get('home_team', '').lower() in actual_key.lower()):
                        actual_game = actual
                        break
                
                if actual_game:
                    aligned_item = {
                        'date': date,
                        'prediction': prediction,
                        'actual': actual_game
                    }
                    aligned_data.append(aligned_item)
        
        self.historical_predictions = aligned_data
    
    def validate_score_predictions(self) -> ValidationResult:
        """Validate score prediction accuracy"""
        if not self.historical_predictions:
            return ValidationResult("ScoreModel", "No Data", 0, 0, 0, 0, 0, 0, 0, 0)
        
        predicted_scores = []
        actual_scores = []
        predicted_totals = []
        actual_totals = []
        predicted_wins = []
        actual_wins = []
        
        for item in self.historical_predictions:
            pred = item['prediction']
            actual = item['actual']
            
            if actual.get('away_score') is not None and actual.get('home_score') is not None:
                # Individual scores
                predicted_scores.extend([
                    pred.get('predicted_away_score', 0),
                    pred.get('predicted_home_score', 0)
                ])
                actual_scores.extend([
                    actual.get('away_score', 0),
                    actual.get('home_score', 0)
                ])
                
                # Totals
                predicted_totals.append(pred.get('predicted_total_runs', 0))
                actual_totals.append(actual.get('away_score', 0) + actual.get('home_score', 0))
                
                # Win predictions
                predicted_wins.append(pred.get('home_win_probability', 0.5) > 0.5)
                actual_wins.append(actual.get('home_score', 0) > actual.get('away_score', 0))
        
        # Calculate metrics
        mae_score = mean_absolute_error(actual_scores, predicted_scores) if actual_scores else 0
        rmse_score = np.sqrt(mean_squared_error(actual_scores, predicted_scores)) if actual_scores else 0
        total_mae = mean_absolute_error(actual_totals, predicted_totals) if actual_totals else 0
        win_accuracy = np.mean([p == a for p, a in zip(predicted_wins, actual_wins)]) if predicted_wins else 0
        
        result = ValidationResult(
            model_name="ScoreModel",
            validation_period=f"{len(self.historical_predictions)} games",
            mae_score=mae_score,
            rmse_score=rmse_score,
            win_accuracy=win_accuracy,
            total_accuracy=1.0 - (total_mae / np.mean(actual_totals)) if actual_totals else 0,
            betting_roi=0.0,  # Calculated separately
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            prediction_count=len(actual_scores)
        )
        
        logger.info(f"Score Validation - MAE: {mae_score:.2f}, RMSE: {rmse_score:.2f}, Win Accuracy: {win_accuracy:.3f}")
        return result
    
    def backtest_betting_strategy(self, strategy_name: str = "Conservative") -> BacktestResult:
        """Backtest betting strategy performance"""
        if not self.historical_predictions:
            return BacktestResult(strategy_name, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        total_bets = 0
        winning_bets = 0
        total_profit = 0.0
        bet_results = []
        
        for item in self.historical_predictions:
            pred = item['prediction']
            actual = item['actual']
            
            if actual.get('away_score') is None or actual.get('home_score') is None:
                continue
            
            # Get betting recommendations
            betting_recs = pred.get('comprehensive_details', {}).get('betting_recommendations', [])
            
            for rec in betting_recs:
                if not isinstance(rec, dict):
                    continue
                
                confidence = rec.get('confidence', 'MEDIUM')
                bet_type = rec.get('type', 'moneyline')
                
                # Apply strategy filters
                if strategy_name == "Conservative" and confidence != 'HIGH':
                    continue
                elif strategy_name == "Aggressive" and confidence == 'LOW':
                    continue
                
                # Simulate bet
                bet_amount = self._get_bet_amount(confidence, strategy_name)
                win_probability = self._calculate_win_probability(rec, pred, actual)
                odds = rec.get('odds', -110)
                
                total_bets += 1
                
                # Determine if bet won
                bet_won = self._evaluate_bet_outcome(rec, pred, actual)
                
                if bet_won:
                    winning_bets += 1
                    profit = self._calculate_profit(bet_amount, odds)
                    total_profit += profit
                    bet_results.append(profit)
                else:
                    total_profit -= bet_amount
                    bet_results.append(-bet_amount)
        
        # Calculate metrics
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        roi_percentage = (total_profit / (total_bets * 100)) * 100 if total_bets > 0 else 0
        
        profit_factor = 0
        if bet_results:
            wins = [r for r in bet_results if r > 0]
            losses = [abs(r) for r in bet_results if r < 0]
            if losses:
                profit_factor = sum(wins) / sum(losses)
        
        result = BacktestResult(
            strategy_name=strategy_name,
            total_bets=total_bets,
            winning_bets=winning_bets,
            total_profit=total_profit,
            roi_percentage=roi_percentage,
            win_rate=win_rate,
            average_odds=-110,  # Simplified
            profit_factor=profit_factor,
            largest_win=max(bet_results) if bet_results else 0,
            largest_loss=min(bet_results) if bet_results else 0
        )
        
        logger.info(f"Backtest {strategy_name} - Bets: {total_bets}, Win Rate: {win_rate:.3f}, ROI: {roi_percentage:.2f}%")
        return result
    
    def _get_bet_amount(self, confidence: str, strategy: str) -> float:
        """Get bet amount based on confidence and strategy"""
        base_amounts = {
            'Conservative': {'HIGH': 100, 'MEDIUM': 50, 'LOW': 25},
            'Aggressive': {'HIGH': 200, 'MEDIUM': 100, 'LOW': 50},
            'Moderate': {'HIGH': 150, 'MEDIUM': 75, 'LOW': 40}
        }
        
        return base_amounts.get(strategy, base_amounts['Moderate']).get(confidence, 50)
    
    def _calculate_win_probability(self, rec: Dict, pred: Dict, actual: Dict) -> float:
        """Calculate actual win probability for a bet"""
        bet_type = rec.get('type', 'moneyline')
        
        if bet_type == 'moneyline':
            if 'home' in rec.get('recommendation', '').lower():
                return 1.0 if actual.get('home_score', 0) > actual.get('away_score', 0) else 0.0
            else:
                return 1.0 if actual.get('away_score', 0) > actual.get('home_score', 0) else 0.0
        
        elif bet_type in ['over', 'under']:
            total_score = actual.get('home_score', 0) + actual.get('away_score', 0)
            line = rec.get('line', 8.5)
            
            if 'over' in rec.get('recommendation', '').lower():
                return 1.0 if total_score > line else 0.0
            else:
                return 1.0 if total_score < line else 0.0
        
        return 0.5  # Default for unknown bet types
    
    def _evaluate_bet_outcome(self, rec: Dict, pred: Dict, actual: Dict) -> bool:
        """Evaluate if a bet would have won"""
        return self._calculate_win_probability(rec, pred, actual) == 1.0
    
    def _calculate_profit(self, bet_amount: float, odds: int) -> float:
        """Calculate profit from winning bet"""
        if odds > 0:
            return bet_amount * (odds / 100)
        else:
            return bet_amount * (100 / abs(odds))
    
    def cross_validate_model(self, n_splits: int = 5) -> List[ValidationResult]:
        """Perform cross-validation on the model"""
        if not self.historical_predictions:
            return []
        
        # Sort by date for time series split
        sorted_data = sorted(self.historical_predictions, key=lambda x: x['date'])
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_results = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(sorted_data)):
            test_data = [sorted_data[i] for i in test_idx]
            
            # Temporarily set test data for validation
            original_data = self.historical_predictions
            self.historical_predictions = test_data
            
            # Validate on this fold
            fold_result = self.validate_score_predictions()
            fold_result.model_name = f"Fold_{fold + 1}"
            cv_results.append(fold_result)
            
            # Restore original data
            self.historical_predictions = original_data
        
        logger.info(f"Cross-validation complete - {n_splits} folds")
        return cv_results
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        if not self.load_validation_data():
            return "❌ Could not load validation data"
        
        # Run validations
        score_validation = self.validate_score_predictions()
        conservative_backtest = self.backtest_betting_strategy("Conservative")
        aggressive_backtest = self.backtest_betting_strategy("Aggressive")
        cv_results = self.cross_validate_model()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# MLB Prediction Model Validation Report
Generated: {timestamp}

## Executive Summary
This report provides comprehensive validation of the MLB prediction model using historical data and backtesting results.

## Score Prediction Validation
- **Mean Absolute Error**: {score_validation.mae_score:.2f} runs
- **Root Mean Square Error**: {score_validation.rmse_score:.2f} runs  
- **Win Prediction Accuracy**: {score_validation.win_accuracy:.1%}
- **Total Games Analyzed**: {score_validation.prediction_count}

### Performance Grade
"""
        
        # Calculate grade
        if score_validation.mae_score < 1.0 and score_validation.win_accuracy > 0.65:
            grade = "A - Excellent"
        elif score_validation.mae_score < 1.5 and score_validation.win_accuracy > 0.58:
            grade = "B - Good"  
        elif score_validation.mae_score < 2.0 and score_validation.win_accuracy > 0.52:
            grade = "C - Average"
        else:
            grade = "D - Needs Improvement"
        
        report += f"**{grade}**\n\n"
        
        # Betting strategy backtests
        report += "## Betting Strategy Backtests\n\n"
        
        report += f"### Conservative Strategy\n"
        report += f"- **Total Bets**: {conservative_backtest.total_bets}\n"
        report += f"- **Win Rate**: {conservative_backtest.win_rate:.1%}\n"
        report += f"- **ROI**: {conservative_backtest.roi_percentage:.2f}%\n"
        report += f"- **Total Profit**: ${conservative_backtest.total_profit:.2f}\n"
        report += f"- **Profit Factor**: {conservative_backtest.profit_factor:.2f}\n\n"
        
        report += f"### Aggressive Strategy\n"
        report += f"- **Total Bets**: {aggressive_backtest.total_bets}\n"
        report += f"- **Win Rate**: {aggressive_backtest.win_rate:.1%}\n"
        report += f"- **ROI**: {aggressive_backtest.roi_percentage:.2f}%\n"
        report += f"- **Total Profit**: ${aggressive_backtest.total_profit:.2f}\n"
        report += f"- **Profit Factor**: {aggressive_backtest.profit_factor:.2f}\n\n"
        
        # Cross-validation results
        if cv_results:
            report += "## Cross-Validation Results\n"
            avg_mae = np.mean([r.mae_score for r in cv_results])
            avg_win_acc = np.mean([r.win_accuracy for r in cv_results])
            std_mae = np.std([r.mae_score for r in cv_results])
            
            report += f"- **Average MAE**: {avg_mae:.2f} ± {std_mae:.2f}\n"
            report += f"- **Average Win Accuracy**: {avg_win_acc:.1%}\n"
            report += f"- **Model Stability**: {'High' if std_mae < 0.3 else 'Medium' if std_mae < 0.5 else 'Low'}\n\n"
        
        # Recommendations
        report += "## Recommendations\n"
        
        if score_validation.mae_score > 1.5:
            report += "- 🔧 **Score predictions need improvement** - Consider retuning pitcher impact weights\n"
        
        if score_validation.win_accuracy < 0.55:
            report += "- 🎯 **Win probability model needs calibration** - Review team strength calculations\n"
        
        if conservative_backtest.roi_percentage < 3:
            report += "- 💰 **Betting strategy underperforming** - Increase selectivity or adjust confidence thresholds\n"
        
        if aggressive_backtest.win_rate < 0.45:
            report += "- ⚡ **Aggressive strategy too risky** - Consider more conservative bet sizing\n"
        
        report += "\n## Next Steps\n"
        report += "1. Run parameter optimization based on validation results\n"
        report += "2. Implement recommended model adjustments\n"
        report += "3. Monitor performance with new parameters\n"
        report += "4. Schedule regular validation cycles\n"
        
        # Save report
        report_file = f"MLB-Betting/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Validation report saved to {report_file}")
        return report

def main():
    """Main validation execution"""
    print("🔍 MLB Model Validation System")
    print("="*45)
    
    validator = ModelValidator()
    
    # Generate comprehensive validation report
    print("📊 Running comprehensive validation...")
    report = validator.generate_validation_report()
    
    print("\n✅ Validation complete!")
    print("📋 Report generated with performance metrics and recommendations")

if __name__ == "__main__":
    main()
