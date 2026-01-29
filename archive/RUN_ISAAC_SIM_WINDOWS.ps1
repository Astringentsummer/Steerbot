$IsaacPath = "C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
$ScriptPath = "C:\Users\rohit\Downloads\Steerbot-Gripper\Steerbot-Gripper\isaac_enhanced_demo.py"

Write-Host "Starting Isaac Sim 4.5.0 on Windows..." -ForegroundColor Cyan

if (Test-Path "$IsaacPath\python.bat") {
    & "$IsaacPath\python.bat" "$ScriptPath"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Wrapper script failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Pause
    }
}
else {
    Write-Host "ERROR: python.bat not found at $IsaacPath" -ForegroundColor Red
}
