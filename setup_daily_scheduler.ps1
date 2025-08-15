# MLB Daily Automation - Windows Task Scheduler Setup
# This script sets up a scheduled task to run the daily automation every morning

param(
    [string]$Time = "06:00",  # Default to 6:00 AM
    [string]$ScriptPath = "C:\Users\mostg\OneDrive\Coding\MLBCompare\daily_automation_safe.py"
)

Write-Host "Setting up MLB Daily Automation Scheduler..." -ForegroundColor Green
Write-Host "Script Path: $ScriptPath" -ForegroundColor Yellow
Write-Host "Schedule Time: $Time daily" -ForegroundColor Yellow

# Check if the script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script not found at $ScriptPath" -ForegroundColor Red
    exit 1
}

# Get the directory containing the script
$WorkingDirectory = Split-Path $ScriptPath -Parent

# Create the scheduled task
$TaskName = "MLB Daily Automation"
$Description = "Daily automation for MLB prediction system - fetches games, updates data, and prepares system for optimal performance"

# Define the action (what to run)
$PythonPath = (Get-Command python).Source
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

# Define the trigger (when to run)
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time

# Define settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create the task
try {
    # Check if task already exists and remove it
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # Register the new task
    $Task = Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description $Description
    
    Write-Host "SUCCESS: Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Description: $Description" -ForegroundColor White
    Write-Host "  Schedule: Daily at $Time" -ForegroundColor White
    Write-Host "  Script: $ScriptPath" -ForegroundColor White
    Write-Host "  Working Directory: $WorkingDirectory" -ForegroundColor White
    Write-Host ""
    Write-Host "The automation will now run every day at $Time" -ForegroundColor Green
    Write-Host "You can manage this task in Windows Task Scheduler" -ForegroundColor Yellow
    
    # Test the task
    Write-Host ""
    Write-Host "Would you like to test the task now? (y/n): " -ForegroundColor Cyan -NoNewline
    $response = Read-Host
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Running test..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Task started. Check the logs for results." -ForegroundColor Green
    }
    
} catch {
    Write-Host "ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "Your MLB prediction system will automatically update every morning at $Time" -ForegroundColor White
