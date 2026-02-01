#!/bin/bash

# Configure X11 Display
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export DISPLAY=$WINDOWS_IP:0
export LIBGL_ALWAYS_INDIRECT=0
export MESA_GL_VERSION_OVERRIDE=4.5

echo "=========================================="
echo "Isaac Sim GUI Launcher"
echo "=========================================="
echo "Display: $DISPLAY"
echo ""
echo "Starting Isaac Sim..."
echo "This may take 2-3 minutes on first launch."
echo ""

# Launch Isaac Sim with GUI
/root/isaac-sim/python.sh /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/isaac_gui_mode.py
