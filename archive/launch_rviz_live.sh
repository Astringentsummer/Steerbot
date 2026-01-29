#!/bin/bash
# Script to view LIVE Isaac Sim data in RViz2
# Usage: ./launch_rviz_live.sh

source /opt/ros/jazzy/setup.bash

echo "Launching RViz2 in LIVE MODE..."
echo "Waiting for Joint States from Isaac Sim..."

# FIX: Force software rendering
export LIBGL_ALWAYS_SOFTWARE=1

# 1. Publish Robot State (Converts /joint_states from Isaac -> TF tree)
# Using the Full Piper Arm URDF
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat urdf/piper_arm.urdf)" &
PID_RSP=$!

# 2. Launch RViz (Visualizer)
ros2 run rviz2 rviz2 -d src/urdf_config.rviz &
PID_RVIZ=$!

wait $PID_RVIZ
kill $PID_RSP
