#!/bin/bash
# ROS2 Humble Installation Script for Ubuntu 22.04 (WSL2)
# Run this in WSL: bash install_ros2.sh

set -e

echo "=========================================="
echo "ROS2 Humble Installation for WSL2"
echo "=========================================="
echo ""

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$VERSION_ID" != "22.04" ]; then
        echo "WARNING: This script is for Ubuntu 22.04"
        echo "You have Ubuntu $VERSION_ID"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo "[1/8] Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo "[2/8] Installing prerequisites..."
sudo apt install -y \
    software-properties-common \
    curl \
    gnupg \
    lsb-release

echo "[3/8] Adding ROS2 repository..."
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo "[4/8] Updating package lists..."
sudo apt update

echo "[5/8] Installing ROS2 Humble Desktop..."
sudo apt install -y ros-humble-desktop

echo "[6/8] Installing development tools..."
sudo apt install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-argcomplete

echo "[7/8] Installing Python ROS2 packages..."
pip3 install rclpy

echo "[8/8] Setting up environment..."
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# ROS2 Humble" >> ~/.bashrc
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
fi

# Source for current session
source /opt/ros/humble/setup.bash

echo ""
echo "=========================================="
echo "ROS2 Humble Installation Complete!"
echo "=========================================="
echo ""
echo "Testing installation..."
ros2 --version

echo ""
echo "✓ ROS2 is ready to use!"
echo ""
echo "Next steps:"
echo "  1. Close and reopen your terminal (or run: source ~/.bashrc)"
echo "  2. Test with: ros2 topic list"
echo "  3. Run gripper node: python ros2_gripper_node.py"
echo ""
echo "See ROS2_ISAAC_SETUP.md for full instructions"
echo "=========================================="
