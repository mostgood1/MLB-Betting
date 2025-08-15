"""
Post-game analysis module for historical betting analysis
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional

def analyze_final_game(prediction: Dict[str, Any], live_status: Dict[str, Any], betting_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a completed game for historical analysis purposes
    
    Args:
        prediction: The original prediction data
        live_status: Live game status information
        betting_data: Betting lines and odds data
        
    Returns:
        Dict containing comprehensive post-game analysis
    """
    try:
        analysis = {
            'game_completed': True,
            'analysis_timestamp': datetime.now().isoformat(),
            'prediction_accuracy': {},
            'betting_performance': {},
            'key_factors': [],
            'lessons_learned': []
        }
        
        # Extract game results from live status
        away_score = live_status.get('away_score', 0)
        home_score = live_status.get('home_score', 0)
        total_runs = away_score + home_score
        
        # Analyze prediction accuracy
        predicted_winner = prediction.get('predicted_winner', 'Unknown')
        actual_winner = 'away' if away_score > home_score else 'home' if home_score > away_score else 'tie'
        
        analysis['prediction_accuracy'] = {
            'predicted_winner': predicted_winner,
            'actual_winner': actual_winner,
            'winner_correct': predicted_winner == actual_winner,
            'predicted_total_runs': prediction.get('predicted_total_runs'),
            'actual_total_runs': total_runs,
            'total_runs_accuracy': _calculate_total_runs_accuracy(prediction.get('predicted_total_runs'), total_runs)
        }
        
        # Analyze betting performance if betting data available
        if betting_data:
            analysis['betting_performance'] = _analyze_betting_performance(
                prediction, live_status, betting_data, away_score, home_score, total_runs
            )
        
        # Identify key factors that influenced the game
        analysis['key_factors'] = _identify_key_factors(prediction, live_status, away_score, home_score)
        
        # Generate lessons learned for future predictions
        analysis['lessons_learned'] = _generate_lessons_learned(prediction, analysis['prediction_accuracy'])
        
        return analysis
        
    except Exception as e:
        return {
            'error': f"Error in post-game analysis: {str(e)}",
            'game_completed': True,
            'analysis_timestamp': datetime.now().isoformat()
        }

def _calculate_total_runs_accuracy(predicted: Optional[float], actual: int) -> Dict[str, Any]:
    """Calculate accuracy of total runs prediction"""
    if predicted is None:
        return {'accuracy': 'No prediction available'}
    
    difference = abs(predicted - actual)
    accuracy_percentage = max(0, 100 - (difference * 10))  # 10% penalty per run difference
    
    return {
        'difference': difference,
        'accuracy_percentage': round(accuracy_percentage, 1),
        'within_1_run': difference <= 1,
        'within_2_runs': difference <= 2
    }

def _analyze_betting_performance(prediction: Dict, live_status: Dict, betting_data: Dict, 
                                away_score: int, home_score: int, total_runs: int) -> Dict[str, Any]:
    """Analyze how betting recommendations performed"""
    performance = {
        'recommendations_analyzed': 0,
        'successful_bets': 0,
        'failed_bets': 0,
        'roi_analysis': {}
    }
    
    try:
        # Analyze moneyline performance
        if 'moneyline' in betting_data:
            ml_performance = _analyze_moneyline_performance(
                prediction, betting_data['moneyline'], away_score, home_score
            )
            performance['moneyline'] = ml_performance
            performance['recommendations_analyzed'] += 1
            if ml_performance.get('successful'):
                performance['successful_bets'] += 1
            else:
                performance['failed_bets'] += 1
        
        # Analyze total runs performance
        if 'totals' in betting_data:
            total_performance = _analyze_total_runs_performance(
                prediction, betting_data['totals'], total_runs
            )
            performance['totals'] = total_performance
            performance['recommendations_analyzed'] += 1
            if total_performance.get('successful'):
                performance['successful_bets'] += 1
            else:
                performance['failed_bets'] += 1
        
        # Calculate overall success rate
        if performance['recommendations_analyzed'] > 0:
            performance['success_rate'] = round(
                (performance['successful_bets'] / performance['recommendations_analyzed']) * 100, 1
            )
        
    except Exception as e:
        performance['error'] = f"Error analyzing betting performance: {str(e)}"
    
    return performance

def _analyze_moneyline_performance(prediction: Dict, moneyline_data: Dict, 
                                  away_score: int, home_score: int) -> Dict[str, Any]:
    """Analyze moneyline betting performance"""
    recommended_team = prediction.get('recommended_bet_team')
    if not recommended_team:
        return {'status': 'No moneyline recommendation made'}
    
    actual_winner = 'away' if away_score > home_score else 'home'
    successful = (recommended_team == actual_winner)
    
    return {
        'recommended_team': recommended_team,
        'actual_winner': actual_winner,
        'successful': successful,
        'confidence': prediction.get('confidence', 'Unknown')
    }

def _analyze_total_runs_performance(prediction: Dict, totals_data: Dict, actual_total: int) -> Dict[str, Any]:
    """Analyze total runs betting performance"""
    recommended_bet = prediction.get('recommended_total_bet')  # 'over' or 'under'
    line = totals_data.get('line', 0)
    
    if not recommended_bet or not line:
        return {'status': 'No total runs recommendation made'}
    
    actual_result = 'over' if actual_total > line else 'under'
    successful = (recommended_bet == actual_result)
    
    return {
        'recommended_bet': recommended_bet,
        'line': line,
        'actual_total': actual_total,
        'actual_result': actual_result,
        'successful': successful,
        'margin': abs(actual_total - line)
    }

def _identify_key_factors(prediction: Dict, live_status: Dict, away_score: int, home_score: int) -> list:
    """Identify key factors that influenced the game outcome"""
    factors = []
    
    # Score differential analysis
    score_diff = abs(away_score - home_score)
    if score_diff == 0:
        factors.append("Game ended in a tie")
    elif score_diff == 1:
        factors.append("Very close game decided by 1 run")
    elif score_diff >= 5:
        factors.append("Decisive victory with large score margin")
    
    # High/low scoring game analysis
    total_runs = away_score + home_score
    if total_runs >= 15:
        factors.append("High-scoring offensive game")
    elif total_runs <= 5:
        factors.append("Low-scoring pitchers' duel")
    
    # Pitcher performance if available
    if 'pitcher_stats' in live_status:
        factors.append("Pitcher performance data available for analysis")
    
    return factors

def _generate_lessons_learned(prediction: Dict, accuracy: Dict) -> list:
    """Generate lessons learned for improving future predictions"""
    lessons = []
    
    if not accuracy.get('winner_correct'):
        lessons.append("Review team strength calculations and recent performance factors")
    
    total_accuracy = accuracy.get('total_runs_accuracy', {})
    if isinstance(total_accuracy, dict) and not total_accuracy.get('within_2_runs'):
        lessons.append("Improve total runs prediction model - consider recent offensive trends")
    
    if prediction.get('confidence') == 'low' and accuracy.get('winner_correct'):
        lessons.append("Low confidence prediction was correct - review confidence threshold")
    
    return lessons

if __name__ == "__main__":
    # Test the module
    print("Post-game analysis module loaded successfully")
