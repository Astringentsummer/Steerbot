# Steerbot Project Status

## Working Files

### Core Functionality
- gripper_interface.py - Controls Piper gripper (MockPiper mode)
- vehicle_gripper_integration.py - Main integration script
- gripper_gazebo.urdf - Robot model for Gazebo simulation

### Demos
- run_gripper_steering_demo.py - 2D visualization demo
- run_gripper_terminal_demo.py - Terminal-based demo

### ROS2 Integration
- ros2_gripper_node.py - ROS2 control node
- ros2_gripper_node_windows.py - Windows mock node
- ros2_gazebo_gripper_control.py - Gazebo controller
- install_ros2.sh - ROS2 installation script

### Isaac Sim
- RUN_ISAAC_SIM.ps1 - Launch Isaac Sim simulation
- isaac_simple_demo.py - Gripper and steering wheel simulation
- launch_isaac_demo.sh - Bash launcher for WSL
- START_HERE_ISAAC_SIM.md - Setup instructions
- ISAAC_SIM_SETUP.md - Detailed documentation

## Running the Simulation

### Isaac Sim (Physics Simulation)
```powershell
.\RUN_ISAAC_SIM.ps1
```
Real physics simulation with PhysX and RTX rendering. Isaac Sim 5.1.0 is in your Downloads folder. Requires VcXsrv X server. See START_HERE_ISAAC_SIM.md for setup.

### 2D Demo (Quick Test)
```powershell
python run_gripper_steering_demo.py
```
Creates an animated GIF showing gripper motion. No physics, just visualization.

## Real Hardware Integration

When your Piper gripper and G29 wheel arrive:
```powershell
python vehicle_gripper_integration.py
```

## Notes

Using Isaac Sim for physics simulation. The 2D demo is available as a quick visualization test, but Isaac Sim provides real physics with PhysX and RTX rendering.
