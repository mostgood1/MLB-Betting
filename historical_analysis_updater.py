#!/usr/bin/env python3
"""
Historical Analysis Data Updater
================================

Update missing performance analysis data and final scores for historical games.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_analysis_updater.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HistoricalAnalysisUpdater')

class HistoricalAnalysisUpdater:
    """Update missing historical analysis data"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.cache_path = 'MLB-Betting/data/unified_predictions_cache.json'
        self.backup_path = f'MLB-Betting/data/unified_predictions_cache_analysis_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
    def load_cache(self) -> Dict[str, Any]:
        """Load the unified cache"""
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}
    
    def save_cache(self, cache_data: Dict[str, Any]) -> bool:
        """Save the updated cache"""
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated cache saved to: {self.cache_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False
    
    def create_backup(self, cache_data: Dict[str, Any]) -> bool:
        """Create backup of original cache"""
        try:
            with open(self.backup_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Backup created: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def get_live_game_status(self, away_team: str, home_team: str, date_str: str) -> Dict[str, Any]:
        """Get live game status from MLB API"""
        try:
            # Import the live MLB data module
            import sys
            sys.path.append('MLB-Betting')
            from live_mlb_data import get_live_game_status
            
            return get_live_game_status(away_team, home_team, date_str)
        except Exception as e:
            logger.error(f"Error getting live status for {away_team} @ {home_team}: {e}")
            return {}
    
    def calculate_performance_grade(self, prediction: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance analysis grade"""
        try:
            # Extract values with safe defaults
            pred_away = prediction.get('predicted_away_score', 0) or 0
            pred_home = prediction.get('predicted_home_score', 0) or 0
            
            actual_away = result.get('away_score', 0) or 0
            actual_home = result.get('home_score', 0) or 0
            
            pred_away_prob = prediction.get('away_win_probability', 0.5)
            pred_home_prob = prediction.get('home_win_probability', 0.5)
            
            # Winner accuracy
            pred_winner = 'away' if pred_away_prob > pred_home_prob else 'home'
            actual_winner = 'away' if actual_away > actual_home else 'home'
            winner_correct = pred_winner == actual_winner
            
            # Score accuracy
            away_score_diff = abs(actual_away - pred_away)
            home_score_diff = abs(actual_home - pred_home)
            avg_score_diff = (away_score_diff + home_score_diff) / 2
            
            # Calculate grade (0-100 scale)
            grade_points = 0
            
            # Winner prediction (50 points max)
            if winner_correct:
                grade_points += 50
            
            # Score accuracy (40 points max)
            if avg_score_diff == 0:
                grade_points += 40
            elif avg_score_diff <= 1:
                grade_points += 30
            elif avg_score_diff <= 2:
                grade_points += 20
            elif avg_score_diff <= 3:
                grade_points += 10
            
            # Confidence bonus (10 points max)
            max_confidence = max(pred_away_prob, pred_home_prob)
            confidence_bonus = min(10, (max_confidence - 0.5) * 20)
            grade_points += confidence_bonus
            
            # Convert to letter grade
            if grade_points >= 90:
                letter_grade = 'A+'
            elif grade_points >= 85:
                letter_grade = 'A'
            elif grade_points >= 80:
                letter_grade = 'B+'
            elif grade_points >= 75:
                letter_grade = 'B'
            elif grade_points >= 70:
                letter_grade = 'B-'
            elif grade_points >= 60:
                letter_grade = 'C'
            else:
                letter_grade = 'D'
            
            return {
                'overall_grade': letter_grade,
                'grade_percentage': round(grade_points, 1),
                'winner_correct': winner_correct,
                'score_accuracy': {
                    'away_diff': away_score_diff,
                    'home_diff': home_score_diff,
                    'avg_diff': round(avg_score_diff, 1)
                },
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance grade: {e}")
            return {
                'overall_grade': 'N/A',
                'grade_percentage': None,
                'status': 'Error calculating grade'
            }
    
    def update_missing_analysis_for_date(self, date_str: str, dry_run: bool = True) -> Dict[str, Any]:
        """Update missing analysis data for a specific date"""
        
        logger.info(f"Updating missing analysis for {date_str} (dry_run={dry_run})")
        
        # Load cache
        cache_data = self.load_cache()
        if not cache_data:
            return {'success': False, 'error': 'Failed to load cache'}
        
        # Create backup
        if not dry_run:
            self.create_backup(cache_data)
        
        predictions_by_date = cache_data.get('predictions_by_date', {})
        date_data = predictions_by_date.get(date_str, {})
        games_dict = date_data.get('games', {})
        
        if not games_dict:
            return {'success': False, 'error': f'No games found for {date_str}'}
        
        updates_made = 0
        analysis_added = 0
        scores_updated = 0
        errors = []
        
        for game_key, game_data in games_dict.items():
            try:
                away_team = game_data.get('away_team', '').replace('_', ' ')
                home_team = game_data.get('home_team', '').replace('_', ' ')
                
                # Get current live status
                live_status = self.get_live_game_status(away_team, home_team, date_str)
                
                # Update final scores if available
                if live_status.get('is_final') and live_status.get('away_score') is not None:
                    if 'result' not in game_data:
                        game_data['result'] = {}
                    
                    game_data['result'].update({
                        'away_score': live_status['away_score'],
                        'home_score': live_status['home_score'],
                        'is_final': True,
                        'status': 'Final'
                    })
                    scores_updated += 1
                    updates_made += 1
                    logger.info(f"  Updated final scores for {away_team} @ {home_team}")
                
                # Calculate performance analysis if missing or incomplete
                result = game_data.get('result', {})
                if result.get('is_final') and result.get('away_score') is not None:
                    
                    current_analysis = game_data.get('performance_analysis', {})
                    needs_analysis = (
                        not current_analysis or 
                        current_analysis.get('overall_grade') == 'N/A' or
                        current_analysis.get('grade_percentage') is None
                    )
                    
                    if needs_analysis:
                        prediction = game_data.get('prediction', game_data)  # Use game_data as fallback
                        
                        # Calculate new performance analysis
                        new_analysis = self.calculate_performance_grade(prediction, result)
                        game_data['performance_analysis'] = new_analysis
                        
                        analysis_added += 1
                        updates_made += 1
                        logger.info(f"  Added performance analysis for {away_team} @ {home_team}: {new_analysis['overall_grade']}")
                
            except Exception as e:
                error_msg = f"Error processing {game_key}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Update metadata
        if updates_made > 0:
            date_data['last_analysis_update'] = datetime.now().isoformat()
            date_data['analysis_update_count'] = date_data.get('analysis_update_count', 0) + updates_made
            
            if not dry_run:
                success = self.save_cache(cache_data)
                if not success:
                    return {'success': False, 'error': 'Failed to save updated cache'}
        
        return {
            'success': True,
            'date': date_str,
            'updates_made': updates_made,
            'analysis_added': analysis_added,
            'scores_updated': scores_updated,
            'errors': errors,
            'dry_run': dry_run
        }
    
    def update_date_range(self, start_date: str, end_date: str = None, dry_run: bool = True) -> Dict[str, Any]:
        """Update missing analysis for a date range"""
        
        if end_date is None:
            end_date = start_date
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        logger.info(f"Updating analysis for date range: {start_date} to {end_date}")
        
        total_updates = 0
        total_analysis_added = 0
        total_scores_updated = 0
        all_errors = []
        date_results = {}
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            result = self.update_missing_analysis_for_date(date_str, dry_run)
            date_results[date_str] = result
            
            if result['success']:
                total_updates += result['updates_made']
                total_analysis_added += result['analysis_added']
                total_scores_updated += result['scores_updated']
                all_errors.extend(result['errors'])
            
            current_dt += timedelta(days=1)
        
        return {
            'success': True,
            'date_range': f"{start_date} to {end_date}",
            'total_updates': total_updates,
            'total_analysis_added': total_analysis_added,
            'total_scores_updated': total_scores_updated,
            'total_errors': len(all_errors),
            'date_results': date_results,
            'dry_run': dry_run
        }

def main():
    """Main function to update historical analysis"""
    
    updater = HistoricalAnalysisUpdater()
    
    # Update through yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
    
    print(f"\n🔄 Historical Analysis Data Updater")
    print(f"Updating dates: {week_ago} to {yesterday}")
    print("=" * 60)
    
    print("⚠️  Note: Make sure your Flask app is running on localhost:5000")
    print("")
    
    try:
        # Run a dry run first
        print("🔍 Running dry run to check what needs updating...")
        dry_result = updater.update_date_range(week_ago, yesterday, dry_run=True)
        
        print(f"\nDry run results:")
        print(f"  Total updates needed: {dry_result['total_updates']}")
        print(f"  Analysis to add: {dry_result['total_analysis_added']}")
        print(f"  Scores to update: {dry_result['total_scores_updated']}")
        print(f"  Errors: {dry_result['total_errors']}")
        
        if dry_result['total_updates'] > 0:
            response = input(f"\nWould you like to apply these {dry_result['total_updates']} updates? (y/n): ")
            if response.lower() == 'y':
                print("\n🔄 Applying updates...")
                result = updater.update_date_range(week_ago, yesterday, dry_run=False)
                
                print(f"\n✅ Updates applied!")
                print(f"  Analysis added: {result['total_analysis_added']}")
                print(f"  Scores updated: {result['total_scores_updated']}")
                print(f"  Total changes: {result['total_updates']}")
                
                if result['total_errors'] > 0:
                    print(f"  ⚠️ Errors encountered: {result['total_errors']}")
            else:
                print("No updates applied.")
        else:
            print("\n✅ All historical analysis appears to be up to date!")
        
    except Exception as e:
        print(f"\n❌ Error during update: {e}")
        logger.error(f"Update failed: {e}")

if __name__ == "__main__":
    main()
