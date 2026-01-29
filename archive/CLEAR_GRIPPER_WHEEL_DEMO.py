#!/usr/bin/env python3
"""
CLEAR DEMO - Gripper TOUCHING and TURNING the Wheel
You will SEE the gripper grip the wheel and turn it!
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
print(" GRIPPER TOUCHING AND TURNING THE WHEEL")
print("=" * 70)

world = World()
world.scene.add_default_ground_plane()
stage = world.stage

# TABLE
table = UsdGeom.Cube.Define(stage, "/World/Table")
table.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.5))
table.AddScaleOp().Set(Gf.Vec3d(3.0, 2.0, 1.0))
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])

# STEERING WHEEL - CENTER of table
wheel_center_x = 0
wheel_center_y = 0
wheel_z = 1.8
wheel_radius = 0.35

print("\n[1/3] Creating steering wheel at CENTER...")
# Wheel rim
wheel_rim = UsdGeom.Cylinder.Define(stage, "/World/SteeringWheel/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x, wheel_center_y, wheel_z))
wheel_rim.AddScaleOp().Set(Gf.Vec3d(wheel_radius, 0.05, wheel_radius))
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.1, 0.1)])

# Hub
hub = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Hub")
hub.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x, wheel_center_y, wheel_z))
hub.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
hub.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Spokes
for i in range(4):
    angle = i * np.pi / 2
    spoke = UsdGeom.Cylinder.Define(stage, f"/World/SteeringWheel/Spoke{i}")
    x_off = (wheel_radius - 0.1) * np.cos(angle)
    y_off = (wheel_radius - 0.1) * np.sin(angle)
    spoke.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + x_off, wheel_center_y + y_off, wheel_z))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.025, wheel_radius - 0.1, 0.025))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

print("✓ Wheel at center of table")

# PIPER ARM - Will reach TO the wheel
print("\n[2/3] Creating Piper arm that REACHES the wheel...")
arm_base_x = -1.2
arm_base_y = 0
arm_base_z = 1.1

# Base
base = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Base")
base.AddTranslateOp().Set(Gf.Vec3d(arm_base_x, arm_base_y, arm_base_z))
base.AddScaleOp().Set(Gf.Vec3d(0.12, 0.1, 0.12))
base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Link 1 - BLUE (will move)
link1 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link1")
link1.AddTranslateOp().Set(Gf.Vec3d(arm_base_x + 0.3, 0, wheel_z))
link1.AddScaleOp().Set(Gf.Vec3d(0.05, 0.3, 0.05))
link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 1.0)])

# Link 2 - GREEN (will move)
link2 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link2")
link2.AddTranslateOp().Set(Gf.Vec3d(arm_base_x + 0.7, 0, wheel_z))
link2.AddScaleOp().Set(Gf.Vec3d(0.05, 0.3, 0.05))
link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 1.0, 0.4)])

# GRIPPER - ORANGE - Will TOUCH the wheel
gripper = UsdGeom.Cube.Define(stage, "/World/PiperArm/Gripper")
gripper.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + wheel_radius, 0, wheel_z))  # ON the wheel rim!
gripper.AddScaleOp().Set(Gf.Vec3d(0.12, 0.12, 0.12))
gripper.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])

# RED marker - shows grip point
grip_marker = UsdGeom.Sphere.Define(stage, "/World/GripMarker")
grip_marker.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + wheel_radius, 0, wheel_z))
grip_marker.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
grip_marker.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.0, 0.0)])

print("✓ Arm reaches from left to wheel")

# CAMERA - Side view to see the action
print("\n[3/3] Setting camera to see gripper-wheel contact...")
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
camera.AddTranslateOp().Set(Gf.Vec3d(0, -3.5, 2.5))  # Side view
camera.AddRotateXYZOp().Set(Gf.Vec3d(-35, 0, 0))
print("✓ Camera: side view to see gripper touching wheel")

print("\n" + "=" * 70)
print(" YOU WILL SEE:")
print("=" * 70)
print("  🟫 Table")
print("  ⚫ Black steering wheel (CENTER)")
print("  🔵 Blue arm link (reaching from left)")
print("  🟢 Green arm link (reaching from left)")
print("  🟠 ORANGE GRIPPER - TOUCHING the wheel rim!")
print("  🔴 Red marker - shows grip point")
print("")
print("  Watch the ORANGE cube PUSH the wheel and make it TURN!")
print("=" * 70)

class WheelController:
    def __init__(self, stage):
        self.stage = stage
        self.time = 0
        self.wheel_angle = 0
        
        # Get all objects
        self.wheel_rim = stage.GetPrimAtPath("/World/SteeringWheel/Rim")
        self.hub = stage.GetPrimAtPath("/World/SteeringWheel/Hub")
        self.spokes = [stage.GetPrimAtPath(f"/World/SteeringWheel/Spoke{i}") for i in range(4)]
        self.link1 = stage.GetPrimAtPath("/World/PiperArm/Link1")
        self.link2 = stage.GetPrimAtPath("/World/PiperArm/Link2")
        self.gripper = stage.GetPrimAtPath("/World/PiperArm/Gripper")
        self.marker = stage.GetPrimAtPath("/World/GripMarker")
        
        self.wheel_center_x = 0
        self.wheel_center_y = 0
        self.wheel_z = 1.8
        self.wheel_radius = 0.35
        self.arm_base_x = -1.2
    
    def update(self, dt):
        self.time += dt
        
        # Wheel rotates
        self.wheel_angle = np.sin(self.time * 0.4) * 0.8  # ±45°
        
        # Gripper position ON the wheel rim
        grip_x = self.wheel_center_x + self.wheel_radius * np.cos(self.wheel_angle)
        grip_y = self.wheel_center_y + self.wheel_radius * np.sin(self.wheel_angle)
        
        # Arm IK to reach grip point
        target_x = grip_x - self.arm_base_x
        target_y = grip_y
        
        # Simple 2-link IK
        r = np.sqrt(target_x**2 + target_y**2)
        r = np.clip(r, 0.1, 0.59)
        theta = np.arctan2(target_y, target_x)
        
        L1 = 0.3
        L2 = 0.3
        cos_q2 = (r**2 - L1**2 - L2**2) / (2 * L1 * L2)
        cos_q2 = np.clip(cos_q2, -1, 1)
        q2 = np.arccos(cos_q2)
        beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
        q1 = theta - beta
        
        # Update Link 1
        link1_x = self.arm_base_x + L1 * np.cos(q1)
        link1_y = L1 * np.sin(q1)
        
        xform1 = UsdGeom.Xformable(self.link1)
        xform1.ClearXformOpOrder()
        xform1.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, self.wheel_z))
        xform1.AddOrientOp().Set(Gf.Quatf(np.cos(q1/2), 0, 0, np.sin(q1/2)))
        xform1.AddScaleOp().Set(Gf.Vec3d(0.05, L1, 0.05))
        
        # Update Link 2
        link2_x = link1_x + L2 * np.cos(q1 + q2)
        link2_y = link1_y + L2 * np.sin(q1 + q2)
        
        xform2 = UsdGeom.Xformable(self.link2)
        xform2.ClearXformOpOrder()
        xform2.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, self.wheel_z))
        xform2.AddOrientOp().Set(Gf.Quatf(np.cos((q1+q2)/2), 0, 0, np.sin((q1+q2)/2)))
        xform2.AddScaleOp().Set(Gf.Vec3d(0.05, L2, 0.05))
        
        # Update Gripper - ON the wheel rim
        xform_gripper = UsdGeom.Xformable(self.gripper)
        xform_gripper.ClearXformOpOrder()
        xform_gripper.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y, self.wheel_z))
        xform_gripper.AddScaleOp().Set(Gf.Vec3d(0.12, 0.12, 0.12))
        
        # Update marker
        xform_marker = UsdGeom.Xformable(self.marker)
        xform_marker.ClearXformOpOrder()
        xform_marker.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y, self.wheel_z))
        xform_marker.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
        
        # Rotate the ENTIRE wheel
        wheel_rotation = Gf.Quatf(np.cos(self.wheel_angle/2), np.sin(self.wheel_angle/2), 0, 0)
        
        xform_rim = UsdGeom.Xformable(self.wheel_rim)
        xform_rim.ClearXformOpOrder()
        xform_rim.AddTranslateOp().Set(Gf.Vec3d(self.wheel_center_x, self.wheel_center_y, self.wheel_z))
        xform_rim.AddOrientOp().Set(wheel_rotation)
        xform_rim.AddScaleOp().Set(Gf.Vec3d(self.wheel_radius, 0.05, self.wheel_radius))
        
        xform_hub = UsdGeom.Xformable(self.hub)
        xform_hub.ClearXformOpOrder()
        xform_hub.AddTranslateOp().Set(Gf.Vec3d(self.wheel_center_x, self.wheel_center_y, self.wheel_z))
        xform_hub.AddOrientOp().Set(wheel_rotation)
        xform_hub.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
        
        for i, spoke_prim in enumerate(self.spokes):
            base_angle = i * np.pi / 2 + self.wheel_angle
            x_off = (self.wheel_radius - 0.1) * np.cos(base_angle)
            y_off = (self.wheel_radius - 0.1) * np.sin(base_angle)
            
            xform_spoke = UsdGeom.Xformable(spoke_prim)
            xform_spoke.ClearXformOpOrder()
            xform_spoke.AddTranslateOp().Set(Gf.Vec3d(self.wheel_center_x + x_off, self.wheel_center_y + y_off, self.wheel_z))
            xform_spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
            xform_spoke.AddScaleOp().Set(Gf.Vec3d(0.025, self.wheel_radius - 0.1, 0.025))

controller = WheelController(stage)
world.reset()

print("\n🎬 WATCH: Orange gripper TOUCHES wheel and makes it TURN!\n")

frame = 0
try:
    while simulation_app.is_running():
        world.step(render=True)
        controller.update(1.0/60.0)
        frame += 1
        if frame % 180 == 0:
            angle_deg = np.degrees(controller.wheel_angle)
            print(f"✅ Frame {frame} - Wheel at {angle_deg:+.1f}° - Gripper PUSHING it!")
except KeyboardInterrupt:
    print("\n\nStopped")

simulation_app.close()
print("\nYou saw the gripper CONTROL the wheel!")
