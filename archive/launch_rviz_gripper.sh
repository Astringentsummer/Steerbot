#!/bin/bash
# Simple script to view the gripper URDF in RViz2
# Usage: ./launch_rviz_gripper.sh

source /opt/ros/jazzy/setup.bash

echo "Launching RViz2 for Gripper Visualization..."
echo "If RViz does not open, ensure your VcXsrv is running on Windows."

# FIX: Force software rendering to prevent WSL2 segmentation faults
export LIBGL_ALWAYS_SOFTWARE=1

# Option 1: Try display.launch.py from urdf_tutorial
if [ -f /opt/ros/jazzy/share/urdf_tutorial/launch/display.launch.py ]; then
    ros2 launch urdf_tutorial display.launch.py model:=urdf/gripper.urdf
else
    # Option 2: Manual Node Start (Backup)
    echo "urdf_tutorial not found, starting manual nodes..."
    
    # 1. Publish Robot State
    ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat urdf/gripper.urdf)" &
    PID_RSP=$!
    
    # 2. Publish Joint States (GUI)
    ros2 run joint_state_publisher_gui joint_state_publisher_gui &
    PID_JSP=$!

    # 3. Launch RViz
    ros2 run rviz2 rviz2 -d src/urdf_config.rviz &
    PID_RVIZ=$!
    
    wait $PID_RVIZ
    kill $PID_RSP $PID_JSP
fi
