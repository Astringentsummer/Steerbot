# Isaac Sim Launcher
# Runs gripper and steering wheel simulation via WSL

[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseDeclaredVarsMoreThanAssignments', '')]
param()

Write-Host "`nIsaac Sim Gripper Simulation" -ForegroundColor Cyan
Write-Host "Using: Isaac Sim 5.1.0 Standalone (via WSL)`n"

Write-Host "Checking requirements..."

# Check WSL
[void](wsl -l -q 2>&1)
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: WSL not available" -ForegroundColor Red
    Write-Host "Install with: wsl --install"
    exit 1
}
Write-Host "[OK] WSL available" -ForegroundColor Green

# Check Ubuntu
[void](wsl -d Ubuntu echo "OK" 2>&1)
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Ubuntu not found" -ForegroundColor Red
    Write-Host "Install with: wsl --install Ubuntu"
    exit 1
}
Write-Host "[OK] Ubuntu ready" -ForegroundColor Green

# Check Isaac Sim
$isaacCheck = wsl -d Ubuntu bash -c "test -f /mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64/isaac-sim.sh && echo 'OK' || echo 'MISSING'"
if ($isaacCheck -ne "OK") {
    Write-Host "ERROR: Isaac Sim not found in Downloads" -ForegroundColor Red
    Write-Host "Expected location: C:\Users\rohit\Downloads\isaac-sim-standalone-5.1.0-linux-x86_64\"
    exit 1
}
Write-Host "[OK] Isaac Sim found" -ForegroundColor Green

Write-Host "`nStarting simulation..."
Write-Host "Features: Real-time physics (PhysX), RTX rendering, Gripper + Steering wheel"
Write-Host "Press ESC in Isaac Sim window to exit`n" -ForegroundColor Yellow

# Launch simulation
wsl -d Ubuntu bash /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/launch_isaac_demo.sh

Write-Host "`nSimulation complete." -ForegroundColor Cyan

