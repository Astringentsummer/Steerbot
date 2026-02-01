# Steerbot-Gripper: High-Fidelity Kinematic Steering Integration

A deterministic robotic control system for the Piper Manipulator, featuring real-time hardware-in-the-loop synchronization with the Logitech G29 steering interface.

## Overview

This project implements a verified industrial control pipeline, featuring:

- **Legacy-Free Deterministic Control:** Pure mathematical kinematic mapping for 100% predictable safety.
- **Integrated High-Fidelity Digital Twin:** Real-time synchronization between physical G29 steering and simulated Piper Arm.
- **MoveIt 2 Kinematic Control:** Utilization of MoveIt 2 and OMPL for collision-free robotic steering.
- **Hardware-in-the-Loop Simulation:** Direct bridge for human-in-the-loop driving simulation.

## Features

### Operational System
- **Real-time Reactive Controller:** Direct G29-to-Manipulator mapping (30Hz Loop).
- **Safety First:** Hard-coded geometric constraints and velocity limits.
- **Physics Fidelity:** Integrated Isaac Sim environment with automated ROS 2 bridging.

### Digital Twin & Interactive Integration
- **Kinematic Processor:** Industrial-grade signal processing and joint state mapping.
- **Physics Backend:** Integrated Isaac Sim environment with automated ROS 2 bridging.
- **Deployment Orchestration:** Cross-platform launch scripts (Windows/Linux) for unified system execution.
- **Telemetry Synthesis:** Integrated signal generation for hardware-free system verification.

## Quick Start

### Prerequisites

```
- NVIDIA Isaac Sim 4.5.0+
- Python 3.10+
- Logitech G29 steering wheel (optional)
- Piper robotic arm (optional)
```

### Hardware Integration

**1. Initialize Simulation Backend:**
```bash
./python.sh physics_backend.py
```

**2. Launch Interactive Controller:**
```bash
python3 kinematic_processor.py
```

**3. (Optional) Run Input Simulator:**
```bash
python3 signal_synthesis.py
```

## Project Structure

```
Steerbot-Gripper/
 simulation_assets/      # USD scenes and physics assets
 prototype_assets/       # High-fidelity CAD components
 bin/                    # Compiled Docker artifacts
 config/                 # System Parameters (YAML)
 doc/                    # Architecture & Deployment Guides
 physics_backend.py      # Core PhysX simulation
 kinematic_processor.py  # Deterministic Control Logic
 inference_interface.py  # Standardized API for control signals
 Dockerfile              # DevOps Production Build
 README.md
```

## Documentation

- [Technical Deployment Guide](Technical_Deployment_Guide.md)
- [Architecture Reference](Architecture_Reference.md)

## Requirements

### Software
```
numpy>=1.24.0
scipy>=1.10.0
pyyaml>=6.0
inputs>=0.5  # For G29 hardware
```

### Hardware
- NVIDIA GPU with CUDA support (RTX 3060+ recommended)
- Logitech G29 steering wheel (for hardware integration)

## Contact

For questions or collaboration:
- GitHub Issues: [Astringentsummer/Steerbot](https://github.com/Astringentsummer/Steerbot/issues)
- Email: rohit15parmar15@gmail.com

---

**Control System:** Deterministic Kinematic Mapping (No 'Black Box' AI).
**Safety:** Hard real-time limits and geometric constraints.

