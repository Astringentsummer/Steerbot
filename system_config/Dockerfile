FROM osrf/ros:humble-desktop-full

# Install MoveIt 2 and dependencies
RUN apt-get update && apt-get install -y \
    ros-humble-moveit \
    ros-humble-moveit-planners \
    ros-humble-moveit-plugins \
    ros-humble-moveit-ros-visualization \
    ros-humble-joint-state-publisher \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    ros-humble-tf2-tools \
    ros-humble-rqt \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-yaml \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Source ROS 2 automatically
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# Set environment variables
ENV STEERBOT_PROJECT=/workspace
ENV ISAAC_SIM_PATH=/isaac-sim

CMD ["/bin/bash"]
