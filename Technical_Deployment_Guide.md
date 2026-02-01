# Technical Deployment Guide: MoveIt 2 and Isaac Sim Integration
## Cross-Platform Environment Configuration

This document outlines the procedures for deploying the Steerbot-Gripper platform on a native Linux workstation. 

> [!IMPORTANT]
> The code developed in WSL uses standard **ROS 2 Humble** and **MoveIt 2** APIs. It is 100% compatible with native Ubuntu 22.04 LTS.

---

## 1. Environment Compatibility
The company workstation should have:
- **OS:** Ubuntu 22.04 LTS (Native recommended for GPU performance).
- **ROS 2:** Humble Hawksbill (Desktop-Full).
- **GPU:** NVIDIA RTX series (required for Isaac Sim).
- **Drivers:** NVIDIA Driver 525+ with Vulkan support.

## 2. Setting Up the Workspace
On the native Linux machine, follow these steps to integrate the code:

1. **Clone the Project:**
   ```bash
   git clone <your-repository-url>
   cd Steerbot-Gripper/piper_ros
   ```
2. **Install Dependencies:**
   ```bash
   rosdep update
   rosdep install --from-paths src --ignore-src -r -y
   ```
3. **Build the MoveIt 2 Packages:**
   ```bash
   colcon build --symlink-install --packages-select piper_description piper_with_gripper_moveit
   source install/setup.bash
   ```

## 3. Configuration & Simulation
Digital Twin synchronization is managed via a dedicated Python bridge.
- **Backend:** Update the path configurations in [physics_backend.py](file:///c:/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/physics_backend.py) to match the host Linux directory structure.

## 4. Operational Execution
The system supports both containerized and native deployments.

### deployment: Containerized (Recommended for DevOps)
1. **Build the Stack:**
   ```bash
   docker-compose build
   ```
2. **Launch the Control Plane:**
   ```bash
   docker-compose up -d steerbot-control
   ```
3. **Initialize Physics Backend (Host-side):**
   ```bash
   ./python.sh physics_backend.py
   ```

### deployment: Native (Legacy)
The system deployment follows a structured three-phase launch sequence:

### Phase 1: Physical Simulation Backend
Initialize the Isaac Sim environment and the ROS 2 hardware bridge:
```bash
./python.sh physics_backend.py
```

### Phase 2: Signal Synthesis
Enable the signal generation bridge or physical HID interface:
```bash
# Option A: System Signal Synthesis
python3 signal_synthesis.py

# Option B: Physical HID Bridge (Logitech G29)
ros2 run g29_isaac_bridge g29_steering_node
```

### Phase 3: Kinematic Processing
Execute the core kinematic mapping service to synchronize the robotic manipulator:
```bash
python3 kinematic_processor.py
```

---

## 5. Technical Support & Verification
| Component | Function | Status |
| :--- | :--- | :--- |
| `physics_backend.py` | PhysX & ROS Bridge | Verified |
| `kinematic_processor.py` | Kinematic Mapping | Verified |
| `maneuver_control.py` | Trajectory Execution | Production |

---
**Deployment Readiness:** COMPLETED
**System Integrity:** HIGH (Standard ROS 2 API Compliance)
