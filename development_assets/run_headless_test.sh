#!/bin/bash
# Script to run headlessly and show output
cd /mnt/c/Users/rohit/Downloads
echo "Starting Isaac Sim (Headless)..."
./python.sh /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/isaac_moveit_safe.py --headless > /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/sim_headless.log 2>&1 &
SIM_PID=$!

echo "Waiting for Simulation to load (30s)..."
sleep 30

echo "Running Mission 55 Humble Controller..."
cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper
source activate_humble.sh
python3 mission_55_humble.py

echo "Mission Complete. Stopping Simulation..."
kill $SIM_PID
