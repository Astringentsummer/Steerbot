#!/bin/bash
# Launch Isaac Sim Gripper Demo from WSL

echo ""
echo "================================================"
echo "  Isaac Sim Gripper + Steering Wheel Demo"
echo "================================================"
echo ""

# Paths
ISAAC_SIM="/mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64"
SCRIPT="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/isaac_simple_demo.py"

# Check Isaac Sim
if [ ! -f "$ISAAC_SIM/isaac-sim.sh" ]; then
    echo "ERROR: Isaac Sim not found at $ISAAC_SIM"
    exit 1
fi

echo "✓ Found Isaac Sim 5.0.0"
echo "✓ Found simulation script"
echo ""

# Set display
export DISPLAY=:0

# Change to Isaac Sim directory
cd "$ISAAC_SIM"

echo "Launching Isaac Sim..."
echo "(Press ESC in Isaac Sim window to exit)"
echo ""

# Run with Python from Isaac Sim
./python.sh "$SCRIPT"

echo ""
echo "================================================"
echo "  Simulation Ended"
echo "================================================"
echo ""
