# MLB New Day Automation - Windows Task Scheduler Setup
# Creates a scheduled task to run daily new day automation every morning

param(
    [string]$Time = "06:00",
    [switch]$Force
)

$taskName = "MLB-New-Day-Automation"
$batchScriptPath = "C:\Users\mostg\OneDrive\Coding\MLBCompare\run_new_day_automation.bat"
$workingDirectory = "C:\Users\mostg\OneDrive\Coding\MLBCompare"

Write-Host "Setting up MLB New Day Automation scheduled task..." -ForegroundColor Green
Write-Host "This will run complete daily automation at $Time every day" -ForegroundColor Yellow

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
    # Define the action - run the batch file
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batchScriptPath`"" -WorkingDirectory $workingDirectory
    
    # Define the trigger (daily at specified time)
    $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    
    # Define settings for reliable execution
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
    
    # Define principal (run with highest privileges)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    
    # Register the task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "MLB New Day Automation - Comprehensive daily prep with 5000 simulations"
    
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    Write-Host "Task Name: $taskName" -ForegroundColor Cyan
    Write-Host "Run Time: $Time daily" -ForegroundColor Cyan
    Write-Host "Script: $batchScriptPath" -ForegroundColor Cyan
    
    Write-Host "`nThe automation will run daily and:" -ForegroundColor Yellow
    Write-Host "  🏗️  Pull fresh games from MLB API" -ForegroundColor White
    Write-Host "  ⚾  Fetch projected starters" -ForegroundColor White
    Write-Host "  📊  Update pitcher stats and team strengths" -ForegroundColor White
    Write-Host "  💰  Update betting lines from OddsAPI" -ForegroundColor White
    Write-Host "  🎰  Run 5000 simulations for each game" -ForegroundColor White
    Write-Host "  🔒  Hard-code locked-in predictions" -ForegroundColor White
    Write-Host "  🎯  Generate betting recommendations" -ForegroundColor White
    Write-Host "  🖥️  Update frontend with today's games" -ForegroundColor White
    
    Write-Host "`n🎯 Your MLB prediction system will be automatically prepared each day!" -ForegroundColor Green
    
    # Show task details
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "`nTask Details:" -ForegroundColor Cyan
    Write-Host "  Status: $($task.State)" -ForegroundColor White
    Write-Host "  Next Run: $($task.NextRunTime)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to create scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nTo manage this task:" -ForegroundColor Yellow
Write-Host "  View:   Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host "  Delete: Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host "  Run:    Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White

Write-Host "`nLogs will be saved to: daily_new_day_automation.log" -ForegroundColor Cyan
