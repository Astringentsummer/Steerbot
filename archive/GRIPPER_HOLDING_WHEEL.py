#!/usr/bin/env python3
"""
G29 + PIPER ARM - GRIPPER HOLDING STEERING WHEEL
The arm gripper now HOLDS the steering wheel!
"""

import sys
import os
import numpy as np
import time

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

config = {"headless": False, "width": 1920, "height": 1080}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from pxr import Gf, UsdGeom
import omni.usd

print("="*70)
print(" G29 + PIPER - GRIPPER HOLDING STEERING WHEEL")
print("="*70)

# ============================================================================
# CREATE WORLD
# ============================================================================
print("\n[1/4] Creating world...")
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()
print("✓ World created")

# ============================================================================
# CREATE TABLE AND STEERING WHEEL SETUP
# ============================================================================
print("\n[2/4] Creating table and steering wheel...")

stage = omni.usd.get_context().get_stage()

# Table
table_path = "/World/Table"
table = UsdGeom.Cube.Define(stage, table_path)
table.GetSizeAttr().Set(1.0)
table_xform = UsdGeom.Xformable(stage.GetPrimAtPath(table_path))
table_xform.AddScaleOp().Set(Gf.Vec3f(1.2, 0.8, 0.05))
table_xform.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.4))

# Steering wheel column (fixed to table)
column_path = "/World/WheelColumn"
column = UsdGeom.Cylinder.Define(stage, column_path)
column.GetRadiusAttr().Set(0.03)
column.GetHeightAttr().Set(0.4)
column.GetAxisAttr().Set("Z")
UsdGeom.Xformable(stage.GetPrimAtPath(column_path)).AddTranslateOp().Set(Gf.Vec3d(0.3, 0, 0.625))

# Steering wheel (at end of column)
wheel_path = "/World/SteeringWheel"
wheel = UsdGeom.Torus.Define(stage, wheel_path)
wheel.GetRadiusAttr().Set(0.15)  # Outer radius
wheel.GetAxisAttr().Set("Z")

print("✓ Table and steering wheel created")

# ============================================================================
# CREATE PIPER ARM (POSITIONED TO REACH WHEEL)
# ============================================================================
print("\n[3/4] Creating Piper arm...")

# Arm base (on table, positioned to reach wheel)
base_path = "/World/ArmBase"
base = UsdGeom.Cylinder.Define(stage, base_path)
base.GetRadiusAttr().Set(0.05)
base.GetHeightAttr().Set(0.1)
base.GetAxisAttr().Set("Z")
UsdGeom.Xformable(stage.GetPrimAtPath(base_path)).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.475))

# Link 1 (shoulder to elbow) - 0.25m
link1_path = "/World/Link1"
link1 = UsdGeom.Cylinder.Define(stage, link1_path)
link1.GetRadiusAttr().Set(0.025)
link1.GetHeightAttr().Set(0.25)
link1.GetAxisAttr().Set("X")

# Link 2 (elbow to wrist) - 0.25m
link2_path = "/World/Link2"
link2 = UsdGeom.Cylinder.Define(stage, link2_path)
link2.GetRadiusAttr().Set(0.02)
link2.GetHeightAttr().Set(0.25)
link2.GetAxisAttr().Set("X")

# Gripper (two fingers)
gripper_left_path = "/World/GripperLeft"
gripper_left = UsdGeom.Cube.Define(stage, gripper_left_path)
gripper_left.GetSizeAttr().Set(1.0)

gripper_right_path = "/World/GripperRight"
gripper_right = UsdGeom.Cube.Define(stage, gripper_right_path)
gripper_right.GetSizeAttr().Set(1.0)

print("✓ Piper arm created")

# ============================================================================
# IK SOLVER FOR ARM TO GRIP WHEEL
# ============================================================================
print("\n[4/4] Setting up IK control...")

def compute_ik_to_wheel(wheel_angle_rad):
    """
    Compute IK for arm to grip the steering wheel
    Wheel is at (0.3, 0, 0.825) and rotates
    Gripper needs to be on the wheel rim
    """
    L1 = 0.25  # Link 1 length
    L2 = 0.25  # Link 2 length
    
    # Wheel center position
    wheel_center_x = 0.3
    wheel_center_y = 0.0
    wheel_center_z = 0.825
    
    # Gripper position on wheel rim (rotates with wheel)
    wheel_radius = 0.15
    grip_x = wheel_center_x + wheel_radius * np.cos(wheel_angle_rad)
    grip_y = wheel_center_y + wheel_radius * np.sin(wheel_angle_rad)
    grip_z = wheel_center_z
    
    # Arm base position
    base_x = 0.0
    base_y = 0.0
    base_z = 0.525
    
    # Target relative to base
    target_x = grip_x - base_x
    target_y = grip_y - base_y
    target_z = grip_z - base_z
    
    # 2D IK in XY plane (ignoring Z for now)
    r = np.sqrt(target_x**2 + target_y**2)
    r = np.clip(r, 0.05, L1 + L2 - 0.05)
    
    theta = np.arctan2(target_y, target_x)
    cos_q2 = np.clip((r**2 - L1**2 - L2**2) / (2 * L1 * L2), -1, 1)
    q2 = np.arccos(cos_q2)
    beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    q1 = theta - beta
    
    return q1, q2, grip_x, grip_y, grip_z

def update_arm_and_gripper(q1, q2, grip_x, grip_y, grip_z):
    """Update arm visualization to show gripper holding wheel"""
    L1 = 0.25
    L2 = 0.25
    base_z = 0.525
    
    # Link 1 position
    link1_x = (L1/2) * np.cos(q1)
    link1_y = (L1/2) * np.sin(q1)
    link1_z = base_z
    
    link1_xform = UsdGeom.Xformable(stage.GetPrimAtPath(link1_path))
    link1_xform.ClearXformOpOrder()
    link1_xform.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, link1_z))
    link1_xform.AddRotateZOp().Set(np.degrees(q1))
    
    # Link 2 position
    elbow_x = L1 * np.cos(q1)
    elbow_y = L1 * np.sin(q1)
    
    link2_x = elbow_x + (L2/2) * np.cos(q1 + q2)
    link2_y = elbow_y + (L2/2) * np.sin(q1 + q2)
    link2_z = base_z
    
    link2_xform = UsdGeom.Xformable(stage.GetPrimAtPath(link2_path))
    link2_xform.ClearXformOpOrder()
    link2_xform.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, link2_z))
    link2_xform.AddRotateZOp().Set(np.degrees(q1 + q2))
    
    # Gripper fingers (gripping wheel)
    gripper_angle = q1 + q2
    
    # Left finger
    left_xform = UsdGeom.Xformable(stage.GetPrimAtPath(gripper_left_path))
    left_xform.ClearXformOpOrder()
    left_xform.AddScaleOp().Set(Gf.Vec3f(0.06, 0.02, 0.08))
    left_xform.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y + 0.03, grip_z))
    left_xform.AddRotateZOp().Set(np.degrees(gripper_angle))
    
    # Right finger
    right_xform = UsdGeom.Xformable(stage.GetPrimAtPath(gripper_right_path))
    right_xform.ClearXformOpOrder()
    right_xform.AddScaleOp().Set(Gf.Vec3f(0.06, 0.02, 0.08))
    right_xform.AddTranslateOp().Set(Gf.Vec3d(grip_x, grip_y - 0.03, grip_z))
    right_xform.AddRotateZOp().Set(np.degrees(gripper_angle))

def update_steering_wheel(angle_rad):
    """Rotate steering wheel"""
    wheel_xform = UsdGeom.Xformable(stage.GetPrimAtPath(wheel_path))
    wheel_xform.ClearXformOpOrder()
    wheel_xform.AddTranslateOp().Set(Gf.Vec3d(0.3, 0, 0.825))
    wheel_xform.AddRotateZOp().Set(np.degrees(angle_rad))

print("✓ IK solver ready")

# ============================================================================
# RUN DEMO
# ============================================================================
print("\n" + "="*70)
print(" DEMO RUNNING - GRIPPER HOLDING WHEEL!")
print("="*70)
print("\nThe Piper arm gripper is now HOLDING the steering wheel")
print("Watch as the wheel turns and the arm follows!")
print("\nPress Ctrl+C to stop")
print("="*70 + "\n")

world.reset()

try:
    step_count = 0
    start_time = time.time()
    
    while simulation_app.is_running():
        world.step(render=True)
        
        # Virtual steering (sine wave)
        elapsed = time.time() - start_time
        steer = np.sin(elapsed * 0.5) * 0.6  # ±0.6 for smoother motion
        
        # Wheel angle in radians
        wheel_angle = steer * 1.5  # ±90 degrees
        
        # Update wheel rotation
        update_steering_wheel(wheel_angle)
        
        # Compute IK for arm to grip wheel
        q1, q2, grip_x, grip_y, grip_z = compute_ik_to_wheel(wheel_angle)
        
        # Update arm and gripper
        update_arm_and_gripper(q1, q2, grip_x, grip_y, grip_z)
        
        # Status
        if step_count % 60 == 0:
            print(f"Wheel: {np.degrees(wheel_angle):+6.1f}° | Grip: ({grip_x:.2f}, {grip_y:.2f}) | Arm: ({np.degrees(q1):+6.1f}°, {np.degrees(q2):+6.1f}°)")
        
        step_count += 1

except KeyboardInterrupt:
    print("\n\nStopping...")

simulation_app.close()
print("\n" + "="*70)
print(" DEMO COMPLETE - GRIPPER WAS HOLDING WHEEL!")
print("="*70)
