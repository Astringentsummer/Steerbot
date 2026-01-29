#!/usr/bin/env python3
"""
Isaac Sim Windows Demo - Enhanced Gripper Simulation
Native Windows version - no WSL needed
"""

import sys
import os

# Add Isaac Sim Python packages to path (Windows version)
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "site"))

from isaacsim import SimulationApp

# Create simulation app optimized for RTX 5080
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
    "renderer": "RayTracedLighting",
    "anti_aliasing": 3,
}

simulation_app = SimulationApp(config)

import omni
from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, DynamicSphere
import numpy as np

# Create world
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

print("\n" + "="*70)
print("  ISAAC SIM WINDOWS - GRIPPER + STEERING WHEEL")
print("="*70)
print("\nFeatures:")
print("  • Native Windows execution (no WSL)")
print("  • PhysX Physics Engine")
print("  • RTX Ray Tracing")
print("  • Force sensors and visualization")
print("\nControls:")
print("  • ESC to exit")
print("  • Mouse to rotate camera")
print("="*70 + "\n")

# Gripper base
gripper_base = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/Base",
        name="gripper_base",
        position=np.array([0.0, 0.0, 0.6]),
        scale=np.array([0.15, 0.1, 0.05]),
        color=np.array([0.3, 0.3, 0.35]),
        mass=0.5,
    )
)

# Left finger
left_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/LeftFinger",
        name="left_finger",
        position=np.array([-0.08, 0.0, 0.5]),
        scale=np.array([0.02, 0.03, 0.15]),
        color=np.array([0.1, 0.1, 0.1]),
        mass=0.05,
    )
)

# Right finger
right_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/RightFinger",
        name="right_finger",
        position=np.array([0.08, 0.0, 0.5]),
        scale=np.array([0.02, 0.03, 0.15]),
        color=np.array([0.1, 0.1, 0.1]),
        mass=0.05,
    )
)

# Steering wheel
wheel = world.scene.add(
    DynamicCuboid(
        prim_path="/World/SteeringWheel",
        name="steering_wheel",
        position=np.array([0.0, 0.0, 0.5]),
        scale=np.array([0.35, 0.35, 0.04]),
        color=np.array([0.05, 0.05, 0.05]),
        mass=2.0,
    )
)

# Force indicators
left_indicator = world.scene.add(
    DynamicSphere(
        prim_path="/World/Indicators/Left",
        name="left_force",
        position=np.array([-0.3, 0.0, 0.5]),
        radius=0.03,
        color=np.array([0.0, 1.0, 0.0]),
        mass=0.01,
    )
)

right_indicator = world.scene.add(
    DynamicSphere(
        prim_path="/World/Indicators/Right",
        name="right_force",
        position=np.array([0.3, 0.0, 0.5]),
        radius=0.03,
        color=np.array([0.0, 1.0, 0.0]),
        mass=0.01,
    )
)

print("Scene created successfully\n")
world.reset()

frame = 0
gripper_width = 0.20
steering_angle = 0.0
PHASE_DURATION = 180
phases = ["OPEN", "APPROACH", "GRASP", "STEER", "RELEASE"]

print("Starting simulation loop...\n")

try:
    while simulation_app.is_running():
        world.step(render=True)
        frame += 1
        
        phase_index = (frame // PHASE_DURATION) % len(phases)
        phase = phases[phase_index]
        
        if phase == "OPEN":
            gripper_width = 0.20
            target_force = 0.0
        elif phase == "APPROACH":
            gripper_width = 0.20
            target_force = 0.0
        elif phase == "GRASP":
            target_width = 0.06
            gripper_width = max(target_width, gripper_width - 0.001)
            grip_progress = (0.20 - gripper_width) / (0.20 - target_width)
            target_force = min(1.0, grip_progress)
        elif phase == "STEER":
            gripper_width = 0.06
            target_force = 0.8
            steering_angle = np.sin((frame % PHASE_DURATION) * 0.05) * 0.785
            wheel_pos = wheel.get_world_pose()[0]
            wheel.set_world_pose(
                position=wheel_pos,
                orientation=np.array([np.cos(steering_angle/2), 0, 0, np.sin(steering_angle/2)])
            )
        elif phase == "RELEASE":
            gripper_width = min(0.20, gripper_width + 0.002)
            target_force = max(0.0, target_force - 0.02)
        
        base_pos = gripper_base.get_world_pose()[0]
        base_ori = gripper_base.get_world_pose()[1]
        
        left_finger.set_world_pose(
            position=np.array([base_pos[0] - gripper_width/2, base_pos[1], base_pos[2] - 0.05]),
            orientation=base_ori
        )
        
        right_finger.set_world_pose(
            position=np.array([base_pos[0] + gripper_width/2, base_pos[1], base_pos[2] - 0.05]),
            orientation=base_ori
        )
        
        left_indicator.set_world_pose(
            position=np.array([-0.3, 0.0, 0.3 + target_force * 0.3])
        )
        right_indicator.set_world_pose(
            position=np.array([0.3, 0.0, 0.3 + target_force * 0.3])
        )
        
        if frame % 60 == 0:
            steering_deg = np.degrees(steering_angle)
            print(f"[Frame {frame:4d}] Phase: {phase:8s} | Gripper: {gripper_width*1000:5.1f}mm | Force: {target_force*100:3.0f}% | Steering: {steering_deg:+5.1f}°")

except KeyboardInterrupt:
    print("\nSimulation interrupted by user")

finally:
    print("\nClosing Isaac Sim...")
    simulation_app.close()
    print("Simulation ended successfully\n")
