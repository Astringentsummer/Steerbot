#!/usr/bin/env python3
"""
PERFECT ISAAC SIM DEMO - Everything ON the table, clearly visible
Piper arm with gripper controlling G29 steering wheel
"""

import sys
import os
import numpy as np
import time

ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.append(os.path.join(ISAAC_SIM_PATH, "exts", "omni.isaac.kit", "omni", "isaac", "kit"))

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from pxr import UsdGeom, Gf

print("=" * 70)
print(" PERFECT DEMO - Piper Arm ON Table Controlling G29 Wheel")
print("=" * 70)

world = World()
world.scene.add_default_ground_plane()
stage = world.stage

# TABLE - Bottom at z=0, top at z=1.0
print("\n[1/4] Creating table...")
table = UsdGeom.Cube.Define(stage, "/World/Table")
table.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.5))  # Center at 0.5, top at 1.0
table.AddScaleOp().Set(Gf.Vec3d(3.0, 2.0, 1.0))  # 3m x 2m x 1m
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])
print("✓ Table: top surface at Z = 1.0")

# STEERING WHEEL - ON the table at z=1.8
print("\n[2/4] Creating G29 steering wheel ON table...")
wheel_z = 1.8  # ABOVE table

# Wheel rim
wheel_rim = UsdGeom.Cylinder.Define(stage, "/World/SteeringWheel/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, wheel_z))
wheel_rim.AddScaleOp().Set(Gf.Vec3d(0.35, 0.05, 0.35))
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))  # Vertical
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.1, 0.1)])

# Center hub
hub = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Hub")
hub.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, wheel_z))
hub.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
hub.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# 4 spokes
for i in range(4):
    angle = i * np.pi / 2
    spoke = UsdGeom.Cylinder.Define(stage, f"/World/SteeringWheel/Spoke{i}")
    x_off = 0.2 * np.cos(angle)
    y_off = 0.2 * np.sin(angle)
    spoke.AddTranslateOp().Set(Gf.Vec3d(0.5 + x_off, y_off, wheel_z))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.025, 0.2, 0.025))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

# Red target marker
target = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Target")
target.AddTranslateOp().Set(Gf.Vec3d(0.85, 0, wheel_z))  # On rim
target.AddScaleOp().Set(Gf.Vec3d(0.06, 0.06, 0.06))
target.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.0, 0.0)])
print(f"✓ G29 wheel ON table at Z = {wheel_z}")

# PIPER ARM - ON the table, left side
print("\n[3/4] Creating Piper arm ON table...")
arm_z = wheel_z  # Same height as wheel
base_x = -1.0  # Left side of table

# Base
base = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Base")
base.AddTranslateOp().Set(Gf.Vec3d(base_x, 0, 1.1))  # On table
base.AddScaleOp().Set(Gf.Vec3d(0.12, 0.1, 0.12))
base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Link 1 - BLUE
link1 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link1")
link1.AddTranslateOp().Set(Gf.Vec3d(base_x + 0.4, 0, arm_z))
link1.AddScaleOp().Set(Gf.Vec3d(0.05, 0.4, 0.05))
link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))  # Horizontal
link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 1.0)])

# Link 2 - GREEN
link2 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link2")
link2.AddTranslateOp().Set(Gf.Vec3d(base_x + 0.9, 0, arm_z))
link2.AddScaleOp().Set(Gf.Vec3d(0.05, 0.4, 0.05))
link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 1.0, 0.4)])

# Gripper - ORANGE
gripper = UsdGeom.Cube.Define(stage, "/World/PiperArm/Gripper")
gripper.AddTranslateOp().Set(Gf.Vec3d(base_x + 1.3, 0, arm_z))
gripper.AddScaleOp().Set(Gf.Vec3d(0.12, 0.12, 0.12))
gripper.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])
print(f"✓ Piper arm ON table at Z = {arm_z}")

# CAMERA - Wide view from above
print("\n[4/4] Setting camera...")
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
camera.AddTranslateOp().Set(Gf.Vec3d(0, -4.0, 3.5))  # From front, high up
camera.AddRotateXYZOp().Set(Gf.Vec3d(-40, 0, 0))  # Looking down at table
print("✓ Camera: front view looking down at table")

print("\n" + "=" * 70)
print(" PERFECT VIEW - You will see:")
print("=" * 70)
print("  🟫 Brown table (3m x 2m)")
print("  ⚫ Black G29 steering wheel (vertical, ON table)")
print("  🔴 Red target marker (on wheel rim)")
print("  🔵 Blue arm link (horizontal, ON table)")
print("  🟢 Green arm link (horizontal, ON table)")
print("  🟠 Orange gripper cube (ON table)")
print("")
print("  Everything is ABOVE the table, clearly visible!")
print("=" * 70)

class Controller:
    def __init__(self, stage):
        self.stage = stage
        self.time = 0
        self.link1 = stage.GetPrimAtPath("/World/PiperArm/Link1")
        self.link2 = stage.GetPrimAtPath("/World/PiperArm/Link2")
        self.gripper = stage.GetPrimAtPath("/World/PiperArm/Gripper")
        self.target = stage.GetPrimAtPath("/World/SteeringWheel/Target")
        self.base_x = -1.0
        self.wheel_z = 1.8
    
    def update(self, dt):
        self.time += dt
        
        # Wheel rotation
        wheel_angle = np.sin(self.time * 0.3) * 1.0  # ±60°
        
        # Target position on wheel
        target_x = 0.5 + 0.35 * np.cos(wheel_angle)
        target_y = 0.35 * np.sin(wheel_angle)
        
        # Arm angles
        q1 = wheel_angle * 0.7
        q2 = -wheel_angle * 0.4
        
        # Update Link 1
        link1_x = self.base_x + 0.4 * np.cos(q1)
        link1_y = 0.4 * np.sin(q1)
        
        xform1 = UsdGeom.Xformable(self.link1)
        xform1.ClearXformOpOrder()
        xform1.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, self.wheel_z))
        xform1.AddOrientOp().Set(Gf.Quatf(np.cos(q1/2), 0, 0, np.sin(q1/2)))
        xform1.AddScaleOp().Set(Gf.Vec3d(0.05, 0.4, 0.05))
        
        # Update Link 2
        link2_x = link1_x + 0.4 * np.cos(q1 + q2)
        link2_y = link1_y + 0.4 * np.sin(q1 + q2)
        
        xform2 = UsdGeom.Xformable(self.link2)
        xform2.ClearXformOpOrder()
        xform2.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, self.wheel_z))
        xform2.AddOrientOp().Set(Gf.Quatf(np.cos((q1+q2)/2), 0, 0, np.sin((q1+q2)/2)))
        xform2.AddScaleOp().Set(Gf.Vec3d(0.05, 0.4, 0.05))
        
        # Update Gripper
        gripper_x = link2_x + 0.4 * np.cos(q1 + q2)
        gripper_y = link2_y + 0.4 * np.sin(q1 + q2)
        
        xform_gripper = UsdGeom.Xformable(self.gripper)
        xform_gripper.ClearXformOpOrder()
        xform_gripper.AddTranslateOp().Set(Gf.Vec3d(gripper_x, gripper_y, self.wheel_z))
        xform_gripper.AddScaleOp().Set(Gf.Vec3d(0.12, 0.12, 0.12))
        
        # Update target
        xform_target = UsdGeom.Xformable(self.target)
        xform_target.ClearXformOpOrder()
        xform_target.AddTranslateOp().Set(Gf.Vec3d(target_x, target_y, self.wheel_z))
        xform_target.AddScaleOp().Set(Gf.Vec3d(0.06, 0.06, 0.06))

controller = Controller(stage)
world.reset()

print("\n🎬 Watch the ORANGE gripper turn the G29 wheel!\n")

frame = 0
try:
    while simulation_app.is_running():
        world.step(render=True)
        controller.update(1.0/60.0)
        frame += 1
        if frame % 180 == 0:
            print(f"✅ Frame {frame} - Gripper controlling wheel ON table")
except KeyboardInterrupt:
    print("\n\nStopped")

simulation_app.close()
print("\nDemo complete - everything was ON the table!")
