#!/bin/bash
# ROS2 Jazzy Installation Script for Ubuntu 24.04 (WSL2)
# Run this in WSL: bash install_ros2_jazzy.sh

set -e

echo "==========================================="
echo "ROS2 Jazzy Installation for WSL2"
echo "==========================================="
echo ""

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Detected: Ubuntu $VERSION_ID"
    if [ "$VERSION_ID" != "24.04" ]; then
        echo "WARNING: This script is optimized for Ubuntu 24.04"
        echo "You have Ubuntu $VERSION_ID"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo ""
echo "[1/9] Updating and repairing system packages..."
sudo apt update
sudo apt --fix-broken install -y
sudo apt upgrade -y

echo ""
echo "[2/9] Installing prerequisites..."
sudo apt install -y \
    software-properties-common \
    curl \
    gnupg \
    lsb-release \
    wget

echo ""
echo "[3/9] Adding ROS2 repository..."
# Force clear any old ROS repositories to prevent "list of sources could not be read" errors
rm -f /etc/apt/sources.list.d/ros2.list /etc/apt/sources.list.d/ros2.sources /etc/apt/sources.list.d/ros-archive-keyring.gpg

# Standard ritual for GPG key
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add the official Jazzy repository for Ubuntu 24.04 (Noble)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo ""
echo "[4/9] Updating package lists..."
sudo apt update

echo ""
echo "[5/9] Installing ROS2 Jazzy Desktop (includes RViz2 and rclpy)..."
sudo apt install -y ros-jazzy-desktop

echo ""
echo "[6/9] Installing visualization and state tools..."
sudo apt install -y \
    ros-jazzy-rviz2 \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-xacro

echo ""
echo "[7/9] Installing development tools..."
sudo apt install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    ros-dev-tools

echo ""
echo "[8/9] Initializing rosdep..."
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi
rosdep update

echo ""
echo "[9/9] Setting up environment..."
# ROS2 Jazzy Environment configuration (No pip install needed for rclpy)

# Source for current session
source /opt/ros/jazzy/setup.bash

echo ""
echo "==========================================="
echo "ROS2 Jazzy Installation Complete!"
echo "==========================================="
echo ""
echo "Testing installation..."
ros2 --version

echo ""
echo "Testing RViz2..."
which rviz2

echo ""
echo "✓ ROS2 and RViz2 are ready to use!"
echo ""
echo "Next steps:"
echo "  1. Close and reopen your terminal (or run: source ~/.bashrc)"
echo "  2. Test ROS2: ros2 topic list"
echo "  3. Test RViz2: rviz2 (requires X server running)"
echo "  4. Run gripper node: python3 ros2_gripper_node.py"
echo ""
echo "To launch RViz2 with X server:"
echo "  export DISPLAY=:0"
echo "  rviz2"
echo ""
echo "==========================================="
