#!/bin/bash
# ROS2 Humble Installation for Ubuntu 22.04
# Standard installation for Jammy Jellyfish

set -e
export DEBIAN_FRONTEND=noninteractive

echo "==========================================="
echo "ROS2 Humble Installation (Ubuntu 22.04)"
echo "==========================================="
echo ""

echo "Note: Installing ROS2 Humble on Ubuntu 24.04"
echo "Humble is the LTS version (supported until 2027)"
echo ""

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Detected: Ubuntu $VERSION_ID"
fi

echo ""
echo "[1/10] Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "[2/10] Installing prerequisites..."
sudo apt install -y \
    software-properties-common \
    curl \
    gnupg \
    lsb-release \
    wget \
    ca-certificates

echo ""
echo "[3/10] Adding ROS2 repository..."
# Clean up any existing ROS2 source files to avoid conflicts
rm -f /etc/apt/sources.list.d/ros2.list /etc/apt/sources.list.d/ros2.sources

# Download and de-armor the GPG key (more reliable for older apt versions, though good practice)
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | gpg --dearmor | tee /usr/share/keyrings/ros-archive-keyring.gpg > /dev/null

# Use jammy (22.04) repo for Humble on 24.04 (Humble isn't native to 24.04 noble)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo ""
echo "[4/10] Updating package lists..."
# Use -o Acquire::AllowInsecureRepositories=true if needed, but repo is secure
apt update

echo ""
echo "[5/10] Installing ROS2 Humble Desktop (includes RViz2)..."
sudo apt install -y ros-humble-desktop-full

echo ""
echo "[6/10] Installing RViz2 and visualization tools..."
sudo apt install -y \
    ros-humble-rviz2 \
    ros-humble-rviz-common \
    ros-humble-rviz-default-plugins \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro

echo ""
echo "[7/10] Installing development tools..."
sudo apt install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-argcomplete \
    python3-vcstool \
    build-essential

echo ""
echo "[8/10] Initializing rosdep..."
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi
rosdep update

echo ""
echo "[9/10] Installing Python ROS2 packages..."
# pip3 install rclpy # Standard ROS2 installation includes this


echo ""
echo "[10/10] Setting up environment..."
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# ROS2 Humble Environment" >> ~/.bashrc
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
    echo "export ROS_LOCALHOST_ONLY=1" >> ~/.bashrc
    echo "# For RViz with VcXsrv" >> ~/.bashrc
    echo "export DISPLAY=:0" >> ~/.bashrc
    echo "export LIBGL_ALWAYS_INDIRECT=0" >> ~/.bashrc
fi

# Source for current session
source /opt/ros/humble/setup.bash
export DISPLAY=:0

echo ""
echo "==========================================="
echo "ROS2 Humble Installation Complete!"
echo "==========================================="
echo ""
echo "Testing installation..."
ros2 --version

echo ""
echo "Testing RViz2..."
which rviz2

echo ""
echo "✓ ROS2 Humble and RViz2 are installed!"
echo ""
echo "Quick Start Guide:"
echo "==================="
echo ""
echo "1. Restart your terminal or run:"
echo "   source ~/.bashrc"
echo ""
echo "2. Test ROS2:"
echo "   ros2 topic list"
echo ""
echo "3. Launch RViz2 (make sure VcXsrv is running on Windows):"
echo "   export DISPLAY=:0"
echo "   rviz2"
echo ""
echo "4. Run gripper ROS2 node:"
echo "   cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper"
echo "   python3 ros2_gripper_node.py"
echo ""
echo "5. View gripper topics:"
echo "   ros2 topic list"
echo "   ros2 topic echo /gripper/state"
echo ""
echo "==========================================="
