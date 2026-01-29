#!/bin/bash
# REAL HARDWARE TEST - G29 + Piper Arm
# Run this in WSL2 to connect physical hardware

echo "========================================"
echo " G29 + PIPER REAL HARDWARE TEST"
echo "========================================"
echo ""
echo "Prerequisites:"
echo "  1. Physical G29 wheel connected"
echo "  2. Piper arm powered on"
echo "  3. ROS2 running"
echo ""

# Source ROS2
source /opt/ros/jazzy/setup.bash
source ~/piper_ros/install/setup.bash

# Launch Piper arm driver
echo "Starting Piper arm driver..."
ros2 launch piper_description piper.launch.py &
PIPER_PID=$!

sleep 3

# Launch G29 bridge
echo "Starting G29-Piper bridge..."
python3 g29_piper_hardware_bridge.py &
BRIDGE_PID=$!

echo ""
echo "========================================"
echo " HARDWARE TEST RUNNING"
echo "========================================"
echo ""
echo "Turn the G29 wheel to control the Piper arm"
echo "Press Ctrl+C to stop"
echo ""

# Wait for user interrupt
wait

# Cleanup
kill $PIPER_PID $BRIDGE_PID 2>/dev/null
echo "Stopped."
