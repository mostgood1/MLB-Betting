#!/usr/bin/env python3
"""
Quick fix for OddsAPI data structure issue
"""

import json
import os

def fix_map_to_game_ids_function():
    """Fix the map_to_game_ids function in fetch_odds_api.py"""
    
    file_path = "fetch_odds_api.py"
    
    # Read the current file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"Could not read {file_path}")
        return False
    
    # Find and replace the problematic section
    old_section = """        # Get games for this date
        date_games = game_scores[date_str].get('games', [])"""
    
    new_section = """        # Get games for this date - handle both dict and list formats
        date_data = game_scores[date_str]
        if isinstance(date_data, dict):
            date_games = date_data.get('games', [])
        elif isinstance(date_data, list):
            date_games = date_data
        else:
            print(f"Unexpected data format for {date_str}: {type(date_data)}")
            return []"""
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        
        # Write the fixed content back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully fixed fetch_odds_api.py")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    else:
        print("Could not find the section to replace")
        return False

if __name__ == "__main__":
    fix_map_to_game_ids_function()
