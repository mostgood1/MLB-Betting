# MLB Enhanced Daily Automation - PowerShell Version
# This script can be run as a Windows Scheduled Task for daily automation

param(
    [string]$LogPath = "daily_automation_powershell.log"
)

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogPath -Value $logMessage
}

function Run-MLBDailyAutomation {
    try {
        # Change to script directory
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        Set-Location $scriptDir
        
        Write-Log "🚀 Starting MLB Enhanced Daily Automation"
        Write-Log "📍 Working Directory: $scriptDir"
        
        # Run the Python automation script
        Write-Log "🐍 Executing Python automation script..."
        $result = & python daily_enhanced_automation.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ MLB Enhanced Daily Automation completed successfully"
            Write-Log "🎯 Your MLB prediction system is ready with enhanced accuracy"
            return $true
        } else {
            Write-Log "❌ MLB Enhanced Daily Automation failed with exit code: $LASTEXITCODE"
            Write-Log "💥 Output: $result"
            return $false
        }
        
    } catch {
        Write-Log "💥 Exception occurred: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
Write-Log "=" * 60
Write-Log "MLB ENHANCED DAILY AUTOMATION - PowerShell Version"
Write-Log "=" * 60

$success = Run-MLBDailyAutomation

if ($success) {
    Write-Log "🏆 Daily automation completed successfully!"
    exit 0
} else {
    Write-Log "⚠️ Daily automation encountered errors - check logs"
    exit 1
}
