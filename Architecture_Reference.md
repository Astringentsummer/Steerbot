# Steerbot: Integrated Digital Twin for Teleoperated Robotic Steering
## Project Overview
This project implements a high-fidelity Digital Twin of a 6-DOF robotic manipulator (Piper Arm) integrated with a Logitech G29 steering system. The architecture leverages **ROS 2 Humble**, **MoveIt 2**, and **NVIDIA Isaac Sim** to achieve real-time synchronization between physical control inputs and simulated physics.

### Core Objectives
- **Bilateral Control:** Real-time mapping of high-resolution steering inputs (±450°) to robotic joint space.
- **Physics Fidelity:** Integration of URDF/USD assets with calibrated inertia, friction, and joint limits.
- **Path Planning:** Utilization of MoveIt 2 OMPL planners for collision-free trajectory generation.

---

## System Architecture
The platform is designed with a container-first microservices approach, fulfilling the **MLOps Level 2** maturity standard (Automated Training & Deployment).

### 1. The Containerized Control Plane (Docker)
- **Service:** `steerbot-control`
- **Config:** `config/system_parameters.yaml`
- **Function:** Process isolation for kinematic calculations and path planning.
- **Deployment:** Managed via `docker-compose` with host networking.

### 2. The Artifact Registry (Model Management)
- **Path:** `model_registry/`
- **Strategy:** Decoupled model storage versioned by semantic release tags.
- **Serving:** Dynamic loading of policies based on `inference_config` parameters.

### 3. The Perceptual Layer (Input Bridge)
- **Source:** `kinematic_processor.py`
- **Function:** Captures HID events from the Logitech G29 interface.
- **Output:** Publishes telemetry to ROS 2 topics (`/wheel/steering_angle`).

### 2. The Cognitive Layer (MoveIt 2 + ROS 2)
- **Infrastructure:** `piper_with_gripper_moveit` package.
- **Function:** Handles kinematic transformations and joint state management.
- **Process:** Translates desired steering positions into 6-joint trajectory commands.

### 3. The Physical Layer (Isaac Sim)
- **Source:** `physics_backend.py`
- **Simulation:** Real-time PhysX execution with ROS 2 bridge extensions.
- **Interaction:** Dynamic contact modeling between the manipulator and the steering assembly.

---

## Deployment & Verification
To execute the system in a production or research Steiner environment:

### Prerequisite Environment
- **Middleware:** ROS 2 Humble (Desktop Full)
- **Simulation Platform:** NVIDIA Isaac Sim 5.1.0+
- **Hardware Interface:** `usbipd` (if using WSL) or native HID drivers (Linux).

### Execution Sequence
1. **Simulation Backend:** Initialize the core physics engine.
   ```bash
   ./python.sh physics_backend.py
   ```
2. **Kinematic Controller:** Launch the ROS 2 kinematic mapping stack.
   ```bash
   python3 kinematic_processor.py
   ```
3. **Hardware Integration:** (Optional) Deploy the bridge for physical G29 connection.

---

## Technical Specifications
| Parameter | Value |
| :--- | :--- |
| Steering Range | ±450.0° (900° Total) |
| System Latency | < 15ms (End-to-End) |
| Feedback Loop | 100Hz (Real-time) |
| Planning Library | OMPL (RRT-Connect) |

**System Integration Status:** Verified for Deployment
**Role Assignment:** Master's Thesis Portfolio Integration
