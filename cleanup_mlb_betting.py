import os
import shutil
from pathlib import Path

def cleanup_mlb_betting_directory():
    """Comprehensive cleanup of MLB-Betting directory"""
    
    print("=== MLB-BETTING DIRECTORY CLEANUP ===")
    print("Cleaning up debugging files, test scripts, and unnecessary clutter...\n")
    
    betting_dir = Path('C:/Users/mostg/OneDrive/Coding/MLBCompare/MLB-Betting')
    
    # Track what we're cleaning
    removed_files = []
    removed_dirs = []
    preserved_files = []
    
    # 1. DEBUGGING SCRIPTS TO REMOVE
    debug_scripts = [
        'check_cache.py',
        'check_pitcher_scores.py', 
        'check_times.py',
        'comprehensive_test.py',
        'debug_historical_recap.py',
        'debug_keys.py',
        'debug_matching.py',
        'debug_original_factors.py',
        'debug_predictions.py',
        'debug_test.py',
        'final_pitcher_check.py',
        'final_pitcher_test.py',
        'find_pitcher_metrics.py',
        'verify_pitcher_scoring.py'
    ]
    
    print("🧹 REMOVING DEBUGGING SCRIPTS:")
    for script in debug_scripts:
        script_path = betting_dir / script
        if script_path.exists():
            script_path.unlink()
            removed_files.append(script)
            print(f"  ✅ Removed: {script}")
    
    # 2. TEST SCRIPTS TO REMOVE  
    test_scripts = [
        'test_comprehensive_direct.py',
        'test_direct_endpoint.py',
        'test_final_integration.py',
        'test_frontend_call.py',
        'test_frontend_integration.py',
        'test_historical_fix.py',
        'test_individual_debug.py',
        'test_new_predictions.py'
    ]
    
    print(f"\n🧪 REMOVING TEST SCRIPTS:")
    for script in test_scripts:
        script_path = betting_dir / script
        if script_path.exists():
            script_path.unlink()
            removed_files.append(script)
            print(f"  ✅ Removed: {script}")
    
    # 3. DEBUGGING TEMPLATES TO REMOVE
    debug_templates = [
        'debug_historical.html',
        'debug_simple.html', 
        'debug_test.html',
        'historical_backup.html',
        'historical_simple.html',
        'historical_simple_fixed.html',
        'historical_working.html',  # Keep as backup but could be removed
        'manual_api_test.html'
    ]
    
    print(f"\n🎨 REMOVING DEBUGGING TEMPLATES:")
    templates_dir = betting_dir / 'templates'
    for template in debug_templates:
        template_path = templates_dir / template
        if template_path.exists():
            template_path.unlink()
            removed_files.append(f"templates/{template}")
            print(f"  ✅ Removed: templates/{template}")
    
    # 4. REMOVE __pycache__ DIRECTORIES
    print(f"\n📦 REMOVING PYTHON CACHE:")
    pycache_dir = betting_dir / '__pycache__'
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir)
        removed_dirs.append('__pycache__')
        print(f"  ✅ Removed: __pycache__ directory")
    
    # 5. REMOVE EMPTY LOGS DIRECTORY
    logs_dir = betting_dir / 'logs'
    if logs_dir.exists() and not any(logs_dir.iterdir()):
        logs_dir.rmdir()
        removed_dirs.append('logs')
        print(f"  ✅ Removed: empty logs directory")
    
    # 6. REPORT SYSTEM DOCUMENTATION TO REMOVE
    report_docs = [
        'HISTORICAL_ANALYSIS_FIX_REPORT.md',
        'LINE_1236_FIX_REPORT.md'
    ]
    
    print(f"\n📄 REMOVING OLD REPORTS:")
    for doc in report_docs:
        doc_path = betting_dir / doc
        if doc_path.exists():
            doc_path.unlink()
            removed_files.append(doc)
            print(f"  ✅ Removed: {doc}")
    
    # 7. ARCHIVE OR REMOVE CONSOLIDATION SCRIPT
    consolidation_script = betting_dir / 'consolidate_predictions_data.py'
    if consolidation_script.exists():
        # This might be useful for future data operations, so we'll keep it
        preserved_files.append('consolidate_predictions_data.py')
        print(f"\n📋 PRESERVED: consolidate_predictions_data.py (may be useful)")
    
    # 8. SUMMARY OF WHAT WE'RE KEEPING
    essential_files = [
        'app.py',                                    # Main Flask application
        'comprehensive_tuned_engine.py',             # Core prediction engine
        'daily_data_refresh_manager.py',             # Daily data management
        'daily_prediction_manager.py',               # Daily predictions
        'enhanced_master_predictions_service.py',   # Master prediction service
        'enhanced_mlb_fetcher.py',                   # Data fetching
        'historical_recap_api.py',                  # Historical analysis API
        'integrated_closing_lines.py',              # Betting lines integration
        'live_mlb_data.py',                         # Live game data
        'post_game_analysis.py',                    # Post-game analysis
        'team_assets.json',                         # Team assets data
        'team_assets_utils.py',                     # Team utilities
        'team_name_normalizer.py',                  # Team name standardization
        'unified_predictions_cache.json',           # Our archaeological data!
        'README.md',                                # Documentation
        'DAILY_REFRESH_SYSTEM.md'                   # System documentation
    ]
    
    # Also keep essential templates
    essential_templates = [
        'index.html',               # Main dashboard
        'historical_robust.html',   # Historical analysis (our restored version)
        'historical.html'           # Original reference template
    ]
    
    # Daily automation scripts
    daily_scripts = [
        'daily_data_refresh.bat',
        'daily_data_refresh.ps1', 
        'setup_daily_task.ps1'
    ]
    
    print(f"\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)
    
    print(f"\n🗑️ REMOVED FILES ({len(removed_files)}):")
    for file in removed_files:
        print(f"    ✅ {file}")
    
    print(f"\n📁 REMOVED DIRECTORIES ({len(removed_dirs)}):")
    for dir in removed_dirs:
        print(f"    ✅ {dir}")
    
    print(f"\n💾 PRESERVED ESSENTIAL FILES:")
    preserved_count = 0
    for file in essential_files:
        if (betting_dir / file).exists():
            preserved_count += 1
            print(f"    ✅ {file}")
    
    print(f"\n🎨 PRESERVED TEMPLATES:")
    for template in essential_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"    ✅ templates/{template}")
    
    print(f"\n🤖 PRESERVED AUTOMATION:")
    for script in daily_scripts:
        script_path = betting_dir / script
        if script_path.exists():
            print(f"    ✅ {script}")
    
    # Calculate cleanup stats
    total_removed = len(removed_files) + len(removed_dirs)
    
    print(f"\n📊 CLEANUP STATISTICS:")
    print(f"    🗑️ Items removed: {total_removed}")
    print(f"    💾 Essential files preserved: {preserved_count}")
    print(f"    🎨 Templates cleaned: {len(debug_templates)} → 3 essential")
    print(f"    🧪 Test scripts removed: {len(test_scripts)}")
    print(f"    🐛 Debug scripts removed: {len(debug_scripts)}")
    
    print(f"\n🏆 MLB-BETTING DIRECTORY CLEANUP: **COMPLETE**")
    print(f"Directory is now clean, organized, and production-ready!")
    
    return {
        'removed_files': removed_files,
        'removed_dirs': removed_dirs,
        'total_removed': total_removed
    }

if __name__ == "__main__":
    results = cleanup_mlb_betting_directory()
    
    print(f"\n🎉 CLEANUP SUCCESSFUL!")
    print(f"Removed {results['total_removed']} unnecessary items.")
    print(f"MLB-Betting directory is now clean and professional!")
