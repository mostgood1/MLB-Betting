# MLB API Integration System

This system integrates MLB API as the source of truth for all MLB game data in our prediction and analysis system. It ensures all games have official MLB Game IDs, starting pitcher information, and maintains data consistency across all system files.

## System Components

### 1. MLB API Integration (`mlb_api_integration.py`)

Fetches official game data from the MLB API and updates our system files:

- Retrieves official game IDs, team names, and pitcher information
- Updates game statuses and scores for completed games
- Saves data in both normalized format and game scores format
- Handles date ranges for batch processing

### 2. Data Deduplication (`deduplicate_date_range.py`)

Ensures data consistency by removing duplicate game entries:

- Removes duplicate game entries from game_scores_cache.json
- Keeps the most complete record when duplicates are found
- Updates game counts and completion status
- Synchronizes game IDs across all files

### 3. Data Synchronization (`synchronize_mlb_data.py`)

Ensures all system components use the same MLB data:

- Synchronizes game IDs across all data files
- Updates pitcher information in all relevant files
- Standardizes team names to handle different formats
- Validates data consistency and reports inconsistencies
- Generates detailed synchronization reports

### 4. Batch Scripts

- `update_mlb_games.bat`: Quick script to update game data from Aug 7 to today
- `mlb_api_integration_workflow.bat`: Comprehensive workflow that runs all steps in sequence

### 5. Testing Tool (`test_mlb_api.py`)

Verifies the MLB API integration for a single date:

- Tests API connectivity and data retrieval
- Shows example game data in both formats
- Useful for debugging or checking current data

## How to Use

### Running the Full Integration

To update all MLB game data with official MLB API data:

```
mlb_api_integration_workflow.bat [start_date] [end_date]
```

Default: Processes data from 2025-08-07 to today.

### Quick Update

To quickly update all game data:

```
update_mlb_games.bat
```

### Running Individual Components

1. MLB API Integration:
   ```
   python mlb_api_integration.py 2025-08-07 2025-08-13
   ```

2. Data Deduplication:
   ```
   python deduplicate_date_range.py 2025-08-07 2025-08-13
   ```

3. Data Synchronization:
   ```
   python synchronize_mlb_data.py 2025-08-07 2025-08-13
   ```

4. Testing:
   ```
   python test_mlb_api.py 2025-08-12
   ```

## System Architecture

- **Source of Truth**: MLB API (statsapi.mlb.com/api/v1)
- **Primary Data Files**:
  - `game_scores_cache.json`: Main game data storage
  - `normalized_game_data.json`: Normalized game data format
  - `historical_predictions_cache.json`: System predictions with game references
  - `historical_betting_lines_cache.json`: Betting lines with game references
  - `team_strength_cache.json`: Team strength data

## Logs and Reports

- `mlb_api_integration.log`: Integration process log
- `deduplicate.log`: Deduplication process log
- `data_synchronizer.log`: Data synchronization log
- `sync_report_*.txt`: Generated synchronization reports

## Schedule

It's recommended to run this integration:

1. Daily - early morning to update the previous day's results
2. 1-2 hours before games start - to get the latest pitcher information
3. After making any significant changes to the system

## Troubleshooting

If you encounter issues:

1. Check the log files for specific error messages
2. Run the test script (`test_mlb_api.py`) to verify API connectivity
3. Check for file permission issues if files cannot be written
4. Verify the MLB API is accessible and responding correctly
