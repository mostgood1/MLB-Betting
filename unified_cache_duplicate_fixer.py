#!/usr/bin/env python3
"""
Unified Cache Duplicate Fixer
============================

Fix duplicate games in the unified predictions cache that are causing
duplicates in the historical analysis frontend.
"""

import json
import os
from datetime import datetime
import logging
from typing import Dict, List, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_cache_duplicate_fix.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UnifiedCacheFixer')

class UnifiedCacheDuplicateFixer:
    """Fix duplicate games in unified cache"""
    
    def __init__(self):
        self.cache_path = 'MLB-Betting/data/unified_predictions_cache.json'
        self.backup_path = f'MLB-Betting/data/unified_predictions_cache_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
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
    
    def normalize_team_name(self, team_name: str) -> str:
        """Normalize team name by replacing underscores with spaces"""
        return team_name.replace('_', ' ').strip()
    
    def find_duplicate_games(self, cache_data: Dict[str, Any]) -> Dict[str, List]:
        """Find duplicate games in the cache"""
        
        duplicates_by_date = {}
        predictions_by_date = cache_data.get('predictions_by_date', {})
        
        for date_str, date_data in predictions_by_date.items():
            games = date_data.get('games', {})
            
            # Group games by normalized matchup
            normalized_games = defaultdict(list)
            
            for game_key, game_data in games.items():
                away_team = self.normalize_team_name(game_data.get('away_team', ''))
                home_team = self.normalize_team_name(game_data.get('home_team', ''))
                
                normalized_matchup = f"{away_team} @ {home_team}"
                normalized_games[normalized_matchup].append({
                    'original_key': game_key,
                    'game_data': game_data,
                    'away_team': away_team,
                    'home_team': home_team
                })
            
            # Find duplicates
            date_duplicates = []
            for matchup, game_list in normalized_games.items():
                if len(game_list) > 1:
                    date_duplicates.append({
                        'matchup': matchup,
                        'count': len(game_list),
                        'games': game_list
                    })
            
            if date_duplicates:
                duplicates_by_date[date_str] = date_duplicates
        
        return duplicates_by_date
    
    def merge_duplicate_games(self, duplicates: List[Dict]) -> Dict[str, Any]:
        """Merge duplicate games into a single best version"""
        
        if not duplicates:
            return {}
        
        # Choose the best game data (priority: most complete data, latest prediction time)
        best_game = None
        best_score = -1
        
        for game in duplicates:
            game_data = game['game_data']
            score = 0
            
            # Score based on data completeness
            if game_data.get('predicted_away_score') is not None:
                score += 10
            if game_data.get('predicted_home_score') is not None:
                score += 10
            if game_data.get('away_pitcher') and game_data['away_pitcher'] != 'TBD':
                score += 5
            if game_data.get('home_pitcher') and game_data['home_pitcher'] != 'TBD':
                score += 5
            if game_data.get('comprehensive_details'):
                score += 20
            if game_data.get('prediction_time'):
                score += 5
            
            # Prefer more recent predictions
            if game_data.get('prediction_time'):
                try:
                    pred_time = datetime.fromisoformat(game_data['prediction_time'].replace('Z', ''))
                    score += (pred_time.timestamp() / 1000000)  # Small bonus for newer
                except:
                    pass
            
            if score > best_score:
                best_score = score
                best_game = game
        
        # Create merged game with normalized team names
        merged_game = best_game['game_data'].copy()
        merged_game['away_team'] = best_game['away_team']
        merged_game['home_team'] = best_game['home_team']
        
        # Create normalized key
        normalized_key = f"{best_game['away_team']} @ {best_game['home_team']}"
        
        return {
            'key': normalized_key,
            'data': merged_game,
            'merged_from': [g['original_key'] for g in duplicates],
            'merge_score': best_score
        }
    
    def fix_duplicates(self, dry_run: bool = True) -> Dict[str, Any]:
        """Fix duplicate games in the cache"""
        
        logger.info(f"Starting duplicate fix (dry_run={dry_run})")
        
        # Load cache
        cache_data = self.load_cache()
        if not cache_data:
            logger.error("Failed to load cache data")
            return {}
        
        # Create backup
        if not dry_run:
            self.create_backup(cache_data)
        
        # Find duplicates
        duplicates_by_date = self.find_duplicate_games(cache_data)
        
        if not duplicates_by_date:
            logger.info("✅ No duplicates found!")
            return {
                'duplicates_found': 0,
                'dates_affected': 0,
                'games_removed': 0,
                'games_merged': 0
            }
        
        # Fix duplicates
        total_duplicates = 0
        total_removed = 0
        total_merged = 0
        
        for date_str, date_duplicates in duplicates_by_date.items():
            logger.info(f"\nProcessing duplicates for {date_str}:")
            
            games_dict = cache_data['predictions_by_date'][date_str]['games']
            
            for duplicate_group in date_duplicates:
                matchup = duplicate_group['matchup']
                games = duplicate_group['games']
                
                logger.info(f"  Fixing duplicate: {matchup} ({len(games)} copies)")
                
                # Merge the duplicates
                merged_result = self.merge_duplicate_games(games)
                
                if merged_result:
                    # Remove all original keys
                    for game in games:
                        if game['original_key'] in games_dict:
                            del games_dict[game['original_key']]
                            total_removed += 1
                    
                    # Add the merged game
                    games_dict[merged_result['key']] = merged_result['data']
                    total_merged += 1
                    
                    logger.info(f"    ✅ Merged into: {merged_result['key']}")
                    logger.info(f"    📝 Removed keys: {merged_result['merged_from']}")
                
                total_duplicates += 1
            
            # Update games count
            cache_data['predictions_by_date'][date_str]['games_count'] = len(games_dict)
        
        # Update metadata
        if 'metadata' not in cache_data:
            cache_data['metadata'] = {}
        
        cache_data['metadata']['last_duplicate_fix'] = datetime.now().isoformat()
        cache_data['metadata']['duplicates_fixed'] = total_duplicates
        cache_data['metadata']['games_merged'] = total_merged
        cache_data['metadata']['games_removed'] = total_removed
        
        # Save if not dry run
        if not dry_run:
            success = self.save_cache(cache_data)
            if success:
                logger.info("✅ Cache updated successfully!")
            else:
                logger.error("❌ Failed to save updated cache")
        else:
            logger.info("🔍 DRY RUN - No changes saved")
        
        return {
            'duplicates_found': total_duplicates,
            'dates_affected': len(duplicates_by_date),
            'games_removed': total_removed,
            'games_merged': total_merged,
            'dry_run': dry_run
        }
    
    def generate_report(self, fix_results: Dict[str, Any]) -> str:
        """Generate a report of the fix operation"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"unified_cache_duplicate_fix_report_{timestamp}.txt"
        
        lines = []
        lines.append("=" * 70)
        lines.append("UNIFIED CACHE DUPLICATE FIX REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Cache file: {self.cache_path}")
        lines.append("")
        
        lines.append("SUMMARY")
        lines.append("-" * 30)
        lines.append(f"Duplicates found: {fix_results['duplicates_found']}")
        lines.append(f"Dates affected: {fix_results['dates_affected']}")
        lines.append(f"Games removed: {fix_results['games_removed']}")
        lines.append(f"Games merged: {fix_results['games_merged']}")
        lines.append(f"Dry run: {fix_results['dry_run']}")
        
        if fix_results['dry_run']:
            lines.append("\n⚠️  This was a DRY RUN - no changes were made")
        else:
            lines.append(f"\n✅ Changes applied to cache")
            lines.append(f"Backup created: {self.backup_path}")
        
        # Save report
        report_content = "\n".join(lines)
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
        
        return report_content

def main():
    """Main function to run the duplicate fixer"""
    
    fixer = UnifiedCacheDuplicateFixer()
    
    print("🔧 Unified Cache Duplicate Fixer")
    print("=" * 50)
    
    # Check for duplicates first (dry run)
    print("Scanning for duplicates...")
    results = fixer.fix_duplicates(dry_run=True)
    
    print(f"\nScan Results:")
    print(f"  Duplicates found: {results['duplicates_found']}")
    print(f"  Dates affected: {results['dates_affected']}")
    print(f"  Games to remove: {results['games_removed']}")
    print(f"  Games to merge: {results['games_merged']}")
    
    if results['duplicates_found'] > 0:
        print(f"\n⚠️  Found {results['duplicates_found']} duplicate groups!")
        
        # Ask user if they want to fix
        response = input("\nWould you like to fix these duplicates? (y/n): ")
        if response.lower() == 'y':
            print("\nFixing duplicates...")
            fix_results = fixer.fix_duplicates(dry_run=False)
            
            # Generate report
            report = fixer.generate_report(fix_results)
            
            print(f"\n✅ Duplicates fixed!")
            print(f"  {fix_results['games_merged']} games merged")
            print(f"  {fix_results['games_removed']} duplicate entries removed")
            print(f"📝 Report generated")
        else:
            print("No changes made.")
    else:
        print("\n✅ No duplicates found!")

if __name__ == "__main__":
    main()
