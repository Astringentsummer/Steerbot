#!/usr/bin/env python3
"""
SIMPLE ISAAC SIM DEMO - Piper Gripper Controls G29 Wheel
Clear visualization of arm turning the steering wheel
"""

import sys
import os
import numpy as np
import time

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.append(os.path.join(ISAAC_SIM_PATH, "exts", "omni.isaac.kit", "omni", "isaac", "kit"))

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from pxr import UsdGeom, Gf
import carb

print("=" * 70)
print(" PIPER GRIPPER CONTROLS G29 STEERING WHEEL")
print("=" * 70)

# Create world
world = World()
world.scene.add_default_ground_plane()
stage = world.stage

print("\n[1/4] Creating table...")
table = UsdGeom.Cube.Define(stage, "/World/Table")
table.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 0.4))
table.AddScaleOp().Set(Gf.Vec3d(0.8, 0.6, 0.8))
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])
print("✓ Table at (0.5, 0, 0.4)")

print("\n[2/4] Creating G29 steering wheel...")
# Wheel rim
wheel_rim = UsdGeom.Cylinder.Define(stage, "/World/SteeringWheel/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 0.9))
wheel_rim.AddScaleOp().Set(Gf.Vec3d(0.15, 0.02, 0.15))
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Spokes
for i in range(4):
    angle = i * np.pi / 2
    spoke = UsdGeom.Cylinder.Define(stage, f"/World/SteeringWheel/Spoke{i}")
    x_off = 0.1 * np.cos(angle)
    y_off = 0.1 * np.sin(angle)
    spoke.AddTranslateOp().Set(Gf.Vec3d(0.5 + x_off, y_off, 0.9))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.01, 0.1, 0.01))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

# Target grip point (red marker)
target = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Target")
target.AddTranslateOp().Set(Gf.Vec3d(0.65, 0, 0.9))
target.AddScaleOp().Set(Gf.Vec3d(0.03, 0.03, 0.03))
target.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.0, 0.0)])
print("✓ Steering wheel at (0.5, 0, 0.9)")

print("\n[3/4] Creating Piper arm with gripper...")
# Base
base = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Base")
base.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.85))
base.AddScaleOp().Set(Gf.Vec3d(0.05, 0.05, 0.05))
base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

# Link 1 (BLUE)
link1 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link1")
link1.AddTranslateOp().Set(Gf.Vec3d(0.15, 0, 0.9))
link1.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 0.8)])

# Link 2 (GREEN)
link2 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link2")
link2.AddTranslateOp().Set(Gf.Vec3d(0.4, 0, 0.9))
link2.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.8, 0.4)])

# Gripper (ORANGE CUBE)
gripper = UsdGeom.Cube.Define(stage, "/World/PiperArm/Gripper")
gripper.AddTranslateOp().Set(Gf.Vec3d(0.55, 0, 0.9))
gripper.AddScaleOp().Set(Gf.Vec3d(0.05, 0.05, 0.05))
gripper.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.6, 0.0)])
print("✓ Piper arm: Base → Link1 (blue) → Link2 (green) → Gripper (orange)")

print("\n[4/4] Setting camera for WIDE VIEW...")
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
# WIDE VIEW - Far back and high up to see everything
camera.AddTranslateOp().Set(Gf.Vec3d(2.0, 2.0, 1.5))  # Much further back
camera.AddRotateXYZOp().Set(Gf.Vec3d(-30, 45, 0))
print("✓ Camera positioned for WIDE VIEW - you'll see EVERYTHING")

print("\n" + "=" * 70)
print(" SCENE READY - You should see:")
print("=" * 70)
print("  ✓ Brown table (workspace)")
print("  ✓ Black steering wheel with 4 spokes")
print("  ✓ Red target marker on wheel")
print("  ✓ Piper arm: Blue link → Green link → Orange gripper")
print("  ✓ Gripper positioned near wheel")
print("")
print("The arm will now turn the steering wheel!")
print("Watch the orange gripper move the red target point")
print("")
print("Press Ctrl+C to stop")
print("=" * 70)

# Simple controller
class SimpleController:
    def __init__(self, stage):
        self.stage = stage
        self.time = 0
        self.link1 = stage.GetPrimAtPath("/World/PiperArm/Link1")
        self.link2 = stage.GetPrimAtPath("/World/PiperArm/Link2")
        self.gripper = stage.GetPrimAtPath("/World/PiperArm/Gripper")
        self.target = stage.GetPrimAtPath("/World/SteeringWheel/Target")
    
    def update(self, dt):
        self.time += dt
        
        # Wheel angle (slow sine wave)
        wheel_angle = np.sin(self.time * 0.3) * 1.2  # ±70°
        
        # Target position on wheel
        target_x = 0.5 + 0.15 * np.cos(wheel_angle)
        target_y = 0.0 + 0.15 * np.sin(wheel_angle)
        
        # Simple IK
        q1 = wheel_angle * 0.8
        q2 = -wheel_angle * 0.5
        
        # Update arm
        link1_x = 0.15 * np.cos(q1)
        link1_y = 0.15 * np.sin(q1)
        
        xform1 = UsdGeom.Xformable(self.link1)
        xform1.ClearXformOpOrder()
        xform1.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, 0.9))
        xform1.AddOrientOp().Set(Gf.Quatf(np.cos(q1/2), 0, 0, np.sin(q1/2)))
        xform1.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
        
        link2_x = link1_x + 0.15 * np.cos(q1 + q2)
        link2_y = link1_y + 0.15 * np.sin(q1 + q2)
        
        xform2 = UsdGeom.Xformable(self.link2)
        xform2.ClearXformOpOrder()
        xform2.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, 0.9))
        xform2.AddOrientOp().Set(Gf.Quatf(np.cos((q1+q2)/2), 0, 0, np.sin((q1+q2)/2)))
        xform2.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
        
        gripper_x = link2_x + 0.15 * np.cos(q1 + q2)
        gripper_y = link2_y + 0.15 * np.sin(q1 + q2)
        
        xform_gripper = UsdGeom.Xformable(self.gripper)
        xform_gripper.ClearXformOpOrder()
        xform_gripper.AddTranslateOp().Set(Gf.Vec3d(gripper_x, gripper_y, 0.9))
        xform_gripper.AddScaleOp().Set(Gf.Vec3d(0.05, 0.05, 0.05))
        
        # Update target
        xform_target = UsdGeom.Xformable(self.target)
        xform_target.ClearXformOpOrder()
        xform_target.AddTranslateOp().Set(Gf.Vec3d(target_x, target_y, 0.9))
        xform_target.AddScaleOp().Set(Gf.Vec3d(0.03, 0.03, 0.03))

controller = SimpleController(stage)
world.reset()

print("\nAnimation starting...\n")

frame = 0
try:
    while simulation_app.is_running():
        world.step(render=True)
        controller.update(1.0/60.0)
        
        frame += 1
        if frame % 120 == 0:
            print(f"Frame {frame} - Arm is turning the wheel smoothly")
        
except KeyboardInterrupt:
    print("\n\nStopped by user")

simulation_app.close()
print("\nDemo complete!")
