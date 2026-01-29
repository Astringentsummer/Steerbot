$IsaacPath = "C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
$ScriptPath = "C:\Users\rohit\Downloads\Steerbot-Gripper\Steerbot-Gripper\isaac_piper_demo.py"

Write-Host "Starting Piper Arm + Gripper Simulation..."
if (Test-Path "$IsaacPath\python.bat") {
    & "$IsaacPath\python.bat" "$ScriptPath" 2>&1
}
else {
    Write-Error "Isaac Sim path not found: $IsaacPath"
}
