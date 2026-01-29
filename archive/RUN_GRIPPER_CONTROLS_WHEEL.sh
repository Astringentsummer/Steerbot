#!/bin/bash
# CORRECT DIRECTION: Piper Gripper Controls G29 Wheel

echo "========================================"
echo " PIPER GRIPPER CONTROLS G29 WHEEL"
echo "========================================"
echo ""
echo "The Piper arm will:"
echo "  1. Grasp the steering wheel"
echo "  2. Turn it back and forth"
echo "  3. Read wheel position as feedback"
echo ""

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Source Piper workspace (correct path)
PIPER_WS="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/piper_ros"
if [ -f "$PIPER_WS/install/setup.bash" ]; then
    source "$PIPER_WS/install/setup.bash"
    echo "✓ Piper workspace sourced"
else
    echo "⚠️  Piper workspace not built at $PIPER_WS"
    echo "   Building now..."
    cd "$PIPER_WS"
    colcon build
    source install/setup.bash
fi

# Go to working directory
cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper

# Launch Piper arm driver
echo "Starting Piper arm driver..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat $PIPER_WS/src/piper_description/urdf/piper_description.urdf)" &
PIPER_PID=$!

sleep 3

# Launch controller
echo "Starting Piper-Controls-G29 controller..."
python3 piper_controls_g29.py &
CONTROLLER_PID=$!

echo ""
echo "========================================"
echo " GRIPPER CONTROLLING WHEEL"
echo "========================================"
echo ""
echo "Watch the Piper arm turn the steering wheel!"
echo "Press Ctrl+C to stop"
echo ""

# Wait for user interrupt
trap "kill $PIPER_PID $CONTROLLER_PID 2>/dev/null; echo 'Stopped.'; exit" INT TERM

wait
