#!/bin/bash
# ==============================================================================
# ISAAC SIM DIGITAL TWIN LAUNCHER (WSL2 OPTIMIZED)
# ==============================================================================

# 1. Setup GPU Bridge (Windows Drivers -> WSL)
export LD_LIBRARY_PATH="/usr/lib/wsl/lib:$LD_LIBRARY_PATH"
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json

# 2. Project Paths
PROJECT_DIR="/root/projects/Steerbot-Gripper/Steerbot-Gripper"
ISAAC_EXE="/root/isaac-sim/python.sh"

echo "[LAUNCH] - Starting NVIDIA Isaac Sim Headless Mode..."
echo "[LAUNCH] - Project Root: $PROJECT_DIR"

# 3. Execution
cd "$PROJECT_DIR"
"$ISAAC_EXE" "$PROJECT_DIR/isaac_sim_demo.py"
