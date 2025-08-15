# MLB-Betting Task Scheduler Setup
# Creates a scheduled task to run daily data refresh every morning

param(
    [string]$Time = "07:00",
    [switch]$Force
)

$taskName = "MLB-Betting-Daily-Data-Refresh"
$scriptPath = "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting\daily_data_refresh.ps1"
$workingDirectory = "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"

Write-Host "Setting up MLB-Betting Daily Data Refresh scheduled task..." -ForegroundColor Green

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask -and !$Force) {
    Write-Host "Task '$taskName' already exists!" -ForegroundColor Yellow
    Write-Host "Use -Force to overwrite the existing task" -ForegroundColor Yellow
    exit 1
}

if ($existingTask -and $Force) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create the scheduled task
try {
    # Define the action
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`" -Verbose" -WorkingDirectory $workingDirectory
    
    # Define the trigger (daily at specified time)
    $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    
    # Define settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    # Define principal (run with highest privileges)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    
    # Register the task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automated daily refresh of MLB-Betting prediction data including pitcher stats, team strength, and betting lines"
    
    Write-Host "✅ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor White
    Write-Host "  Schedule: Daily at $Time" -ForegroundColor White
    Write-Host "  Script: $scriptPath" -ForegroundColor White
    Write-Host "  Working Directory: $workingDirectory" -ForegroundColor White
    Write-Host ""
    Write-Host "The task will run automatically every day at $Time to refresh:" -ForegroundColor Green
    Write-Host "  • Pitcher statistics" -ForegroundColor White
    Write-Host "  • Team strength metrics" -ForegroundColor White  
    Write-Host "  • Betting lines and odds" -ForegroundColor White
    Write-Host "  • Clear prediction cache for fresh predictions" -ForegroundColor White
    Write-Host ""
    Write-Host "You can:" -ForegroundColor Yellow
    Write-Host "  • View the task: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host "  • Run manually: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host "  • Remove task: Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    
}
catch {
    Write-Host "❌ Failed to create scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test the task by running it once (optional)
$runNow = Read-Host "`nWould you like to test the task by running it now? (y/N)"
if ($runNow -eq "y" -or $runNow -eq "Y") {
    Write-Host "Running the task now..." -ForegroundColor Yellow
    try {
        Start-ScheduledTask -TaskName $taskName
        Write-Host "✅ Task started successfully! Check the logs directory for output." -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to start task: $($_.Exception.Message)" -ForegroundColor Red
    }
}
