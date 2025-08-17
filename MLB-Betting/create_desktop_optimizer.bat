@echo off
REM Create Desktop Shortcut for Always-Running Optimizer

echo.
echo =======================================
echo   Creating Desktop Shortcut
echo =======================================
echo.

set "shortcut_name=MLB Auto-Optimizer"
set "target_path=C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting\start_optimizer_no_admin.bat"
set "desktop_path=%USERPROFILE%\Desktop"

echo Creating desktop shortcut for always-running optimizer...

REM Create VBS script to create shortcut
echo Set WshShell = WScript.CreateObject("WScript.Shell") > "%temp%\create_shortcut.vbs"
echo Set oShellLink = WshShell.CreateShortcut("%desktop_path%\%shortcut_name%.lnk") >> "%temp%\create_shortcut.vbs"
echo oShellLink.TargetPath = "%target_path%" >> "%temp%\create_shortcut.vbs"
echo oShellLink.WorkingDirectory = "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting" >> "%temp%\create_shortcut.vbs"
echo oShellLink.Description = "Always-Running MLB Auto-Optimizer" >> "%temp%\create_shortcut.vbs"
echo oShellLink.Save >> "%temp%\create_shortcut.vbs"

REM Execute VBS script
cscript //nologo "%temp%\create_shortcut.vbs"

REM Clean up
del "%temp%\create_shortcut.vbs"

if exist "%desktop_path%\%shortcut_name%.lnk" (
    echo.
    echo ✅ SUCCESS: Desktop shortcut created!
    echo.
    echo Look for "%shortcut_name%" on your desktop.
    echo Double-click it to start always-running optimization.
    echo.
    echo The shortcut will:
    echo   - Start continuous auto-tuning
    echo   - Run optimization daily at 6:00 AM
    echo   - Perform quick checks every 4 hours
    echo   - Keep running until you close the window
    echo.
) else (
    echo.
    echo ❌ ERROR: Failed to create desktop shortcut
    echo.
)

echo.
echo Alternative: Run this directly for always-running optimization:
echo   start_optimizer_no_admin.bat
echo.
pause
