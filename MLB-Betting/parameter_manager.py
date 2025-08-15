"""
Advanced Parameter Configuration System for MLB Prediction Engine
===============================================================

This module manages and optimizes all configurable parameters for the prediction engine.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class PitcherParameters:
    """Parameters for pitcher impact calculation"""
    era_weight: float = 0.35
    whip_weight: float = 0.25
    k9_weight: float = 0.20
    home_away_adjustment: float = 0.15
    rest_days_factor: float = 0.05
    recent_form_weight: float = 0.30
    career_vs_team_weight: float = 0.25
    
    # Thresholds for pitcher quality tiers
    ace_era_threshold: float = 3.00
    good_era_threshold: float = 3.75
    average_era_threshold: float = 4.50
    
    # Impact multipliers
    ace_run_impact: float = -0.8
    good_run_impact: float = -0.4
    average_run_impact: float = 0.0
    poor_run_impact: float = 0.6

@dataclass
class TeamParameters:
    """Parameters for team strength calculation"""
    offensive_runs_weight: float = 0.40
    defensive_runs_weight: float = 0.35
    recent_form_weight: float = 0.25
    home_field_advantage: float = 0.15
    
    # Streak modifiers
    win_streak_bonus: float = 0.05
    loss_streak_penalty: float = -0.05
    max_streak_impact: float = 0.25
    
    # Head-to-head factors
    h2h_weight: float = 0.20
    division_rival_adjustment: float = 0.10

@dataclass
class GameSituationParameters:
    """Parameters for game situation factors"""
    day_game_adjustment: float = -0.05
    night_game_adjustment: float = 0.0
    double_header_fatigue: float = -0.10
    
    # Weather impacts (when available)
    wind_speed_impact: float = 0.02  # per mph
    temperature_impact: float = 0.005  # per degree over 70F
    dome_adjustment: float = 0.0
    
    # Series position
    series_opener_adjustment: float = 0.02
    series_finale_adjustment: float = -0.02

@dataclass
class BettingParameters:
    """Parameters for betting recommendation generation"""
    # Confidence thresholds
    high_confidence_threshold: float = 0.65
    medium_confidence_threshold: float = 0.55
    
    # Edge requirements
    minimum_edge_percentage: float = 5.0
    strong_edge_percentage: float = 10.0
    
    # Bet sizing
    conservative_bet_percentage: float = 1.0
    aggressive_bet_percentage: float = 3.0
    max_bet_percentage: float = 5.0
    
    # ROI targets
    target_roi_percentage: float = 8.0
    minimum_roi_percentage: float = 3.0

@dataclass
class AdvancedParameters:
    """Advanced parameters for model fine-tuning"""
    # Uncertainty factors
    uncertainty_scaling: float = 1.0
    model_ensemble_weights: List[float] = None
    
    # Regression to mean
    regression_factor: float = 0.15
    
    # Sample size adjustments
    minimum_sample_size: int = 10
    sample_size_scaling: float = 0.1
    
    # Outlier handling
    outlier_threshold_std: float = 2.5
    outlier_dampening: float = 0.7
    
    def __post_init__(self):
        if self.model_ensemble_weights is None:
            self.model_ensemble_weights = [0.4, 0.35, 0.25]  # Base, Advanced, ML weights

@dataclass
class PredictionEngineConfig:
    """Complete configuration for the prediction engine"""
    pitcher: PitcherParameters
    team: TeamParameters
    game_situation: GameSituationParameters
    betting: BettingParameters
    advanced: AdvancedParameters
    
    # Meta parameters
    version: str = "1.0"
    last_updated: str = ""
    performance_grade: str = "UNTESTED"
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

class ParameterManager:
    """Manages parameter loading, saving, and optimization"""
    
    def __init__(self, config_file: str = "MLB-Betting/data/prediction_config.json"):
        self.config_file = config_file
        self.config: Optional[PredictionEngineConfig] = None
        self.backup_configs: List[PredictionEngineConfig] = []
    
    def load_config(self) -> PredictionEngineConfig:
        """Load configuration from file or create default"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Convert dict to dataclass
            config = PredictionEngineConfig(
                pitcher=PitcherParameters(**data.get('pitcher', {})),
                team=TeamParameters(**data.get('team', {})),
                game_situation=GameSituationParameters(**data.get('game_situation', {})),
                betting=BettingParameters(**data.get('betting', {})),
                advanced=AdvancedParameters(**data.get('advanced', {})),
                version=data.get('version', '1.0'),
                last_updated=data.get('last_updated', ''),
                performance_grade=data.get('performance_grade', 'UNTESTED')
            )
            
            self.config = config
            logger.info(f"Loaded configuration version {config.version}")
            return config
            
        except FileNotFoundError:
            logger.info("No configuration file found, creating default")
            return self.create_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.create_default_config()
    
    def create_default_config(self) -> PredictionEngineConfig:
        """Create default configuration"""
        config = PredictionEngineConfig(
            pitcher=PitcherParameters(),
            team=TeamParameters(),
            game_situation=GameSituationParameters(),
            betting=BettingParameters(),
            advanced=AdvancedParameters()
        )
        
        self.config = config
        self.save_config()
        logger.info("Created default configuration")
        return config
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        if not self.config:
            logger.error("No configuration to save")
            return False
        
        try:
            # Update timestamp
            self.config.last_updated = datetime.now().isoformat()
            
            # Convert to dict for JSON serialization
            config_dict = asdict(self.config)
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def backup_current_config(self) -> None:
        """Create backup of current configuration"""
        if self.config:
            self.backup_configs.append(self.config)
            # Keep only last 5 backups
            if len(self.backup_configs) > 5:
                self.backup_configs = self.backup_configs[-5:]
    
    def apply_tuning_results(self, tuning_results: Dict[str, Any]) -> bool:
        """Apply tuning results to configuration"""
        if not self.config:
            self.load_config()
        
        self.backup_current_config()
        
        try:
            # Apply parameter adjustments
            adjustments = tuning_results.get('parameter_adjustments', {})
            
            if 'pitcher_impact_weight' in adjustments:
                self.config.pitcher.era_weight *= adjustments['pitcher_impact_weight']
                self.config.pitcher.whip_weight *= adjustments['pitcher_impact_weight']
            
            if 'score_variance_reduction' in adjustments:
                self.config.team.recent_form_weight *= adjustments['score_variance_reduction']
                self.config.advanced.regression_factor *= adjustments['score_variance_reduction']
            
            if 'win_prob_calibration' in adjustments:
                self.config.betting.high_confidence_threshold *= adjustments['win_prob_calibration']
                self.config.betting.medium_confidence_threshold *= adjustments['win_prob_calibration']
            
            # Update version and performance grade
            old_version = float(self.config.version)
            self.config.version = f"{old_version + 0.1:.1f}"
            self.config.performance_grade = tuning_results.get('performance_grade', 'TUNED')
            
            self.save_config()
            logger.info(f"Applied tuning results, updated to version {self.config.version}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying tuning results: {e}")
            # Restore from backup
            if self.backup_configs:
                self.config = self.backup_configs[-1]
            return False
    
    def optimize_for_metric(self, metric_name: str, target_value: float) -> bool:
        """Optimize configuration for specific metric"""
        if not self.config:
            self.load_config()
        
        self.backup_current_config()
        
        optimizations = {
            'score_accuracy': {
                'pitcher.era_weight': 0.4,
                'pitcher.recent_form_weight': 0.35,
                'team.offensive_runs_weight': 0.45,
                'advanced.regression_factor': 0.2
            },
            'win_probability': {
                'team.recent_form_weight': 0.3,
                'pitcher.era_weight': 0.3,
                'team.home_field_advantage': 0.2,
                'game_situation.series_position': 0.05
            },
            'betting_roi': {
                'betting.minimum_edge_percentage': 7.0,
                'betting.high_confidence_threshold': 0.7,
                'betting.conservative_bet_percentage': 1.5
            }
        }
        
        if metric_name not in optimizations:
            logger.warning(f"No optimization profile for metric: {metric_name}")
            return False
        
        try:
            profile = optimizations[metric_name]
            
            for param_path, value in profile.items():
                parts = param_path.split('.')
                obj = self.config
                
                # Navigate to the correct object
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                
                # Set the value
                setattr(obj, parts[-1], value)
            
            # Update version
            old_version = float(self.config.version)
            self.config.version = f"{old_version + 0.1:.1f}"
            self.config.performance_grade = f"OPTIMIZED_FOR_{metric_name.upper()}"
            
            self.save_config()
            logger.info(f"Optimized configuration for {metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing configuration: {e}")
            if self.backup_configs:
                self.config = self.backup_configs[-1]
            return False
    
    def get_parameter_summary(self) -> Dict[str, Any]:
        """Get summary of current parameters"""
        if not self.config:
            self.load_config()
        
        return {
            'version': self.config.version,
            'last_updated': self.config.last_updated,
            'performance_grade': self.config.performance_grade,
            'key_parameters': {
                'pitcher_era_weight': self.config.pitcher.era_weight,
                'team_offense_weight': self.config.team.offensive_runs_weight,
                'home_field_advantage': self.config.team.home_field_advantage,
                'high_confidence_threshold': self.config.betting.high_confidence_threshold,
                'minimum_edge_percentage': self.config.betting.minimum_edge_percentage
            },
            'backup_count': len(self.backup_configs)
        }

def create_parameter_optimization_schedule() -> Dict[str, Any]:
    """Create a schedule for systematic parameter optimization"""
    return {
        'daily_micro_adjustments': {
            'description': 'Small daily adjustments based on previous day results',
            'frequency': 'daily',
            'parameters': ['pitcher.recent_form_weight', 'team.recent_form_weight'],
            'max_adjustment': 0.05
        },
        'weekly_performance_review': {
            'description': 'Weekly analysis and moderate adjustments',
            'frequency': 'weekly',
            'parameters': ['pitcher.era_weight', 'team.offensive_runs_weight', 'betting.confidence_thresholds'],
            'max_adjustment': 0.15
        },
        'monthly_comprehensive_tuning': {
            'description': 'Full parameter optimization using ML techniques',
            'frequency': 'monthly',
            'parameters': 'all',
            'max_adjustment': 0.30
        },
        'seasonal_major_updates': {
            'description': 'Major model updates at season start/end',
            'frequency': 'seasonal',
            'parameters': 'all',
            'max_adjustment': 0.50
        }
    }

if __name__ == "__main__":
    # Example usage
    manager = ParameterManager()
    config = manager.load_config()
    
    print("🎛️ Parameter Manager Demo")
    print("="*40)
    print(f"Configuration Version: {config.version}")
    print(f"Performance Grade: {config.performance_grade}")
    print(f"Last Updated: {config.last_updated}")
    
    summary = manager.get_parameter_summary()
    print("\n📊 Key Parameters:")
    for param, value in summary['key_parameters'].items():
        print(f"  {param}: {value}")
    
    print("\n✅ Parameter management system ready!")
