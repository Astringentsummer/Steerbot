#!/bin/bash
# ==============================================================================
# WSL Environment Setup for MoveIt 2 + Isaac Sim Integration
# ROS 2 HUMBLE Edition (for Ubuntu 22.04)
# ==============================================================================

set -e  # Exit on error

echo "=========================================="
echo "WSL Environment Setup for Mission 55"
echo "ROS 2 Humble (Ubuntu 22.04)"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Check Ubuntu version
echo ""
echo "Step 1: Checking Ubuntu version..."
UBUNTU_VERSION=$(lsb_release -rs)
print_status "Ubuntu version: $UBUNTU_VERSION"

if [ "$UBUNTU_VERSION" != "22.04" ]; then
    print_error "This script requires Ubuntu 22.04 for ROS 2 Humble"
    print_error "Current version: $UBUNTU_VERSION"
    exit 1
fi

# 2. Check/Install ROS 2 Humble
echo ""
echo "Step 2: Checking ROS 2 Humble installation..."

if [ -f "/opt/ros/humble/setup.bash" ]; then
    print_status "ROS 2 Humble is already installed"
    source /opt/ros/humble/setup.bash
    ros2 --version
else
    print_warning "ROS 2 Humble not found. Installing..."
    
    # Add ROS 2 repository
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository universe -y
    
    # Add ROS 2 GPG key
    sudo apt update && sudo apt install -y curl
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    
    # Add repository to sources list
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
    
    # Install ROS 2 Humble
    sudo apt update
    sudo apt install -y ros-humble-desktop
    
    print_status "ROS 2 Humble installed successfully"
fi

# 3. Check/Install MoveIt 2
echo ""
echo "Step 3: Checking MoveIt 2 installation..."

if dpkg -l | grep -q "ros-humble-moveit"; then
    print_status "MoveIt 2 is already installed"
else
    print_warning "MoveIt 2 not found. Installing..."
    sudo apt update
    sudo apt install -y \
        ros-humble-moveit \
        ros-humble-moveit-planners \
        ros-humble-moveit-plugins \
        ros-humble-moveit-ros-visualization
    print_status "MoveIt 2 installed successfully"
fi

# 4. Install additional ROS 2 dependencies
echo ""
echo "Step 4: Installing additional ROS 2 dependencies..."
sudo apt install -y \
    ros-humble-joint-state-publisher \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    ros-humble-tf2-tools \
    ros-humble-rqt \
    python3-colcon-common-extensions \
    python3-rosdep

print_status "ROS 2 dependencies installed"

# 5. Initialize rosdep
echo ""
echo "Step 5: Initializing rosdep..."
if [ ! -f "/etc/ros/rosdep/sources.list.d/20-default.list" ]; then
    sudo rosdep init
    print_status "rosdep initialized"
else
    print_status "rosdep already initialized"
fi

rosdep update
print_status "rosdep updated"

# 6. Verify Isaac Sim Python
echo ""
echo "Step 6: Verifying Isaac Sim installation..."
ISAAC_PATH="/mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64"

if [ -f "$ISAAC_PATH/python.sh" ]; then
    print_status "Isaac Sim found at: $ISAAC_PATH"
    ISAAC_PYTHON_VERSION=$($ISAAC_PATH/python.sh --version 2>&1)
    print_status "Isaac Sim Python: $ISAAC_PYTHON_VERSION"
else
    print_error "Isaac Sim not found at: $ISAAC_PATH"
    exit 1
fi

# 7. Verify USD assets
echo ""
echo "Step 7: Verifying USD assets..."
PROJECT_PATH="/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper"

PIPER_USD="$PROJECT_PATH/dev/piper_isaac_sim/usd/piper_description.usd"
G29_USD="$PROJECT_PATH/isaac/scenes/g29.usd"

if [ -f "$PIPER_USD" ]; then
    print_status "Piper USD found: $PIPER_USD"
else
    print_error "Piper USD not found: $PIPER_USD"
    exit 1
fi

if [ -f "$G29_USD" ]; then
    print_status "G29 USD found: $G29_USD"
else
    print_error "G29 USD not found: $G29_USD"
    exit 1
fi

# 8. Set up environment variables
echo ""
echo "Step 8: Setting up environment variables..."

ENV_FILE="$HOME/.bashrc"

# Add ROS 2 sourcing if not already present
if ! grep -q "source /opt/ros/humble/setup.bash" "$ENV_FILE"; then
    echo "" >> "$ENV_FILE"
    echo "# ROS 2 Humble" >> "$ENV_FILE"
    echo "source /opt/ros/humble/setup.bash" >> "$ENV_FILE"
    print_status "Added ROS 2 Humble to .bashrc"
else
    print_status "ROS 2 Humble already in .bashrc"
fi

# Add project path
if ! grep -q "STEERBOT_PROJECT" "$ENV_FILE"; then
    echo "" >> "$ENV_FILE"
    echo "# Steerbot Project" >> "$ENV_FILE"
    echo "export STEERBOT_PROJECT=$PROJECT_PATH" >> "$ENV_FILE"
    echo "export ISAAC_SIM_PATH=$ISAAC_PATH" >> "$ENV_FILE"
    print_status "Added project environment variables to .bashrc"
else
    print_status "Project environment variables already in .bashrc"
fi

# 9. Install Python dependencies
echo ""
echo "Step 9: Installing Python dependencies..."
sudo apt install -y python3-pip python3-yaml python3-numpy

print_status "Python dependencies installed"

# 10. Summary
echo ""
echo "=========================================="
echo "Environment Setup Complete!"
echo "=========================================="
echo ""
print_status "ROS 2 Humble: Installed"
print_status "MoveIt 2: Installed"
print_status "Isaac Sim: Verified"
print_status "USD Assets: Verified"
echo ""
echo "Next steps:"
echo "  1. Source ROS 2: source /opt/ros/humble/setup.bash"
echo "  2. Navigate to project: cd $PROJECT_PATH"
echo "  3. Run Isaac Sim scene: $ISAAC_PATH/python.sh isaac_moveit_scene.py"
echo ""
echo "Or simply restart your WSL terminal to load the new environment."
