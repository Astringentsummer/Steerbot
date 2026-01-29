#!/bin/bash
# REAL HARDWARE TEST - Production Ready

echo "========================================"
echo " REAL HARDWARE TEST"
echo " G29 Wheel → Piper Arm"
echo "========================================"
echo ""
echo "Prerequisites:"
echo "  1. G29 wheel connected to PC"
echo "  2. Piper arm powered on and connected"
echo "  3. ROS2 Jazzy installed"
echo ""

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Source Piper workspace (if exists)
PIPER_WS="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/piper_ros"
if [ -f "$PIPER_WS/install/setup.bash" ]; then
    source "$PIPER_WS/install/setup.bash"
    echo "✓ Piper workspace sourced"
fi

cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper

echo ""
echo "Starting hardware bridge..."
echo ""

# Run bridge
python3 real_hardware_bridge.py

echo ""
echo "Test complete."
