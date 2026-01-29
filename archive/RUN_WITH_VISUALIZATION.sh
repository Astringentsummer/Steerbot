#!/bin/bash
# WORKING VERSION: Piper Controls G29 with Pre-configured RViz

echo "========================================"
echo " PIPER CONTROLS G29 - WITH RVIZ"
echo "========================================"
echo ""

# Kill any existing processes
pkill -f 'piper_controls_g29.py' 2>/dev/null
pkill -f 'g29_piper_hardware_bridge.py' 2>/dev/null
sleep 1

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Source Piper workspace
PIPER_WS="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/piper_ros"
if [ -f "$PIPER_WS/install/setup.bash" ]; then
    source "$PIPER_WS/install/setup.bash"
    echo "✓ Piper workspace sourced"
fi

cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper

# URDF file path
URDF_FILE="$PIPER_WS/src/piper_description/urdf/piper_description.urdf"

# RViz config (if exists in Steerbot-main)
RVIZ_CONFIG="/mnt/c/Users/rohit/Downloads/Steerbot-main/Steerbot-main/ros2_ws/src/piper_ros/src/piper_description/rviz/piper.rviz"

echo ""
echo "Launching components:"
echo "  1. Robot State Publisher"
echo "  2. Joint State Publisher GUI"
echo "  3. RViz (with config)"
echo "  4. Piper Controller"
echo ""

# 1. Robot State Publisher
echo "[1/4] Starting Robot State Publisher..."
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!
sleep 2

# 2. Joint State Publisher GUI
echo "[2/4] Starting Joint State Publisher GUI..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!
sleep 1

# 3. RViz with config file
echo "[3/4] Starting RViz..."
if [ -f "$RVIZ_CONFIG" ]; then
    echo "   Using config: $RVIZ_CONFIG"
    ros2 run rviz2 rviz2 -d "$RVIZ_CONFIG" &
else
    echo "   Using default config"
    ros2 run rviz2 rviz2 &
fi
RVIZ_PID=$!
sleep 3

# 4. Controller
echo "[4/4] Starting Piper-Controls-G29 controller..."
python3 piper_controls_g29.py &
CONTROLLER_PID=$!

echo ""
echo "========================================"
echo " ALL SYSTEMS RUNNING"
echo "========================================"
echo ""
echo "✓ RViz should now show the Piper arm!"
echo "✓ Watch it move in a sine wave pattern"
echo "✓ Use Joint State Publisher sliders for manual control"
echo ""
echo "Press Ctrl+C to stop everything"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $RSP_PID $JSP_PID $RVIZ_PID $CONTROLLER_PID 2>/dev/null
    pkill -f 'piper_controls_g29.py' 2>/dev/null
    echo "Stopped."
    exit 0
}

trap cleanup INT TERM

# Wait
wait
