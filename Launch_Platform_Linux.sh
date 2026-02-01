#!/bin/bash

# Integrated System Deployment Script (Native Linux)
# Usage: ./launch_system.sh

echo "============================================================"
echo "  STEERBOT: KINEMATIC INTEGRATION PLATFORM (LINUX)"
echo "============================================================"

# 1. Source Environment
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
    echo "[OK] ROS 2 Humble Middleware Sourced"
else
    echo "[!] Warning: ROS 2 Humble not found"
fi

# 2. Start Simulation Backend (Background)
echo "[1/2] Initializing Physics Backend..."
./python.sh physics_backend.py &
SIM_PID=$!

# 3. Wait for Initialization
echo "     Synchronizing Physics and ROS 2 Middleware..."
sleep 45

# 4. Start Kinematic Processor
echo "[2/2] Launching Kinematic Processing Engine..."
python3 kinematic_processor.py &
CTRL_PID=$!

echo ""
echo "============================================================"
echo "  SYSTEM DEPLOYMENT SUCCESSFUL"
echo "  Press Ctrl+C to terminate all components"
echo "============================================================"

# Handle termination
trap "kill $SIM_PID $CTRL_PID; exit" INT
wait
