#!/usr/bin/env python3

"""
MLB Team Name Normalization Utility
Provides consistent team name normalization across the entire application
"""

def normalize_team_name(team_name: str) -> str:
    """
    Normalize team names to match our internal naming convention.
    This function should be used throughout the application to ensure consistency.
    """
    if not team_name:
        return team_name
        
    # Strip whitespace and convert to title case for consistent comparison
    team_name = team_name.strip()
    
    # Dictionary of all possible team name variations to our standard names
    name_mappings = {
        # Athletics variations
        'Oakland Athletics': 'Athletics',
        'Oakland A\'s': 'Athletics',
        'Oakland As': 'Athletics',
        'A\'s': 'Athletics',
        'As': 'Athletics',
        'OAK': 'Athletics',
        
        # Angels variations
        'Los Angeles Angels': 'Angels',
        'Los Angeles Angels of Anaheim': 'Angels',
        'Anaheim Angels': 'Angels',
        'California Angels': 'Angels',
        'LAA': 'Angels',
        'ANA': 'Angels',
        
        # Dodgers variations
        'Los Angeles Dodgers': 'Dodgers',
        'LA Dodgers': 'Dodgers',
        'LAD': 'Dodgers',
        
        # Yankees variations
        'New York Yankees': 'Yankees',
        'NY Yankees': 'Yankees',
        'NYY': 'Yankees',
        
        # Mets variations
        'New York Mets': 'Mets',
        'NY Mets': 'Mets',
        'NYM': 'Mets',
        
        # White Sox variations
        'Chicago White Sox': 'White Sox',
        'CHW': 'White Sox',
        'CWS': 'White Sox',
        
        # Cubs variations
        'Chicago Cubs': 'Cubs',
        'CHC': 'Cubs',
        
        # Cardinals variations
        'St. Louis Cardinals': 'Cardinals',
        'Saint Louis Cardinals': 'Cardinals',
        'St Louis Cardinals': 'Cardinals',
        'STL': 'Cardinals',
        
        # Red Sox variations
        'Boston Red Sox': 'Red Sox',
        'BOS': 'Red Sox',
        
        # Blue Jays variations
        'Toronto Blue Jays': 'Blue Jays',
        'TOR': 'Blue Jays',
        'TBJ': 'Blue Jays',
        
        # Rays variations
        'Tampa Bay Rays': 'Rays',
        'Tampa Bay Devil Rays': 'Rays',
        'TB': 'Rays',
        'TBR': 'Rays',
        
        # Orioles variations
        'Baltimore Orioles': 'Orioles',
        'BAL': 'Orioles',
        
        # Guardians variations
        'Cleveland Guardians': 'Guardians',
        'Cleveland Indians': 'Guardians',  # Legacy name
        'CLE': 'Guardians',
        'CLG': 'Guardians',
        
        # Tigers variations
        'Detroit Tigers': 'Tigers',
        'DET': 'Tigers',
        
        # Royals variations
        'Kansas City Royals': 'Royals',
        'KC': 'Royals',
        'KCR': 'Royals',
        
        # Twins variations
        'Minnesota Twins': 'Twins',
        'MIN': 'Twins',
        
        # Astros variations
        'Houston Astros': 'Astros',
        'HOU': 'Astros',
        
        # Mariners variations
        'Seattle Mariners': 'Mariners',
        'SEA': 'Mariners',
        
        # Rangers variations
        'Texas Rangers': 'Rangers',
        'TEX': 'Rangers',
        
        # Braves variations
        'Atlanta Braves': 'Braves',
        'ATL': 'Braves',
        
        # Marlins variations
        'Miami Marlins': 'Marlins',
        'Florida Marlins': 'Marlins',  # Legacy name
        'MIA': 'Marlins',
        'FLA': 'Marlins',
        
        # Phillies variations
        'Philadelphia Phillies': 'Phillies',
        'PHI': 'Phillies',
        
        # Nationals variations
        'Washington Nationals': 'Nationals',
        'WAS': 'Nationals',
        'WSN': 'Nationals',
        
        # Diamondbacks variations
        'Arizona Diamondbacks': 'Diamondbacks',
        'ARI': 'Diamondbacks',
        'AZ': 'Diamondbacks',
        
        # Rockies variations
        'Colorado Rockies': 'Rockies',
        'COL': 'Rockies',
        
        # Padres variations
        'San Diego Padres': 'Padres',
        'SD': 'Padres',
        'SDP': 'Padres',
        
        # Giants variations
        'San Francisco Giants': 'Giants',
        'SF': 'Giants',
        'SFG': 'Giants',
        
        # Brewers variations
        'Milwaukee Brewers': 'Brewers',
        'MIL': 'Brewers',
        
        # Reds variations
        'Cincinnati Reds': 'Reds',
        'CIN': 'Reds',
        
        # Pirates variations
        'Pittsburgh Pirates': 'Pirates',
        'PIT': 'Pirates',
    }
    
    # Check for exact match first (case-sensitive)
    if team_name in name_mappings:
        return name_mappings[team_name]
    
    # Check for case-insensitive match
    for variant, standard in name_mappings.items():
        if team_name.lower() == variant.lower():
            return standard
    
    # If no mapping found, return the original name
    return team_name

def get_team_abbreviation(team_name: str) -> str:
    """Get the standard 3-letter abbreviation for a team"""
    # First normalize the team name
    normalized = normalize_team_name(team_name)
    
    # Mapping from normalized names to abbreviations
    abbreviations = {
        'Athletics': 'OAK',
        'Angels': 'LAA',
        'Dodgers': 'LAD',
        'Yankees': 'NYY',
        'Mets': 'NYM',
        'White Sox': 'CHW',
        'Cubs': 'CHC',
        'Cardinals': 'STL',
        'Red Sox': 'BOS',
        'Blue Jays': 'TOR',
        'Rays': 'TBR',
        'Orioles': 'BAL',
        'Guardians': 'CLE',
        'Tigers': 'DET',
        'Royals': 'KCR',
        'Twins': 'MIN',
        'Astros': 'HOU',
        'Mariners': 'SEA',
        'Rangers': 'TEX',
        'Braves': 'ATL',
        'Marlins': 'MIA',
        'Phillies': 'PHI',
        'Nationals': 'WSN',
        'Diamondbacks': 'ARI',
        'Rockies': 'COL',
        'Padres': 'SDP',
        'Giants': 'SFG',
        'Brewers': 'MIL',
        'Reds': 'CIN',
        'Pirates': 'PIT',
    }
    
    return abbreviations.get(normalized, 'UNK')

def get_standard_team_names():
    """Get a list of all standard team names used in the system"""
    return [
        'Athletics', 'Angels', 'Dodgers', 'Yankees', 'Mets', 'White Sox', 'Cubs',
        'Cardinals', 'Red Sox', 'Blue Jays', 'Rays', 'Orioles', 'Guardians',
        'Tigers', 'Royals', 'Twins', 'Astros', 'Mariners', 'Rangers', 'Braves',
        'Marlins', 'Phillies', 'Nationals', 'Diamondbacks', 'Rockies', 'Padres',
        'Giants', 'Brewers', 'Reds', 'Pirates'
    ]

def validate_team_name(team_name: str) -> bool:
    """Check if a team name can be normalized to a valid MLB team"""
    normalized = normalize_team_name(team_name)
    return normalized in get_standard_team_names()

# Usage examples and testing
if __name__ == "__main__":
    print("=== MLB Team Name Normalization Testing ===")
    
    test_cases = [
        'Oakland Athletics',
        'Oakland A\'s',
        'OAK',
        'Athletics',
        'Los Angeles Angels',
        'Anaheim Angels',
        'LAA',
        'New York Yankees',
        'Chicago White Sox',
        'St. Louis Cardinals',
        'Tampa Bay Rays',
        'Invalid Team Name'
    ]
    
    for test_name in test_cases:
        normalized = normalize_team_name(test_name)
        abbreviation = get_team_abbreviation(test_name)
        is_valid = validate_team_name(test_name)
        print(f"{test_name:20} -> {normalized:15} ({abbreviation}) [Valid: {is_valid}]")
