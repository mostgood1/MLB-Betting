"""
Automated Prediction Engine Tuning Workflow
==========================================

This script orchestrates the complete tuning process for the MLB prediction engine,
combining historical analysis, parameter optimization, and model validation.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import traceback

# Import our tuning modules
from prediction_engine_tuner import MLBPredictionTuner, TuningMetrics
from parameter_manager import ParameterManager, PredictionEngineConfig
from model_validator import ModelValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tuning_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedTuningWorkflow:
    """Orchestrates the complete automated tuning process"""
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = workspace_dir
        self.tuner = MLBPredictionTuner("data")
        self.param_manager = ParameterManager("data/prediction_config.json")
        self.validator = ModelValidator("data")
        
        self.workflow_results = {
            'start_time': None,
            'end_time': None,
            'steps_completed': [],
            'errors': [],
            'recommendations': [],
            'performance_improvement': {},
            'final_grade': None
        }
    
    def run_complete_workflow(self, optimization_level: str = "moderate") -> Dict[str, Any]:
        """
        Run the complete tuning workflow
        
        optimization_level: 'conservative', 'moderate', 'aggressive'
        """
        self.workflow_results['start_time'] = datetime.now().isoformat()
        
        try:
            print("🚀 Starting Automated MLB Prediction Engine Tuning")
            print("="*60)
            
            # Step 1: Load and analyze historical data
            print("\n📊 Step 1: Loading Historical Data...")
            if not self._load_historical_data():
                raise Exception("Failed to load historical data")
            
            # Step 2: Baseline performance analysis
            print("\n📈 Step 2: Analyzing Current Performance...")
            baseline_metrics = self._analyze_baseline_performance()
            
            # Step 3: Load current configuration
            print("\n⚙️ Step 3: Loading Current Configuration...")
            current_config = self._load_current_configuration()
            
            # Step 4: Run optimization algorithms
            print("\n🔧 Step 4: Running Parameter Optimization...")
            optimization_results = self._run_parameter_optimization(optimization_level)
            
            # Step 5: Validate optimized model
            print("\n✅ Step 5: Validating Optimized Model...")
            validation_results = self._validate_optimized_model()
            
            # Step 6: Generate recommendations
            print("\n💡 Step 6: Generating Recommendations...")
            recommendations = self._generate_comprehensive_recommendations(
                baseline_metrics, optimization_results, validation_results
            )
            
            # Step 7: Apply best parameters (if significant improvement)
            print("\n🎯 Step 7: Applying Optimizations...")
            application_results = self._apply_optimizations(recommendations, optimization_level)
            
            # Step 8: Final validation and reporting
            print("\n📋 Step 8: Final Validation and Reporting...")
            final_results = self._generate_final_report(
                baseline_metrics, recommendations, application_results
            )
            
            self.workflow_results['end_time'] = datetime.now().isoformat()
            self.workflow_results['final_grade'] = final_results.get('final_grade', 'UNKNOWN')
            
            print(f"\n✨ Tuning Workflow Complete!")
            print(f"🏆 Final Grade: {self.workflow_results['final_grade']}")
            print(f"⏱️ Total Time: {self._calculate_runtime()}")
            
            return self.workflow_results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            logger.error(traceback.format_exc())
            self.workflow_results['errors'].append(str(e))
            self.workflow_results['end_time'] = datetime.now().isoformat()
            return self.workflow_results
    
    def _load_historical_data(self) -> bool:
        """Load and validate historical data"""
        try:
            # Check if required files exist
            required_files = [
                'unified_predictions_cache.json',
                'game_scores_cache.json'
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                logger.warning(f"Missing files: {missing_files}")
                # Try to find files in different locations
                for file in missing_files:
                    alt_path = f"MLB-Betting/data/{file}"
                    if os.path.exists(alt_path):
                        logger.info(f"Found {file} in alternative location")
                    else:
                        logger.error(f"Could not find {file}")
                        return False
            
            # Load data into tuner
            historical_data = self.tuner.load_historical_data()
            
            if not historical_data:
                logger.error("No historical data loaded")
                return False
            
            completed_games = len([r for r in historical_data if r.actual_away_score is not None])
            logger.info(f"Loaded {len(historical_data)} predictions, {completed_games} with results")
            
            if completed_games < 10:
                logger.warning("Limited historical data may affect tuning quality")
            
            self.workflow_results['steps_completed'].append('historical_data_loaded')
            return True
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            self.workflow_results['errors'].append(f"Data loading failed: {e}")
            return False
    
    def _analyze_baseline_performance(self) -> TuningMetrics:
        """Analyze current model performance"""
        try:
            metrics = self.tuner.analyze_prediction_accuracy()
            
            logger.info("Baseline Performance Metrics:")
            logger.info(f"  Score MAE: {metrics.score_mae:.2f}")
            logger.info(f"  Win Accuracy: {metrics.win_probability_accuracy:.3f}")
            logger.info(f"  Betting ROI: {metrics.betting_roi:.2f}%")
            
            self.workflow_results['steps_completed'].append('baseline_analysis')
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing baseline: {e}")
            self.workflow_results['errors'].append(f"Baseline analysis failed: {e}")
            return TuningMetrics(0, 0, 0, 0, 0, 0)
    
    def _load_current_configuration(self) -> PredictionEngineConfig:
        """Load current parameter configuration"""
        try:
            config = self.param_manager.load_config()
            
            logger.info(f"Loaded configuration version {config.version}")
            logger.info(f"Performance grade: {config.performance_grade}")
            
            self.workflow_results['steps_completed'].append('config_loaded')
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.workflow_results['errors'].append(f"Config loading failed: {e}")
            return self.param_manager.create_default_config()
    
    def _run_parameter_optimization(self, level: str) -> Dict[str, Any]:
        """Run parameter optimization based on level"""
        try:
            # Get optimization parameters based on level
            optimization_params = {
                'conservative': {'max_adjustment': 0.1, 'iterations': 3},
                'moderate': {'max_adjustment': 0.2, 'iterations': 5},
                'aggressive': {'max_adjustment': 0.4, 'iterations': 10}
            }
            
            params = optimization_params.get(level, optimization_params['moderate'])
            
            # Run core optimization
            optimal_params = self.tuner.optimize_parameters()
            
            # Generate tuning recommendations
            recommendations = self.tuner.generate_tuning_recommendations()
            
            results = {
                'optimal_parameters': optimal_params,
                'recommendations': recommendations,
                'optimization_level': level,
                'max_adjustment': params['max_adjustment']
            }
            
            logger.info(f"Parameter optimization complete - Level: {level}")
            self.workflow_results['steps_completed'].append('optimization_complete')
            
            return results
            
        except Exception as e:
            logger.error(f"Error in parameter optimization: {e}")
            self.workflow_results['errors'].append(f"Optimization failed: {e}")
            return {}
    
    def _validate_optimized_model(self) -> Dict[str, Any]:
        """Validate the optimized model performance"""
        try:
            # Load validation data
            if not self.validator.load_validation_data():
                logger.warning("Could not load validation data")
                return {}
            
            # Run comprehensive validation
            score_validation = self.validator.validate_score_predictions()
            conservative_backtest = self.validator.backtest_betting_strategy("Conservative")
            aggressive_backtest = self.validator.backtest_betting_strategy("Aggressive")
            
            results = {
                'score_validation': score_validation,
                'conservative_backtest': conservative_backtest,
                'aggressive_backtest': aggressive_backtest
            }
            
            logger.info("Model validation complete")
            self.workflow_results['steps_completed'].append('validation_complete')
            
            return results
            
        except Exception as e:
            logger.error(f"Error in model validation: {e}")
            self.workflow_results['errors'].append(f"Validation failed: {e}")
            return {}
    
    def _generate_comprehensive_recommendations(self, baseline: TuningMetrics, 
                                              optimization: Dict, validation: Dict) -> List[Dict]:
        """Generate comprehensive tuning recommendations"""
        recommendations = []
        
        try:
            # Score accuracy recommendations
            if baseline.score_mae > 1.5:
                recommendations.append({
                    'type': 'parameter_adjustment',
                    'priority': 'HIGH',
                    'category': 'score_accuracy',
                    'description': 'Score predictions have high error - adjust pitcher weights',
                    'action': 'increase_pitcher_impact',
                    'adjustment': 1.2
                })
            
            # Win probability recommendations
            if baseline.win_probability_accuracy < 0.58:
                recommendations.append({
                    'type': 'model_enhancement',
                    'priority': 'HIGH',
                    'category': 'win_probability',
                    'description': 'Win probability accuracy is low - recalibrate model',
                    'action': 'recalibrate_win_model',
                    'adjustment': 1.15
                })
            
            # Betting ROI recommendations
            if baseline.betting_roi < 3.0:
                recommendations.append({
                    'type': 'strategy_adjustment',
                    'priority': 'MEDIUM',
                    'category': 'betting_roi',
                    'description': 'Betting ROI below target - increase selectivity',
                    'action': 'increase_confidence_threshold',
                    'adjustment': 1.1
                })
            
            # Add optimization-specific recommendations
            if optimization.get('recommendations'):
                for action in optimization['recommendations'].get('immediate_actions', []):
                    recommendations.append({
                        'type': 'immediate_action',
                        'priority': 'HIGH',
                        'category': 'optimization',
                        'description': action,
                        'action': 'apply_optimization',
                        'adjustment': 1.0
                    })
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            self.workflow_results['recommendations'] = recommendations
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _apply_optimizations(self, recommendations: List[Dict], level: str) -> Dict[str, Any]:
        """Apply optimization recommendations to configuration"""
        try:
            applied_changes = []
            
            # Create tuning results for parameter manager
            tuning_results = {
                'parameter_adjustments': {},
                'performance_grade': 'TUNED'
            }
            
            for rec in recommendations:
                if rec['type'] == 'parameter_adjustment':
                    param_key = rec.get('action', 'unknown')
                    adjustment = rec.get('adjustment', 1.0)
                    
                    # Map actions to parameter adjustments
                    if param_key == 'increase_pitcher_impact':
                        tuning_results['parameter_adjustments']['pitcher_impact_weight'] = adjustment
                    elif param_key == 'recalibrate_win_model':
                        tuning_results['parameter_adjustments']['win_prob_calibration'] = adjustment
                    elif param_key == 'increase_confidence_threshold':
                        tuning_results['parameter_adjustments']['confidence_threshold'] = adjustment
                    
                    applied_changes.append(rec['description'])
            
            # Apply to parameter manager if significant changes
            if tuning_results['parameter_adjustments']:
                success = self.param_manager.apply_tuning_results(tuning_results)
                
                if success:
                    logger.info(f"Applied {len(applied_changes)} optimizations")
                else:
                    logger.warning("Failed to apply some optimizations")
            
            results = {
                'applied_changes': applied_changes,
                'tuning_results': tuning_results,
                'success': len(applied_changes) > 0
            }
            
            self.workflow_results['steps_completed'].append('optimizations_applied')
            return results
            
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
            self.workflow_results['errors'].append(f"Optimization application failed: {e}")
            return {'applied_changes': [], 'success': False}
    
    def _generate_final_report(self, baseline: TuningMetrics, 
                              recommendations: List[Dict], 
                              application: Dict) -> Dict[str, Any]:
        """Generate final tuning report"""
        try:
            # Calculate final grade
            if baseline.score_mae < 1.0 and baseline.win_probability_accuracy > 0.65:
                final_grade = "A - Excellent"
            elif baseline.score_mae < 1.5 and baseline.win_probability_accuracy > 0.58:
                final_grade = "B - Good"
            elif baseline.score_mae < 2.0 and baseline.win_probability_accuracy > 0.52:
                final_grade = "C - Average"
            else:
                final_grade = "D - Needs Improvement"
            
            # Create comprehensive report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_content = f"""
# Automated Tuning Workflow Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Workflow Summary
- **Start Time**: {self.workflow_results['start_time']}
- **End Time**: {self.workflow_results['end_time']}
- **Runtime**: {self._calculate_runtime()}
- **Steps Completed**: {len(self.workflow_results['steps_completed'])}
- **Errors Encountered**: {len(self.workflow_results['errors'])}

## Performance Analysis
- **Score MAE**: {baseline.score_mae:.2f} runs
- **Win Accuracy**: {baseline.win_probability_accuracy:.1%}
- **Betting ROI**: {baseline.betting_roi:.2f}%
- **Overall Grade**: {final_grade}

## Optimizations Applied
"""
            
            for change in application.get('applied_changes', []):
                report_content += f"- {change}\n"
            
            report_content += f"""
## Recommendations Generated
Total: {len(recommendations)} recommendations

### High Priority
"""
            high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
            for rec in high_priority:
                report_content += f"- {rec.get('description', 'Unknown')}\n"
            
            report_content += """
## Next Steps
1. Monitor performance with new parameters
2. Schedule next tuning cycle in 7 days  
3. Validate improvements with live predictions
4. Consider additional data sources if performance is still suboptimal

## Files Generated
- Configuration updated with optimized parameters
- Validation report with detailed metrics
- This comprehensive workflow report
"""
            
            # Save report
            report_file = f"MLB-Betting/tuning_workflow_report_{timestamp}.md"
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            results = {
                'final_grade': final_grade,
                'report_file': report_file,
                'report_content': report_content,
                'baseline_metrics': baseline,
                'recommendations_count': len(recommendations),
                'optimizations_applied': len(application.get('applied_changes', []))
            }
            
            logger.info(f"Final report saved to {report_file}")
            self.workflow_results['steps_completed'].append('final_report_generated')
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            return {'final_grade': 'ERROR', 'report_file': None}
    
    def _calculate_runtime(self) -> str:
        """Calculate workflow runtime"""
        try:
            if self.workflow_results['start_time'] and self.workflow_results['end_time']:
                start = datetime.fromisoformat(self.workflow_results['start_time'])
                end = datetime.fromisoformat(self.workflow_results['end_time'])
                duration = end - start
                
                minutes = int(duration.total_seconds() // 60)
                seconds = int(duration.total_seconds() % 60)
                
                return f"{minutes}m {seconds}s"
            else:
                return "Unknown"
        except:
            return "Error calculating runtime"

def main():
    """Main entry point for automated tuning"""
    print("🤖 MLB Prediction Engine - Automated Tuning System")
    print("="*55)
    
    # Get optimization level from user
    print("\nSelect optimization level:")
    print("1. Conservative (minimal changes, safe)")
    print("2. Moderate (balanced approach)")  
    print("3. Aggressive (maximum optimization)")
    
    choice = input("\nEnter choice (1-3) [default: 2]: ").strip()
    
    level_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
    optimization_level = level_map.get(choice, 'moderate')
    
    print(f"\n🎯 Running {optimization_level} optimization...")
    
    # Initialize and run workflow
    workflow = AutomatedTuningWorkflow()
    results = workflow.run_complete_workflow(optimization_level)
    
    # Display summary
    print("\n" + "="*55)
    print("📊 TUNING WORKFLOW SUMMARY")
    print("="*55)
    
    print(f"🏆 Final Grade: {results.get('final_grade', 'Unknown')}")
    print(f"⏱️  Runtime: {workflow._calculate_runtime()}")
    print(f"✅ Steps Completed: {len(results.get('steps_completed', []))}")
    print(f"💡 Recommendations: {len(results.get('recommendations', []))}")
    
    if results.get('errors'):
        print(f"❌ Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"   - {error}")
    
    print("\n🎉 Automated tuning complete!")
    print("📋 Check the generated reports for detailed analysis")

if __name__ == "__main__":
    main()
