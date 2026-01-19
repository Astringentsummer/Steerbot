# Development Guide - Steerbot Project

## Repository Organization

**Question: Do I need a branch named "Gripper" or should I create a separate repository?**

**Answer:** You need a **branch**, NOT a separate repository. All gripper-related development should be done within this Steerbot repository using feature branches.

## Why Use Branches Instead of a New Repository?

The Steerbot project is designed as a unified workspace that includes:
- Logitech G29 steering wheel integration
- Piper robot arm (with and without gripper configurations)
- ROS2 communication infrastructure
- Isaac Sim integration

Creating a separate repository for gripper work would:
- Break the integration between components
- Duplicate shared infrastructure (ROS2 workspace, build configs, etc.)
- Make it harder to test the complete digital twin system

## Branch Naming Convention

For feature development related to gripper functionality, use descriptive branch names:

### Good Branch Names:
- `feature/gripper-integration`
- `feature/gripper-control`
- `feature/gripper-isaac-sim`
- `feature/gripper-moveit-config`
- `dev/gripper-testing`
- `fix/gripper-collision`

### Branch Workflow:
1. Create a feature branch from main/master
2. Develop your gripper-related changes
3. Test with the complete system
4. Create a pull request to merge back to main

## Gripper Configuration in This Repository

The repository already contains gripper support in multiple locations:

### 1. Robot Description (`piper_description`)
- URDFs with gripper: Located in `piper_description/urdf/`
- Gripper meshes: `piper_description/meshes/gripper_base.STL`
- Launch files: `piper_description/launch/piper_with_gripper/`

### 2. MoveIt Configuration (`piper_moveit`)
- `piper_with_gripper_moveit/` - Complete MoveIt2 configuration for gripper-equipped robot
- `piper_no_gripper_moveit/` - Configuration without gripper

Launch commands:
```bash
# With gripper
ros2 launch piper_with_gripper_moveit controller_bringup_gripper.launch.py
ros2 launch piper_with_gripper_moveit moveit_dt_gripper.launch.py

# Without gripper
ros2 launch piper_no_gripper_moveit controller_bringup.launch.py
ros2 launch piper_no_gripper_moveit moveit_dt.launch.py
```

### 3. Simulation (`piper_sim`)
- Gazebo with gripper: `piper_gazebo/launch/piper_with_gripper/`
- Gazebo without gripper: `piper_gazebo/launch/piper_no_gripper/`

## Development Workflow for Gripper Features

### Step 1: Create a Feature Branch
```bash
# From the repository root
git checkout -b feature/gripper-your-feature-name
```

### Step 2: Make Your Changes
Work on gripper-related files in the appropriate packages:
- Robot description: `ros2_ws/src/piper_ros/src/piper_description/`
- MoveIt config: `ros2_ws/src/piper_ros/src/piper_moveit/piper_with_gripper_moveit/`
- Simulation: `ros2_ws/src/piper_ros/src/piper_sim/`
- Isaac Sim scenes: `isaac/scenes/`

### Step 3: Build and Test
```bash
cd ~/Steerbot/ros2_ws
colcon build --symlink-install
source install/setup.bash

# Test with gripper configuration
ros2 launch piper_with_gripper_moveit moveit_dt_gripper.launch.py
```

### Step 4: Commit and Push
```bash
git add .
git commit -m "Add/update gripper feature: description"
git push origin feature/gripper-your-feature-name
```

### Step 5: Create Pull Request
Create a PR to merge your gripper feature branch back into the main branch.

## Integration with Isaac Sim

For gripper integration with Isaac Sim:
1. Update/create USD scenes in `isaac/scenes/`
2. Ensure gripper meshes are properly converted to USD format
3. Configure gripper articulation and physics
4. Test gripper grasping in simulation

Example scene structure:
```
isaac/
└── scenes/
    ├── piper_with_gripper.usd
    ├── g29_and_piper_gripper.usd
    └── gripper_grasp_test.usd
```

## Summary

✅ **Use branches** for gripper development
❌ **Don't create** a separate repository

All gripper work belongs in this unified Steerbot repository, organized by feature branches for clean development workflow and easy integration testing.
