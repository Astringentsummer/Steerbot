# MoveIt 2 + Isaac Sim Steering Control System

## System Architecture

This project implements a **collision-aware steering actuation system** using:

- **MoveIt 2** - Motion planning (the brain)
- **Isaac Sim** - Physics simulation (the body)
- **ROS 2 Action Graph** - Synchronization (nervous system)
- **Piper Robotic Arm** - Physical execution
- **Logitech G29 Steering Wheel** - Target actuator

## Mission: Rotate G29 Wheel 55 Degrees

The system achieves repeatable, collision-aware steering control by having the Piper arm grasp and rotate the G29 steering wheel to a precise 55-degree angle.

## Core Components

### 1. Environment Modeling

**G29 Steering Wheel:**
- Modeled with dedicated revolute joint
- Clearly defined rotation axis
- Physics-based force feedback

**Piper Robotic Arm:**
- Official URDF aligned with MoveIt 2
- Consistent joint definitions
- Separate visual and collision geometry

**Result:** Continuous collision checking during robot-wheel interaction

### 2. Coordinate Frames & TF Consistency

All components maintain consistent coordinate frames:
- Piper robotic arm frame
- G29 steering wheel frame
- Supporting table frames
- World frame

**Result:** Motion planned in RViz matches physical execution in Isaac Sim

### 3. Synchronization via Action Graph

**Problem:** ROS 2 and simulator on different clocks causes timing drift

**Solution:** Action Graph triggered on every simulation tick
- Reads simulation time
- Publishes as ROS 2 `/clock`
- ROS 2 operates in simulation time

**Result:** Planning and execution are fully synchronized

### 4. Motion Execution

**Flow:**
1. MoveIt 2 computes joint trajectories
2. Publishes as joint states
3. Action Graph subscribes to joint states
4. Forwards commands to articulation controller
5. Robot moves according to plan

**Result:** Tight coupling between planning and execution

### 5. Steering Wheel Observation

**Feedback Loop:**
- Wheel rotation joint state published to ROS 2
- Control algorithm knows current steering angle
- Enables verification of target angle (e.g., 55°)
- Supports position holding

**Result:** Observable and feedback-based control

## Key Files

### Isaac Sim Integration
- `setup_ros2_action_graph.py` - ROS 2 synchronization setup
- `g29_isaac_bridge.py` - G29 wheel interface

### Hardware Deployment
- `deploy_to_piper.py` - Real Piper arm deployment
- `export_model.py` - Model export utilities

### USD Assets
- `dev/piper_isaac_sim/usd/piper_description.usd` - Piper arm model
- `isaac/scenes/g29.usd` - G29 steering wheel model
- `isaac/scenes/g29_force.usd` - G29 with force feedback

## Running the System

### Prerequisites
- ROS 2 (Humble or later)
- MoveIt 2
- Isaac Sim 4.5.0
- Piper arm (physical or simulated)

### Launch Sequence

1. **Start Isaac Sim with ROS 2 Bridge**
   ```bash
   # In Isaac Sim, load the scene with Piper and G29
   # Enable ROS 2 bridge extension
   ```

2. **Setup Action Graph**
   ```bash
   python setup_ros2_action_graph.py
   ```

3. **Launch MoveIt 2**
   ```bash
   ros2 launch piper_moveit_config demo.launch.py
   ```

4. **Execute Steering Motion**
   ```bash
   # Plan and execute 55-degree rotation in RViz
   ```

## Achievements

- **Collision-Aware Planning** - No hard-coded motions
- **Physically Plausible** - All movements validated by physics
- **Repeatable Execution** - Deterministic synchronization
- **Observable Control** - Real-time feedback from wheel angle
- **Target Accuracy** - Achieves 54.26° (within 1° of 55° target)

## Project Type

**University-Company Partnership Project** (Master's Level)

This is an industry-level integration project demonstrating:
- Professional ROS 2 architecture
- Physics-based validation
- Synchronized multi-system control
- Repeatable steering outcomes

## Next Steps

1. Fine-tune motion planning for optimal trajectories
2. Implement force feedback control
3. Add safety constraints for real hardware
4. Extend to continuous steering control
5. Deploy to physical Piper arm

---

**Note:** This system focuses on MoveIt 2 motion planning and Isaac Sim physics simulation. All reinforcement learning and SAC training components have been removed to maintain focus on the core architecture.
