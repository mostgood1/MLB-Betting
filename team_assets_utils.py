#!/usr/bin/env python3

"""
MLB Team Logo and Color Utilities
Provides team logo URLs, colors, and styling functions for the web interface
"""

import json
import os
from typing import Dict, Optional, Any
import json
import os
from typing import Dict, Optional, Any

# Define the team assets manager class inline to avoid circular imports
class MLBTeamAssets:
    """Team assets manager singleton for MLB logos and colors"""
    
    def __init__(self):
        """Initialize the team assets manager"""
        self._assets = {}
        self._load_assets()
    
    def _load_assets(self):
        """Load team assets from JSON files"""
        # Try different possible locations for the team assets
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'team_assets.json'),
            os.path.join(os.path.dirname(__file__), '..', 'team_assets.json'),
            os.path.join(os.path.dirname(__file__), 'mlb-clean-deploy', 'team_assets.json')
        ]
        
        # Use the first path that exists
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self._assets = json.load(f)
                    print(f"✓ Team assets loaded from {path}")
                    break
                except Exception as e:
                    print(f"⚠ Error loading team assets from {path}: {str(e)}")
        else:
            print("⚠ No team assets file found!")
    
    def get_team_assets(self, team_name: str) -> Dict[str, Any]:
        """Get the assets for a specific team"""
        # Try to find the team by exact name
        if team_name in self._assets:
            return self._assets[team_name]
        
        # Try to find the team by case-insensitive match
        for name, assets in self._assets.items():
            if name.lower() == team_name.lower():
                return assets
        
        # Try to find the team by abbreviation
        for name, assets in self._assets.items():
            if assets.get('abbreviation', '').lower() == team_name.lower():
                return assets
        
        # If no match found, return None
        return None
    
    def get_all_team_assets(self) -> Dict[str, Dict[str, Any]]:
        """Get all team assets"""
        return self._assets

# Initialize the team assets manager as a singleton
_team_assets_manager = MLBTeamAssets()

def load_team_assets() -> Dict[str, Any]:
    """Load team assets from the manager"""
    return _team_assets_manager.get_all_team_assets()

def get_team_assets(team_name: str) -> Dict[str, Any]:
    """Get team assets (logo, colors) for a given team name"""
    if not team_name:
        return get_default_team_assets()
    
    # Use the team assets manager to get the team's assets
    team_assets = _team_assets_manager.get_team_assets(team_name)
    
    # If the team assets manager found a match, return it
    if team_assets:
        # Make sure it has all the required keys with default fallbacks
        if 'logo_url' not in team_assets and 'logo' in team_assets:
            team_assets['logo_url'] = team_assets['logo']
            
        if 'primary_color' not in team_assets and 'colors' in team_assets:
            team_assets['primary_color'] = team_assets['colors'].get('primary', '#333333')
            
        if 'secondary_color' not in team_assets and 'colors' in team_assets:
            team_assets['secondary_color'] = team_assets['colors'].get('secondary', '#666666')
            
        if 'text_color' not in team_assets:
            team_assets['text_color'] = '#FFFFFF'
            
        if 'bg_color' not in team_assets:
            team_assets['bg_color'] = team_assets.get('primary_color', '#333333')
            
        return team_assets
            
    # Return default if no match found
    print(f"⚠ Team assets not found for: {team_name}")
    return get_default_team_assets(team_name)

def get_default_team_assets(team_name: str = "Unknown") -> Dict[str, Any]:
    """Get default team assets for when a team is not found"""
    return {
        'name': team_name,
        'logo': '/static/default_team_logo.png',
        'logo_url': '/static/default_team_logo.png',
        'primary_color': '#333333',
        'secondary_color': '#666666',
        'text_color': '#FFFFFF',
        'bg_color': '#333333'
    }

def get_team_logo(team_name: str) -> str:
    """Get just the team logo URL for a team"""
    assets = get_team_assets(team_name)
    return assets.get('logo_url', '/static/default_team_logo.png')

def get_team_primary_color(team_name: str) -> str:
    """Get just the primary color for a team"""
    assets = get_team_assets(team_name)
    return assets.get('primary_color', '#333333')

def get_team_secondary_color(team_name: str) -> str:
    """Get just the secondary color for a team"""
    assets = get_team_assets(team_name)
    return assets.get('secondary_color', '#666666')

def get_team_css(team_name: str) -> str:
    """Get CSS styling for a team"""
    assets = get_team_assets(team_name)
    primary = assets.get('primary_color', '#333333')
    secondary = assets.get('secondary_color', '#666666')
    text = assets.get('text_color', '#FFFFFF')
    
    return f"background-color: {primary}; color: {text}; border-color: {secondary};"

def get_team_card_html(team: str, include_logo: bool = True) -> str:
    """Generate HTML for a team card with logo and styling"""
    try:
        assets = get_team_assets(team)
        logo = assets.get('logo_url', '')
        name = assets.get('name', team)
        style = get_team_css(team)
        
        if include_logo and logo:
            logo_html = f'<img src="{logo}" alt="{name}" class="team-logo" />'
        else:
            logo_html = ''
            
        return f'<div class="team-card" style="{style}">{logo_html}<span>{name}</span></div>'
    except Exception as e:
        print(f"Error generating team card: {str(e)}")
        return f'<div class="team-card default">{team}</div>'

def get_teams_comparison_html(away_team: str, home_team: str) -> str:
    """Generate HTML for a teams comparison (away @ home)"""
    away_card = get_team_card_html(away_team)
    home_card = get_team_card_html(home_team)
    
    return f'<div class="game-matchup">{away_card}<span class="at-symbol">@</span>{home_card}</div>'
