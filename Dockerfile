# ==============================================================================
# STAGE 1: BUILDER (Artifact Compilation)
# ==============================================================================
FROM osrf/ros:humble-desktop-full AS builder

SHELL ["/bin/bash", "-c"]

WORKDIR /build
COPY ros2_workspace/ src/

# Build optimization: Cache dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    && rosdep update \
    && rosdep install --from-paths src --ignore-src -r -y 

# Compile with optimization flags
RUN source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# ==============================================================================
# STAGE 2: RUNTIME (Operational Environment)
# ==============================================================================
FROM osrf/ros:humble-desktop-full

LABEL maintainer="DevOps Engineering Team <deployment@steerbot.io>"
LABEL org.opencontainers.image.source="https://github.com/steerbot/platform"

# 1. Security & User Configuration
# ------------------------------------------------------------------------------
ARG USERNAME=steerbot
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create a non-root user with hardware access (video/input/dialout groups)
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && usermod -aG video,input,dialout,plugdev $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# 2. Runtime Dependencies
# ------------------------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-evdev \
    ros-humble-moveit \
    ros-humble-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# 3. Payload Delivery
# ------------------------------------------------------------------------------
WORKDIR /app/bin

# Copy compiled artifacts from Builder Stage (Multi-stage pattern)
COPY --from=builder /build/install /app/ros_workspace/install
COPY --from=builder /build/build /app/ros_workspace/build

# Copy Application Source
COPY kinematic_processor.py .
COPY maneuver_control.py .
COPY signal_synthesis.py .
COPY environment_setup.sh .

# Fix permissions for non-root user
RUN chown -R $USERNAME:$USERNAME /app

# 4. Container Health & Entrypoint
# ------------------------------------------------------------------------------
USER $USERNAME

# Healthcheck to ensure ROS 2 daemon is responsive
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD ros2 node list || exit 1

ENTRYPOINT ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && source /app/ros_workspace/install/setup.bash && exec \"$@\"", "--"]
CMD ["python3", "kinematic_processor.py"]
