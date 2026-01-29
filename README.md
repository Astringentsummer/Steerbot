# Steerbot-Gripper: Piper Arm with G29 Steering Wheel

## Project Overview
Integration of a Piper 6-DOF robotic manipulator with a Logitech G29 steering wheel using NVIDIA Isaac Sim. This project aims to control the steering wheel using the robot arm's gripper.

## Key Components

### Simulation
- **`isaac_sim_demo.py`**: Main simulation script.
- **`run_isaac_demo.bat`**: Helper script to run the simulation.
- **`isaac_rl/tasks/G29PiperTask.py`**: RL environment task definition.

### Hardware
- **`safe_hardware_bridge.py`**: Bridge for physical robot control.
- **`test_g29.py`**: Test script for G29 wheel input (UDP).
- **`test_piper.py`**: Test script for Piper arm connection (ROS2).

## Hardware Specifications
- **Robot**: Piper 6-DOF Manipulator with parallel-jaw gripper.
- **Input**: Logitech G29 Steering Wheel.

## Usage
1. **Run Simulation**:
   ```powershell
   .\run_isaac_demo.bat
   ```
2. **Test Hardware**:
   - G29: `python test_g29.py`
   - Piper: `python test_piper.py`
