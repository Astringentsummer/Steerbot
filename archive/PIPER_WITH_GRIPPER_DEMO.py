#!/usr/bin/env python3
"""
REAL PIPER ARM with Mock Gripper Controlling G29 Wheel
Uses actual Piper URDF + gripper attached to wrist
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
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.nucleus import get_assets_root_path
from pxr import UsdGeom, Gf, UsdPhysics
import carb

print("=" * 70)
print(" REAL PIPER ARM + MOCK GRIPPER → G29 WHEEL")
print("=" * 70)

world = World()
world.scene.add_default_ground_plane()
stage = world.stage

# TABLE
print("\n[1/5] Creating table...")
table = UsdGeom.Cube.Define(stage, "/World/Table")
table.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.5))
table.AddScaleOp().Set(Gf.Vec3d(3.0, 2.0, 1.0))
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])
print("✓ Table created")

# STEERING WHEEL
print("\n[2/5] Creating G29 steering wheel...")
wheel_center_x = 0.5
wheel_center_y = 0
wheel_z = 1.8
wheel_radius = 0.35

wheel_rim = UsdGeom.Cylinder.Define(stage, "/World/SteeringWheel/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x, wheel_center_y, wheel_z))
wheel_rim.AddScaleOp().Set(Gf.Vec3d(wheel_radius, 0.05, wheel_radius))
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.1, 0.1)])

hub = UsdGeom.Sphere.Define(stage, "/World/SteeringWheel/Hub")
hub.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x, wheel_center_y, wheel_z))
hub.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
hub.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

for i in range(4):
    angle = i * np.pi / 2
    spoke = UsdGeom.Cylinder.Define(stage, f"/World/SteeringWheel/Spoke{i}")
    x_off = (wheel_radius - 0.1) * np.cos(angle)
    y_off = (wheel_radius - 0.1) * np.sin(angle)
    spoke.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + x_off, wheel_center_y + y_off, wheel_z))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.025, wheel_radius - 0.1, 0.025))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

print("✓ Steering wheel created")

# PIPER ARM - Try to load URDF
print("\n[3/5] Loading Piper arm...")
piper_urdf_path = "c:/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/piper_ros/src/piper_description/urdf/piper_v3.urdf"

try:
    # Import URDF
    from omni.importer.urdf import _urdf
    import_config = _urdf.ImportConfig()
    import_config.merge_fixed_joints = False
    import_config.fix_base = True
    import_config.import_inertia_tensor = True
    
    # Import at specific location
    piper_path = "/World/PiperArm"
    success, prim_path = _urdf.acquire_urdf_interface().parse_urdf(
        piper_urdf_path,
        piper_path,
        import_config
    )
    
    if success:
        print(f"✓ Piper URDF loaded at {prim_path}")
        
        # Position the arm
        piper_prim = stage.GetPrimAtPath(prim_path)
        xform = UsdGeom.Xformable(piper_prim)
        xform.ClearXformOpOrder()
        xform.AddTranslateOp().Set(Gf.Vec3d(-0.8, 0, 1.0))  # On table, left side
        
        # Create articulation
        piper_robot = world.scene.add(Articulation(prim_path=prim_path, name="piper"))
        
        print("✓ Piper arm positioned and articulated")
        use_real_piper = True
    else:
        print("⚠️  URDF import failed, using simplified arm")
        use_real_piper = False
        
except Exception as e:
    print(f"⚠️  Could not load URDF: {e}")
    print("   Using simplified arm representation")
    use_real_piper = False

# If URDF failed, create simplified arm
if not use_real_piper:
    print("\n[3/5] Creating simplified Piper arm...")
    arm_base_x = -0.8
    
    base = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Base")
    base.AddTranslateOp().Set(Gf.Vec3d(arm_base_x, 0, 1.1))
    base.AddScaleOp().Set(Gf.Vec3d(0.12, 0.1, 0.12))
    base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])
    
    link1 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link1")
    link1.AddTranslateOp().Set(Gf.Vec3d(arm_base_x + 0.2, 0, wheel_z))
    link1.AddScaleOp().Set(Gf.Vec3d(0.05, 0.2, 0.05))
    link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 1.0)])
    
    link2 = UsdGeom.Cylinder.Define(stage, "/World/PiperArm/Link2")
    link2.AddTranslateOp().Set(Gf.Vec3d(arm_base_x + 0.5, 0, wheel_z))
    link2.AddScaleOp().Set(Gf.Vec3d(0.05, 0.2, 0.05))
    link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 1.0, 0.4)])
    
    wrist = UsdGeom.Sphere.Define(stage, "/World/PiperArm/Wrist")
    wrist.AddTranslateOp().Set(Gf.Vec3d(arm_base_x + 0.7, 0, wheel_z))
    wrist.AddScaleOp().Set(Gf.Vec3d(0.06, 0.06, 0.06))
    wrist.CreateDisplayColorAttr().Set([Gf.Vec3f(0.5, 0.5, 0.5)])
    
    print("✓ Simplified arm created")

# MOCK GRIPPER - Attached to wrist
print("\n[4/5] Creating mock gripper attached to wrist...")
gripper_base = UsdGeom.Cube.Define(stage, "/World/MockGripper/Base")
gripper_base.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + wheel_radius, 0, wheel_z))
gripper_base.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
gripper_base.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])

# Gripper fingers
finger1 = UsdGeom.Cube.Define(stage, "/World/MockGripper/Finger1")
finger1.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + wheel_radius, -0.05, wheel_z))
finger1.AddScaleOp().Set(Gf.Vec3d(0.03, 0.08, 0.03))
finger1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.8, 0.4, 0.0)])

finger2 = UsdGeom.Cube.Define(stage, "/World/MockGripper/Finger2")
finger2.AddTranslateOp().Set(Gf.Vec3d(wheel_center_x + wheel_radius, +0.05, wheel_z))
finger2.AddScaleOp().Set(Gf.Vec3d(0.03, 0.08, 0.03))
finger2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.8, 0.4, 0.0)])

print("✓ Mock gripper with fingers created")

# CAMERA
print("\n[5/5] Setting camera...")
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
camera.AddTranslateOp().Set(Gf.Vec3d(0, -3.5, 2.5))
camera.AddRotateXYZOp().Set(Gf.Vec3d(-35, 0, 0))
print("✓ Camera positioned")

print("\n" + "=" * 70)
print(" SCENE READY:")
print("=" * 70)
print("  🟫 Table")
print("  ⚫ G29 steering wheel")
print("  🤖 Piper arm (URDF or simplified)")
print("  🟠 Mock gripper with fingers")
print("  🎯 Gripper will control the wheel!")
print("=" * 70)

class Controller:
    def __init__(self, stage, use_real_piper):
        self.stage = stage
        self.time = 0
        self.use_real_piper = use_real_piper
        self.wheel_angle = 0
        
        self.wheel_rim = stage.GetPrimAtPath("/World/SteeringWheel/Rim")
        self.hub = stage.GetPrimAtPath("/World/SteeringWheel/Hub")
        self.spokes = [stage.GetPrimAtPath(f"/World/SteeringWheel/Spoke{i}") for i in range(4)]
        
        if not use_real_piper:
            self.link1 = stage.GetPrimAtPath("/World/PiperArm/Link1")
            self.link2 = stage.GetPrimAtPath("/World/PiperArm/Link2")
            self.wrist = stage.GetPrimAtPath("/World/PiperArm/Wrist")
        
        self.gripper_base = stage.GetPrimAtPath("/World/MockGripper/Base")
        self.finger1 = stage.GetPrimAtPath("/World/MockGripper/Finger1")
        self.finger2 = stage.GetPrimAtPath("/World/MockGripper/Finger2")
        
        self.wheel_center_x = 0.5
        self.wheel_center_y = 0
        self.wheel_z = 1.8
        self.wheel_radius = 0.35
        self.arm_base_x = -0.8
    
    def update(self, dt):
        self.time += dt
        self.wheel_angle = np.sin(self.time * 0.4) * 0.8
        
        # Gripper position on wheel rim
        grip_x = self.wheel_center_x + self.wheel_radius * np.cos(self.wheel_angle)
        grip_y = self.wheel_center_y + self.wheel_radius * np.sin(self.wheel_angle)
        
        # Update simplified arm if not using real Piper
        if not self.use_real_piper:
            target_x = grip_x - self.arm_base_x
            target_y = grip_y
            
            r = np.sqrt(target_x**2 + target_y**2)
            r = np.clip(r, 0.1, 0.39)
            theta = np.arctan2(target_y, target_x)
            
            L1 = 0.2
            L2 = 0.2
            cos_q2 = (r**2 - L1**2 - L2**2) / (2 * L1 * L2)
            cos_q2 = np.clip(cos_q2, -1, 1)
            q2 = np.arccos(cos_q2)
            beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
            q1 = theta - beta
            
            # Update links
            link1_x = self.arm_base_x + L1 * np.cos(q1)
            link1_y = L1 * np.sin(q1)
            
            xform1 = UsdGeom.Xformable(self.link1)
            xform1.ClearXformOpOrder()
            xform1.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, self.wheel_z))
            xform1.AddOrientOp().Set(Gf.Quatf(np.cos(q1/2), 0, 0, np.sin(q1/2)))
            xform1.AddScaleOp().Set(Gf.Vec3d(0.05, L1, 0.05))
            
            link2_x = link1_x + L2 * np.cos(q1 + q2)
            link2_y = link1_y + L2 * np.sin(q1 + q2)
            
            xform2 = UsdGeom.Xformable(self.link2)
            xform2.ClearXformOpOrder()
            xform2.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, self.wheel_z))
            xform2.AddOrientOp().Set(Gf.Quatf(np.cos((q1+q2)/2), 0, 0, np.sin((q1+q2)/2)))
            xform2.AddScaleOp().Set(Gf.Vec3d(0.05, L2, 0.05))
            
            wrist_x = link2_x + L2 * np.cos(q1 + q2)
            wrist_y = link2_y + L2 * np.sin(q1 + q2)
            
            xform_wrist = UsdGeom.Xformable(self.wrist)
            xform_wrist.ClearXformOpOrder()
            xform_wrist.AddTranslateOp().Set(Gf.Vec3d(wrist_x, wrist_y, self.wheel_z))
            xform_wrist.AddScaleOp().Set(Gf.Vec3d(0.06, 0.06, 0.06))
        
        # Update gripper
        xform_gripper = UsdGeom.Xformable(self.gripper_base)
        xform_gripper.ClearXformOpOrder()
        xform_gripper.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y, self.wheel_z))
        xform_gripper.AddScaleOp().Set(Gf.Vec3d(0.08, 0.08, 0.08))
        
        # Update fingers
        xform_f1 = UsdGeom.Xformable(self.finger1)
        xform_f1.ClearXformOpOrder()
        xform_f1.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y - 0.05, self.wheel_z))
        xform_f1.AddScaleOp().Set(Gf.Vec3d(0.03, 0.08, 0.03))
        
        xform_f2 = UsdGeom.Xformable(self.finger2)
        xform_f2.ClearXformOpOrder()
        xform_f2.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y + 0.05, self.wheel_z))
        xform_f2.AddScaleOp().Set(Gf.Vec3d(0.03, 0.08, 0.03))
        
        # Rotate wheel
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

controller = Controller(stage, use_real_piper)
world.reset()

print("\n🎬 Piper arm with mock gripper controlling G29 wheel!\n")

frame = 0
try:
    while simulation_app.is_running():
        world.step(render=True)
        controller.update(1.0/60.0)
        frame += 1
        if frame % 180 == 0:
            angle_deg = np.degrees(controller.wheel_angle)
            print(f"✅ Frame {frame} - Mock gripper at {angle_deg:+.1f}°")
except KeyboardInterrupt:
    print("\n\nStopped")

simulation_app.close()
print("\nDemo complete!")
