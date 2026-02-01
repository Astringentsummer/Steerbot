#!/bin/bash

# Setup Isaac Sim Python environment for SAC training
echo '=========================================='
echo 'Setting up Isaac Sim Environment for SAC'
echo '=========================================='

# Check if Isaac Sim is installed
ISAAC_SIM_PATH="/root/.local/share/ov/pkg/isaac-sim-4.2.0"

if [ ! -d "$ISAAC_SIM_PATH" ]; then
    echo "ERROR: Isaac Sim not found at $ISAAC_SIM_PATH"
    echo "Searching for Isaac Sim installation..."
    ISAAC_SIM_PATH=$(find /root -name "isaac-sim*" -type d 2>/dev/null | head -n 1)
    if [ -z "$ISAAC_SIM_PATH" ]; then
        echo "ERROR: Could not find Isaac Sim installation"
        echo "Please install Isaac Sim first"
        exit 1
    fi
    echo "Found Isaac Sim at: $ISAAC_SIM_PATH"
fi

# Use Isaac Sim's Python (comes with PyTorch pre-installed)
ISAAC_PYTHON="$ISAAC_SIM_PATH/python.sh"

echo "Isaac Sim Python: $ISAAC_PYTHON"
echo ""

# Install additional dependencies using Isaac Sim's pip
echo "Installing additional dependencies..."
$ISAAC_PYTHON -m pip install scipy --quiet

echo ""
echo "[SUCCESS] Environment ready!"
echo ""
echo "To run SAC training:"
echo "  $ISAAC_PYTHON train_sac_isaac.py"
echo ""
echo "Or create an alias:"
echo "  alias isaac-python='$ISAAC_PYTHON'"
echo "  isaac-python train_sac_isaac.py"
