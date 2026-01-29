#!/bin/bash
# SIMPLE RVIZ TEST - Just show the robot

echo "========================================"
echo " SIMPLE RVIZ TEST"
echo "========================================"
echo ""

# Kill old processes
pkill -f 'rviz2' 2>/dev/null
pkill -f 'robot_state_publisher' 2>/dev/null
pkill -f 'joint_state_publisher' 2>/dev/null
sleep 1

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Source Piper workspace
PIPER_WS="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/piper_ros"
if [ -f "$PIPER_WS/install/setup.bash" ]; then
    source "$PIPER_WS/install/setup.bash"
fi

cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper

# URDF file
URDF_FILE="$PIPER_WS/src/piper_description/urdf/piper_description.urdf"

echo "Starting Robot State Publisher..."
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!

sleep 2

echo "Starting Joint State Publisher (no GUI)..."
ros2 run joint_state_publisher joint_state_publisher &
JSP_PID=$!

sleep 1

echo ""
echo "Opening RViz..."
echo "This should open a 3D window showing the Piper arm"
echo ""

# Try with explicit display
export DISPLAY=:0
ros2 run rviz2 rviz2 &
RVIZ_PID=$!

echo ""
echo "========================================"
echo " RVIZ SHOULD BE OPENING"
echo "========================================"
echo ""
echo "If you see RViz window:"
echo "  1. Click 'Add' button"
echo "  2. Select 'RobotModel'"
echo "  3. Set Fixed Frame to 'base_link'"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Cleanup
trap "kill $RSP_PID $JSP_PID $RVIZ_PID 2>/dev/null; echo 'Stopped.'; exit" INT TERM

wait
