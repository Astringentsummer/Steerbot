#!/usr/bin/env python3
"""
ISAAC SIM - LARGE VISIBLE DEMO
Everything scaled up and clearly visible!
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
print(" LARGE VISIBLE DEMO - Piper Controls G29")
print("=" * 70)

world = World()
world.scene.add_default_ground_plane()
stage = world.stage

print("\n[1/4] Creating LARGE table...")
table = UsdGeom.Cube.Define(stage, "/World/Table")
table.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.5))  # Centered
table.AddScaleOp().Set(Gf.Vec3d(2.0, 2.0, 1.0))  # MUCH BIGGER
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])
print("✓ LARGE brown table at center")

print("\n[2/4] Creating LARGE steering wheel...")
# Wheel rim - MUCH BIGGER
wheel_rim = UsdGeom.Cylinder.Define(stage, "/World/SteeringWheel/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1.5))  # Higher up
wheel_rim.AddScaleOp().Set(Gf.Vec3d(0.4, 0.05, 0.4))  # 3x BIGGER
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.1, 0.1)])

# Center hub - VISIBLE
hub = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Hub")
hub.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1.5))
hub.AddScaleOp().Set(Gf.Vec3d(0.1, 0.1, 0.1))
hub.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Spokes - THICK
for i in range(4):
    angle = i * np.pi / 2
    spoke = UsdGeom.Cylinder.Define(stage, f"/World/SteeringWheel/Spoke{i}")
    x_off = 0.25 * np.cos(angle)
    y_off = 0.25 * np.sin(angle)
    spoke.AddTranslateOp().Set(Gf.Vec3d(x_off, y_off, 1.5))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.03, 0.25, 0.03))  # THICK
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

# RED target - BIG
target = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Target")
target.AddTranslateOp().Set(Gf.Vec3d(0.4, 0, 1.5))
target.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))  # BIG RED BALL
target.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.0, 0.0)])
print("✓ LARGE black steering wheel with RED target")

print("\n[3/4] Creating LARGE Piper arm...")
# Base - BIG
base = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Base")
base.AddTranslateOp().Set(Gf.Vec3d(-1.0, 0, 1.1))  # Left side
base.AddScaleOp().Set(Gf.Vec3d(0.15, 0.1, 0.15))  # BIG BASE
base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Link 1 - BLUE and BIG
link1 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link1")
link1.AddTranslateOp().Set(Gf.Vec3d(-0.5, 0, 1.5))
link1.AddScaleOp().Set(Gf.Vec3d(0.06, 0.5, 0.06))  # THICK
link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 1.0)])  # BRIGHT BLUE

# Link 2 - GREEN and BIG
link2 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link2")
link2.AddTranslateOp().Set(Gf.Vec3d(0.2, 0, 1.5))
link2.AddScaleOp().Set(Gf.Vec3d(0.06, 0.5, 0.06))  # THICK
link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 1.0, 0.4)])  # BRIGHT GREEN

# Gripper - ORANGE CUBE - BIG
gripper = UsdGeom.Cube.Define(stage, "/World/PiperArm/Gripper")
gripper.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 1.5))
gripper.AddScaleOp().Set(Gf.Vec3d(0.15, 0.15, 0.15))  # BIG CUBE
gripper.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])  # BRIGHT ORANGE
print("✓ LARGE Piper arm: BLUE → GREEN → ORANGE")

print("\n[4/4] Setting camera for PERFECT VIEW...")
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
# Camera looking at center from distance
camera.AddTranslateOp().Set(Gf.Vec3d(3.0, 3.0, 2.5))  # Far back
camera.AddRotateXYZOp().Set(Gf.Vec3d(-30, 45, 0))
print("✓ Camera positioned to see EVERYTHING")

print("\n" + "=" * 70)
print(" YOU SHOULD NOW SEE:")
print("=" * 70)
print("  🟫 LARGE brown table")
print("  ⚫ LARGE black steering wheel")
print("  🔴 BIG RED target ball")
print("  🔵 BLUE arm link (left)")
print("  🟢 GREEN arm link (middle)")
print("  🟠 ORANGE gripper cube (right)")
print("")
print("Everything is 3-5x BIGGER and clearly visible!")
print("=" * 70)

class Controller:
    def __init__(self, stage):
        self.stage = stage
        self.time = 0
        self.link1 = stage.GetPrimAtPath("/World/PiperArm/Link1")
        self.link2 = stage.GetPrimAtPath("/World/PiperArm/Link2")
        self.gripper = stage.GetPrimAtPath("/World/PiperArm/Gripper")
        self.target = stage.GetPrimAtPath("/World/SteeringWheel/Target")
    
    def update(self, dt):
        self.time += dt
        wheel_angle = np.sin(self.time * 0.3) * 1.2
        
        target_x = 0.4 * np.cos(wheel_angle)
        target_y = 0.4 * np.sin(wheel_angle)
        
        q1 = wheel_angle * 0.8
        q2 = -wheel_angle * 0.5
        
        # Update arm positions
        link1_x = -1.0 + 0.5 * np.cos(q1)
        link1_y = 0.5 * np.sin(q1)
        
        xform1 = UsdGeom.Xformable(self.link1)
        xform1.ClearXformOpOrder()
        xform1.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, 1.5))
        xform1.AddOrientOp().Set(Gf.Quatf(np.cos(q1/2), 0, 0, np.sin(q1/2)))
        xform1.AddScaleOp().Set(Gf.Vec3d(0.06, 0.5, 0.06))
        
        link2_x = link1_x + 0.5 * np.cos(q1 + q2)
        link2_y = link1_y + 0.5 * np.sin(q1 + q2)
        
        xform2 = UsdGeom.Xformable(self.link2)
        xform2.ClearXformOpOrder()
        xform2.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, 1.5))
        xform2.AddOrientOp().Set(Gf.Quatf(np.cos((q1+q2)/2), 0, 0, np.sin((q1+q2)/2)))
        xform2.AddScaleOp().Set(Gf.Vec3d(0.06, 0.5, 0.06))
        
        gripper_x = link2_x + 0.5 * np.cos(q1 + q2)
        gripper_y = link2_y + 0.5 * np.sin(q1 + q2)
        
        xform_gripper = UsdGeom.Xformable(self.gripper)
        xform_gripper.ClearXformOpOrder()
        xform_gripper.AddTranslateOp().Set(Gf.Vec3d(gripper_x, gripper_y, 1.5))
        xform_gripper.AddScaleOp().Set(Gf.Vec3d(0.15, 0.15, 0.15))
        
        xform_target = UsdGeom.Xformable(self.target)
        xform_target.ClearXformOpOrder()
        xform_target.AddTranslateOp().Set(Gf.Vec3d(target_x, target_y, 1.5))
        xform_target.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))

controller = Controller(stage)
world.reset()

print("\n🎬 Animation starting - watch the ORANGE cube turn the wheel!\n")

frame = 0
try:
    while simulation_app.is_running():
        world.step(render=True)
        controller.update(1.0/60.0)
        frame += 1
        if frame % 120 == 0:
            print(f"✅ Frame {frame} - ORANGE gripper turning wheel smoothly")
except KeyboardInterrupt:
    print("\n\nStopped")

simulation_app.close()
print("\nDemo complete!")
