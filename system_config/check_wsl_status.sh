#!/bin/bash
# Professional Status Checker for Master's Project

echo "=========================================="
echo "WSL Environment Status Check"
echo "=========================================="

# 1. Check ROS 2
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    echo "[✓] ROS 2 Jazzy: INSTALLED"
    source /opt/ros/jazzy/setup.bash
    ros2 --version | head -n 1
else
    echo "[ ] ROS 2 Jazzy: NOT FOUND (Installation may be in progress)"
fi

# 2. Check MoveIt 2
if dpkg -l | grep -q "ros-jazzy-moveit"; then
    echo "[✓] MoveIt 2: INSTALLED"
else
    echo "[ ] MoveIt 2: NOT FOUND"
fi

# 3. Check Isaac Sim Connectivity
ISAAC_PATH="/mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64"
if [ -f "$ISAAC_PATH/python.sh" ]; then
    echo "[✓] Isaac Sim: DETECTED"
else
    echo "[✗] Isaac Sim: NOT FOUND at mount point"
fi

# 4. Check Background Installation
LOG_FILE="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/install_log.txt"
if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "Last 5 lines of Installation Log:"
    tail -n 5 "$LOG_FILE"
else
    echo ""
    echo "No installation log found. Run setup_wsl_environment.sh if needed."
fi

echo "=========================================="
