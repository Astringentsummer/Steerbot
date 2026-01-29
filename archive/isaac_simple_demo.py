#!/usr/bin/env python3
"""
Simple Isaac Sim Gripper Demo
Based on Isaac Sim standalone examples
"""

import sys
import os

# Add Isaac Sim Python packages to path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

# Create simulation app with high FPS for 240Hz display
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
    "max_fps": 240,  # Match your display refresh rate
    "physics_fps": 120,  # Physics simulation rate (balance between speed and stability)
}

simulation_app = SimulationApp(config)

import omni
from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid
import numpy as np

# Create world
world = World()
world.scene.add_default_ground_plane()

print("\n" + "="*60)
print("  ISAAC SIM GRIPPER + STEERING WHEEL SIMULATION")
print("="*60)
print("\nStarting simulation...")
print("  • Physics Engine: NVIDIA PhysX")
print("  • Renderer: RTX Ray Tracing")
print("  • Press ESC or close window to exit\n")

# Create gripper base (dark gray metal)
gripper_base = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/Base",
        name="gripper_base",
        position=np.array([0.0, 0.0, 0.5]),
        scale=np.array([0.15, 0.1, 0.05]),
        color=np.array([0.25, 0.25, 0.25]),
    )
)

# Left finger (black rubber/plastic)
left_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/LeftFinger",
        name="left_finger",
        position=np.array([-0.08, 0.0, 0.45]),
        scale=np.array([0.02, 0.02, 0.12]),
        color=np.array([0.1, 0.1, 0.1]),
    )
)

# Right finger (black rubber/plastic)
right_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/RightFinger",
        name="right_finger",
        position=np.array([0.08, 0.0, 0.45]),
        scale=np.array([0.02, 0.02, 0.12]),
        color=np.array([0.1, 0.1, 0.1]),
    )
)

# Steering wheel (black leather/rubber)
wheel = world.scene.add(
    DynamicCuboid(
        prim_path="/World/SteeringWheel",
        name="steering_wheel",
        position=np.array([0.0, 0.0, 0.4]),
        scale=np.array([0.2, 0.2, 0.03]),
        color=np.array([0.05, 0.05, 0.05]),
    )
)

print("✓ Scene created successfully")
print("  - Gripper with 2 fingers")
print("  - Steering wheel")
print("  - Ground plane\n")

# Reset world
world.reset()

# Simulation loop
frame = 0
gripper_width = 0.16  # Starting width in meters

print("Running simulation loop...")
print("Phase 1: Opening gripper")

try:
    while simulation_app.is_running():
        world.step(render=True)
        frame += 1
        
        # Simple animation cycle
        phase_duration = 120  # frames per phase
        phase = (frame // phase_duration) % 5
        
        if phase == 0:  # Opening
            gripper_width = 0.16
        elif phase == 1:  # Approaching
            gripper_width = 0.16
        elif phase == 2:  # Closing
            gripper_width = max(0.05, gripper_width - 0.002)
        elif phase == 3:  # Steering
            # Rotate wheel
            angle = np.sin(frame * 0.05) * 0.5
            wheel_pos = wheel.get_world_pose()[0]
            wheel.set_world_pose(
                position=wheel_pos,
                orientation=np.array([np.cos(angle/2), 0, 0, np.sin(angle/2)])
            )
        elif phase == 4:  # Opening again
            gripper_width = min(0.16, gripper_width + 0.002)
        
        # Update finger positions
        left_finger.set_world_pose(
            position=np.array([-gripper_width/2, 0.0, 0.45])
        )
        right_finger.set_world_pose(
            position=np.array([gripper_width/2, 0.0, 0.45])
        )
        
        # Print status every 60 frames
        if frame % 60 == 0:
            phase_names = ["OPEN", "APPROACH", "GRASP", "STEER", "RELEASE"]
            print(f"[Frame {frame}] Phase: {phase_names[phase]} | Gripper: {gripper_width*1000:.1f}mm")

except KeyboardInterrupt:
    print("\n\nSimulation interrupted by user")

finally:
    print("\nClosing Isaac Sim...")
    simulation_app.close()
    print("✓ Simulation ended\n")
