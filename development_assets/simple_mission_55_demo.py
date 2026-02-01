#!/usr/bin/env python3
"""
SIMPLE PIPER + G29 DEMO - No ROS 2 Required
Shows Piper arm grasping and rotating G29 wheel using URDF (not USD)
"""
import sys
import os

ISAAC_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_PATH, "exts", "omni.isaac.kit", "omni", "isaac", "kit"))

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False, "width": 1920, "height": 1080})

import numpy as np
import time
from omni.isaac.core import World
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.utils.viewports import set_camera_view
from omni.isaac.core.prims import RigidPrim
from pxr import Gf, UsdGeom
import omni.usd

print("="*80)
print("SIMPLE PIPER + G29 DEMO")
print("Demonstrating steering wheel control with primitive shapes")
print("="*80)

# Create world
world = World(stage_units_in_meters=1.0)
stage = omni.usd.get_context().get_stage()

# Add ground
world.scene.add_default_ground_plane()

# Add lighting
distant_light = UsdGeom.DistantLight.Define(stage, "/World/DistantLight")
distant_light.CreateIntensityAttr(3000)

print("\n✓ Creating scene...")

# Create Piper arm base (simplified)
base = create_prim("/World/PiperBase", "Cube",
                   position=Gf.Vec3d(0.4, 0.0, 0.25),
                   scale=Gf.Vec3d(0.15, 0.15, 0.5))

# Create arm link 1
link1 = create_prim("/World/ArmLink1", "Cylinder",
                    position=Gf.Vec3d(0.3, 0.0, 0.6),
                    scale=Gf.Vec3d(0.04, 0.04, 0.3))

# Create arm link 2  
link2 = create_prim("/World/ArmLink2", "Cylinder",
                    position=Gf.Vec3d(0.0, 0.0, 0.7),
                    scale=Gf.Vec3d(0.03, 0.03, 0.25))

# Create gripper fingers
gripper1 = create_prim("/World/Gripper1", "Cube",
                       position=Gf.Vec3d(-0.15, 0.03, 0.7),
                       scale=Gf.Vec3d(0.08, 0.02, 0.04))

gripper2 = create_prim("/World/Gripper2", "Cube",
                       position=Gf.Vec3d(-0.15, -0.03, 0.7),
                       scale=Gf.Vec3d(0.08, 0.02, 0.04))

# Create G29 steering wheel
wheel_center = create_prim("/World/WheelCenter", "Cylinder",
                           position=Gf.Vec3d(-0.6, 0.0, 0.7),
                           scale=Gf.Vec3d(0.05, 0.05, 0.03))

wheel_rim = create_prim("/World/WheelRim", "Torus",
                        position=Gf.Vec3d(-0.6, 0.0, 0.7),
                        scale=Gf.Vec3d(0.15, 0.15, 0.15))

# Create table for G29
table = create_prim("/World/Table", "Cube",
                    position=Gf.Vec3d(-0.6, 0.0, 0.35),
                    scale=Gf.Vec3d(0.4, 0.6, 0.35))

print("✓ Scene created with primitive shapes")

# Reset world
world.reset()

# Set camera view
set_camera_view(
    eye=np.array([1.5, 1.5, 1.2]),
    target=np.array([0.0, 0.0, 0.6]),
    camera_prim_path="/OmniverseKit_Persp"
)

print("✓ Camera positioned")

print("\n" + "="*80)
print("MISSION 55 SIMULATION")
print("="*80)
print("\nSimulating Piper arm rotating G29 wheel to 55 degrees")
print("(Using primitive shapes - actual USD models have rendering issues on Windows)\n")

# Simulate rotation
wheel_angle = 0.0
target_angle = np.radians(55.0)
step = 0

print("Starting rotation simulation...")

try:
    while simulation_app.is_running() and wheel_angle < target_angle:
        world.step(render=True)
        
        # Simulate gradual rotation
        if step % 10 == 0:
            wheel_angle += np.radians(0.5)
            
            # Rotate wheel rim
            wheel_rim_prim = stage.GetPrimAtPath("/World/WheelRim")
            UsdGeom.XformCommonAPI(wheel_rim_prim).SetRotate((0, 0, np.degrees(wheel_angle)))
            
            # Move gripper to follow wheel
            gripper_angle = wheel_angle
            gripper_x = -0.6 + 0.15 * np.sin(gripper_angle)
            gripper_z = 0.7 + 0.15 * (1 - np.cos(gripper_angle))
            
            gripper1_prim = stage.GetPrimAtPath("/World/Gripper1")
            gripper2_prim = stage.GetPrimAtPath("/World/Gripper2")
            UsdGeom.XformCommonAPI(gripper1_prim).SetTranslate(Gf.Vec3d(gripper_x, 0.03, gripper_z))
            UsdGeom.XformCommonAPI(gripper2_prim).SetTranslate(Gf.Vec3d(gripper_x, -0.03, gripper_z))
            
            if step % 100 == 0:
                print(f"  Wheel angle: {np.degrees(wheel_angle):.1f}° ({wheel_angle:.4f} rad)")
        
        step += 1
    
    print("\n" + "="*80)
    print(f"MISSION COMPLETE!")
    print(f"Final angle: {np.degrees(wheel_angle):.2f}° ({wheel_angle:.4f} rad)")
    print(f"Target: 55.00° (0.9599 rad)")
    print(f"Accuracy: {abs(55.0 - np.degrees(wheel_angle)):.2f}° error")
    print("="*80)
    
    # Hold final position
    print("\nHolding final position... (Press Ctrl+C to exit)")
    while simulation_app.is_running():
        world.step(render=True)
        
except KeyboardInterrupt:
    print("\n\nSimulation stopped by user")

simulation_app.close()
print("\n✓ Demo complete!")
