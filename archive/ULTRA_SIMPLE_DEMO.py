#!/usr/bin/env python3
"""
ULTRA SIMPLE - Visible Piper Arm + Gripper + Wheel
Everything clearly visible, no clipping!
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
print(" ULTRA SIMPLE - EVERYTHING VISIBLE")
print("=" * 70)

world = World()
world.scene.add_default_ground_plane()
stage = world.stage

# TABLE - Large and flat
print("\n[1/5] Table...")
table = UsdGeom.Cube.Define(stage, "/World/Table")
table.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.5))
table.AddScaleOp().Set(Gf.Vec3d(4.0, 3.0, 1.0))
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])
print("✓ Large brown table")

# STEERING WHEEL - Right side
print("\n[2/5] G29 Steering Wheel...")
wheel_x = 1.0  # Right side
wheel_y = 0
wheel_z = 2.0  # High up
wheel_radius = 0.4

# Rim
rim = UsdGeom.Cylinder.Define(stage, "/World/Wheel/Rim")
rim.AddTranslateOp().Set(Gf.Vec3d(wheel_x, wheel_y, wheel_z))
rim.AddScaleOp().Set(Gf.Vec3d(wheel_radius, 0.05, wheel_radius))
rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))
rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.1, 0.1)])

# Hub
hub = UsdGeom.Sphere.Define(stage, "/World/Wheel/Hub")
hub.AddTranslateOp().Set(Gf.Vec3d(wheel_x, wheel_y, wheel_z))
hub.AddScaleOp().Set(Gf.Vec3d(0.1, 0.1, 0.1))
hub.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# 4 spokes
for i in range(4):
    angle = i * np.pi / 2
    spoke = UsdGeom.Cylinder.Define(stage, f"/World/Wheel/Spoke{i}")
    x_off = (wheel_radius - 0.1) * np.cos(angle)
    y_off = (wheel_radius - 0.1) * np.sin(angle)
    spoke.AddTranslateOp().Set(Gf.Vec3d(wheel_x + x_off, wheel_y + y_off, wheel_z))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.03, wheel_radius - 0.1, 0.03))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

print(f"✓ Black wheel at ({wheel_x}, {wheel_y}, {wheel_z})")

# PIPER ARM - Left side, CLEARLY VISIBLE
print("\n[3/5] Piper Arm Structure...")
arm_x = -1.0  # Left side
arm_y = 0
arm_z = 1.1  # Base on table

# BASE - Dark gray cylinder
base = UsdGeom.Cylinder.Define(stage, "/World/Piper/Base")
base.AddTranslateOp().Set(Gf.Vec3d(arm_x, arm_y, arm_z))
base.AddScaleOp().Set(Gf.Vec3d(0.15, 0.15, 0.15))
base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])
print(f"  ✓ BASE (gray) at ({arm_x}, {arm_y}, {arm_z})")

# SHOULDER JOINT - Red sphere
shoulder = UsdGeom.Sphere.Define(stage, "/World/Piper/Shoulder")
shoulder.AddTranslateOp().Set(Gf.Vec3d(arm_x, arm_y, arm_z + 0.2))
shoulder.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
shoulder.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.2, 0.2)])
print(f"  ✓ SHOULDER (red sphere)")

# LINK 1 - Blue cylinder
link1 = UsdGeom.Cylinder.Define(stage, "/World/Piper/Link1")
link1.AddTranslateOp().Set(Gf.Vec3d(arm_x + 0.3, arm_y, wheel_z))
link1.AddScaleOp().Set(Gf.Vec3d(0.06, 0.3, 0.06))
link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 1.0)])
print(f"  ✓ LINK 1 (blue)")

# ELBOW JOINT - Yellow sphere
elbow = UsdGeom.Sphere.Define(stage, "/World/Piper/Elbow")
elbow.AddTranslateOp().Set(Gf.Vec3d(arm_x + 0.6, arm_y, wheel_z))
elbow.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
elbow.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 1.0, 0.2)])
print(f"  ✓ ELBOW (yellow sphere)")

# LINK 2 - Green cylinder
link2 = UsdGeom.Cylinder.Define(stage, "/World/Piper/Link2")
link2.AddTranslateOp().Set(Gf.Vec3d(arm_x + 0.9, arm_y, wheel_z))
link2.AddScaleOp().Set(Gf.Vec3d(0.06, 0.3, 0.06))
link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 1.0, 0.4)])
print(f"  ✓ LINK 2 (green)")

# WRIST JOINT - Cyan sphere
wrist = UsdGeom.Sphere.Define(stage, "/World/Piper/Wrist")
wrist.AddTranslateOp().Set(Gf.Vec3d(arm_x + 1.2, arm_y, wheel_z))
wrist.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
wrist.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 1.0, 1.0)])
print(f"  ✓ WRIST (cyan sphere)")

print("✓ Complete Piper arm structure visible!")

# GRIPPER - Orange, OUTSIDE the wheel
print("\n[4/5] Mock Gripper...")
grip_x = wheel_x + wheel_radius + 0.15  # OUTSIDE wheel
grip_y = 0
grip_z = wheel_z

# Gripper base
gripper = UsdGeom.Cube.Define(stage, "/World/Gripper/Base")
gripper.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y, grip_z))
gripper.AddScaleOp().Set(Gf.Vec3d(0.1, 0.1, 0.1))
gripper.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])

# Finger 1 - pointing toward wheel
finger1 = UsdGeom.Cube.Define(stage, "/World/Gripper/Finger1")
finger1.AddTranslateOp().Set(Gf.Vec3d(grip_x - 0.08, grip_y - 0.06, grip_z))
finger1.AddScaleOp().Set(Gf.Vec3d(0.12, 0.03, 0.03))
finger1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.8, 0.4, 0.0)])

# Finger 2 - pointing toward wheel
finger2 = UsdGeom.Cube.Define(stage, "/World/Gripper/Finger2")
finger2.AddTranslateOp().Set(Gf.Vec3d(grip_x - 0.08, grip_y + 0.06, grip_z))
finger2.AddScaleOp().Set(Gf.Vec3d(0.12, 0.03, 0.03))
finger2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.8, 0.4, 0.0)])

print(f"✓ Orange gripper OUTSIDE wheel at ({grip_x}, {grip_y}, {grip_z})")

# CAMERA - Side view to see everything
print("\n[5/5] Camera...")
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
camera.AddTranslateOp().Set(Gf.Vec3d(0, -4.5, 3.0))  # Side view
camera.AddRotateXYZOp().Set(Gf.Vec3d(-30, 0, 0))
print("✓ Side view camera")

print("\n" + "=" * 70)
print(" YOU WILL SEE:")
print("=" * 70)
print("  LEFT SIDE:")
print("    ⚫ Gray BASE cylinder")
print("    🔴 Red SHOULDER sphere")
print("    🔵 Blue LINK 1 cylinder")
print("    🟡 Yellow ELBOW sphere")
print("    🟢 Green LINK 2 cylinder")
print("    🔵 Cyan WRIST sphere")
print("")
print("  RIGHT SIDE:")
print("    ⚫ Black STEERING WHEEL")
print("    🟠 Orange GRIPPER (OUTSIDE wheel)")
print("    🟠 Two orange FINGERS")
print("")
print("  Complete Piper arm structure clearly visible!")
print("=" * 70)

world.reset()

print("\n🎬 Static view - all components visible!\n")
print("Press Ctrl+C to exit")

try:
    while simulation_app.is_running():
        world.step(render=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nStopped")

simulation_app.close()
print("\nYou saw the complete Piper arm structure!")
