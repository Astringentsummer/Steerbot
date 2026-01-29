# PowerShell script to run ROS2 gripper node in WSL
# This properly sets up the environment and runs the node

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ROS2 Gripper Node in WSL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if WSL is available
wsl --list --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: WSL not found" -ForegroundColor Red
    Write-Host "Please install WSL2 first" -ForegroundColor Yellow
    exit 1
}

# Check if ROS2 is installed
Write-Host "[1/3] Checking ROS2 installation..." -ForegroundColor Yellow
$ros2Check = wsl -d Ubuntu-22.04 bash -c "which ros2" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ROS2 is NOT installed in WSL" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install ROS2, run:" -ForegroundColor Yellow
    Write-Host "  wsl -d Ubuntu-22.04" -ForegroundColor Cyan
    Write-Host "  cd /mnt/c/Users/rohit/Documents/Steerbot" -ForegroundColor Cyan
    Write-Host "  bash install_ros2.sh" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or see ROS2_ISAAC_SETUP.md for manual installation" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ ROS2 found at: $ros2Check" -ForegroundColor Green

# Copy files to WSL
Write-Host "[2/3] Copying files to WSL..." -ForegroundColor Yellow
$wslPath = "/home/$env:USERNAME/steerbot_ros2"
wsl -d Ubuntu-22.04 bash -c "mkdir -p $wslPath"
wsl -d Ubuntu-22.04 bash -c "cp /mnt/c/Users/rohit/Documents/Steerbot/ros2_gripper_node.py $wslPath/"
wsl -d Ubuntu-22.04 bash -c "cp /mnt/c/Users/rohit/Documents/Steerbot/gripper_interface.py $wslPath/"
Write-Host "  ✓ Files copied to WSL" -ForegroundColor Green

# Run the node
Write-Host "[3/3] Starting ROS2 node..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ROS2 Gripper Node Running in WSL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To send commands, open another terminal and run:" -ForegroundColor Yellow
Write-Host "  wsl -d Ubuntu-22.04" -ForegroundColor Cyan
Write-Host "  source /opt/ros/humble/setup.bash" -ForegroundColor Cyan
Write-Host "  ros2 topic pub /gripper/command std_msgs/Float32 'data: 50.0' --once" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the node in WSL
wsl -d Ubuntu-22.04 bash -c "cd $wslPath && source /opt/ros/humble/setup.bash && python3 ros2_gripper_node.py"
