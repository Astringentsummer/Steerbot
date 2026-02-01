#!/bin/bash
# Script to activate ROS 2 Humble environment (Robostack)

# Set the root prefix for micromamba
export MAMBA_ROOT_PREFIX=~/micromamba
export MAMBA_EXE='/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/bin/micromamba'

# Initialize shell hook
eval "$($MAMBA_EXE shell hook -s bash --root-prefix $MAMBA_ROOT_PREFIX)"

# Activate the humble environment
alias micromamba="$MAMBA_EXE"
micromamba activate humble

# Check if ROS 2 is available
if command -v ros2 &> /dev/null; then
    echo "ROS 2 Humble Activated Successfully"
else
    echo "Error: ROS 2 Humble could not be activated. Environment might still be building."
fi
