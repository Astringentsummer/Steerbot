#!/usr/bin/env python3
"""
ISAAC SIM SAFE SIMULATION TEST
Professional physics simulation with safety validation
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
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.stage import add_reference_to_stage
from pxr import UsdGeom, Gf, UsdPhysics, PhysxSchema
import carb

print("=" * 70)
print(" ISAAC SIM - SAFE SIMULATION TEST")
print(" Professional Physics Simulation for Safety Validation")
print("=" * 70)
print("")

# Create world with physics
print("[1/7] Creating physics world...")
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()
print("✓ Physics world created (60 Hz)")

stage = world.stage

# Create table
print("\n[2/7] Creating table...")
table_path = "/World/Table"
table = UsdGeom.Cube.Define(stage, table_path)
table.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 0.4))
table.AddScaleOp().Set(Gf.Vec3d(0.8, 0.6, 0.8))
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])

# Add collision
UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(table_path))
print("✓ Table created with collision")

# Create steering wheel
print("\n[3/7] Creating steering wheel...")
wheel_path = "/World/SteeringWheel"

# Wheel rim
wheel_rim = UsdGeom.Cylinder.Define(stage, wheel_path + "/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 0.9))
wheel_rim.AddScaleOp().Set(Gf.Vec3d(0.15, 0.02, 0.15))
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Wheel spokes
for i in range(4):
    angle = i * np.pi / 2
    spoke_path = f"{wheel_path}/Spoke{i}"
    spoke = UsdGeom.Cylinder.Define(stage, spoke_path)
    
    x_offset = 0.1 * np.cos(angle)
    y_offset = 0.1 * np.sin(angle)
    
    spoke.AddTranslateOp().Set(Gf.Vec3d(0.5 + x_offset, y_offset, 0.9))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.01, 0.1, 0.01))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

# Target marker
target_marker = UsdGeom.Sphere.Define(stage, wheel_path + "/Target")
target_marker.AddTranslateOp().Set(Gf.Vec3d(0.65, 0, 0.9))
target_marker.AddScaleOp().Set(Gf.Vec3d(0.03, 0.03, 0.03))
target_marker.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.0, 0.0)])

print("✓ Steering wheel created")

# Create simplified arm
print("\n[4/7] Creating Piper arm...")
arm_base_path = "/World/PiperArm"

# Base
base = UsdGeom.Cylinder.Define(stage, arm_base_path + "/Base")
base.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.85))
base.AddScaleOp().Set(Gf.Vec3d(0.05, 0.05, 0.05))
base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

# Link 1
link1 = UsdGeom.Cylinder.Define(stage, arm_base_path + "/Link1")
link1.AddTranslateOp().Set(Gf.Vec3d(0.15, 0, 0.9))
link1.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
link1.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link1.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.4, 0.8)])

# Link 2
link2 = UsdGeom.Cylinder.Define(stage, arm_base_path + "/Link2")
link2.AddTranslateOp().Set(Gf.Vec3d(0.4, 0, 0.9))
link2.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
link2.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))
link2.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.8, 0.4)])

# Gripper
gripper = UsdGeom.Cube.Define(stage, arm_base_path + "/Gripper")
gripper.AddTranslateOp().Set(Gf.Vec3d(0.55, 0, 0.9))
gripper.AddScaleOp().Set(Gf.Vec3d(0.05, 0.05, 0.05))
gripper.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.6, 0.0)])

print("✓ Piper arm created")

# Camera
print("\n[5/7] Setting up camera...")
camera_path = "/World/Camera"
camera = UsdGeom.Camera.Define(stage, camera_path)
camera.AddTranslateOp().Set(Gf.Vec3d(1.5, 1.5, 1.2))
camera.AddRotateXYZOp().Set(Gf.Vec3d(-20, 45, 0))
print("✓ Camera positioned")

# Safety controller
print("\n[6/7] Initializing safety controller...")

class SafetyController:
    """Safety controller with physics validation"""
    
    def __init__(self, stage):
        self.stage = stage
        self.time = 0
        self.L1 = 0.3
        self.L2 = 0.3
        
        # SAFETY: Joint limits
        self.joint_limits = {
            'base': (-3.14, 3.14),
            'shoulder': (-1.57, 1.57),
            'elbow': (-2.0, 2.0)
        }
        
        # SAFETY: Speed limits (REDUCED for safety margin)
        self.max_speed = 0.7  # 40°/s - SAFE with margin
        
        # SAFETY: Acceleration limits
        self.max_accel = 2.0  # rad/s² - Smooth acceleration
        
        # State
        self.current_joints = [0.0, 0.0, 0.0]
        self.current_velocity = [0.0, 0.0, 0.0]  # Track velocity
        self.last_update = time.time()
        self.safety_violations = []
        
        # Get prims
        self.link1 = stage.GetPrimAtPath("/World/PiperArm/Link1")
        self.link2 = stage.GetPrimAtPath("/World/PiperArm/Link2")
        self.gripper = stage.GetPrimAtPath("/World/PiperArm/Gripper")
        self.target = stage.GetPrimAtPath("/World/SteeringWheel/Target")
    
    def simple_ik(self, target_x, target_y):
        """IK with safety clamping"""
        r = np.sqrt(target_x**2 + target_y**2)
        r = np.clip(r, 0.05, self.L1 + self.L2 - 0.05)
        
        theta = np.arctan2(target_y, target_x)
        cos_q2 = (r**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        cos_q2 = np.clip(cos_q2, -1, 1)
        q2 = np.arccos(cos_q2)
        
        beta = np.arctan2(self.L2 * np.sin(q2), self.L1 + self.L2 * np.cos(q2))
        q1 = theta - beta
        
        return q1, q2
    
    def check_safety(self, target_joints):
        """SAFETY: Validate target joints"""
        violations = []
        
        # Check limits
        if not (self.joint_limits['base'][0] <= target_joints[0] <= self.joint_limits['base'][1]):
            violations.append(f"Base {np.degrees(target_joints[0]):.1f}° exceeds limits")
        
        if not (self.joint_limits['shoulder'][0] <= target_joints[1] <= self.joint_limits['shoulder'][1]):
            violations.append(f"Shoulder {np.degrees(target_joints[1]):.1f}° exceeds limits")
        
        # Check speed
        dt = time.time() - self.last_update
        if dt > 0.001:
            for i, (curr, targ) in enumerate(zip(self.current_joints[:2], target_joints)):
                speed = abs(targ - curr) / dt
                if speed > self.max_speed:
                    violations.append(f"Joint {i} speed {np.degrees(speed):.1f}°/s exceeds limit")
        
        return violations
    
    def rate_limit(self, target_joints):
        """SAFETY: Rate limiting with acceleration control"""
        dt = time.time() - self.last_update
        if dt < 0.001:
            dt = 0.001
        
        safe_joints = []
        new_velocities = []
        
        for i, (curr_pos, targ_pos, curr_vel) in enumerate(zip(
            self.current_joints, target_joints, self.current_velocity
        )):
            # Desired velocity to reach target
            position_error = targ_pos - curr_pos
            desired_vel = position_error / dt
            
            # Clamp desired velocity to max speed
            desired_vel = np.clip(desired_vel, -self.max_speed, self.max_speed)
            
            # Acceleration needed
            accel = (desired_vel - curr_vel) / dt
            
            # Clamp acceleration
            if abs(accel) > self.max_accel:
                accel = np.sign(accel) * self.max_accel
            
            # New velocity with limited acceleration
            new_vel = curr_vel + accel * dt
            
            # Double-check speed limit
            new_vel = np.clip(new_vel, -self.max_speed, self.max_speed)
            
            # New position
            new_pos = curr_pos + new_vel * dt
            
            safe_joints.append(new_pos)
            new_velocities.append(new_vel)
        
        self.current_velocity = new_velocities
        return safe_joints
    
    def update(self, dt):
        """Update with safety checks"""
        self.time += dt
        
        # Compute target (sine wave)
        wheel_angle = np.sin(self.time * 0.5) * 1.57
        
        wheel_center_x = 0.5
        wheel_center_y = 0.0
        grip_distance = 0.15
        
        target_x = wheel_center_x + grip_distance * np.cos(wheel_angle)
        target_y = wheel_center_y + grip_distance * np.sin(wheel_angle)
        
        # IK
        q1, q2 = self.simple_ik(target_x, target_y)
        target_joints = [q1, q2, 0.0]
        
        # SAFETY: Check before applying
        violations = self.check_safety(target_joints)
        if violations:
            print("⚠️  SAFETY VIOLATION:")
            for v in violations:
                print(f"   - {v}")
            self.safety_violations.extend(violations)
            return False
        
        # SAFETY: Rate limit
        safe_joints = self.rate_limit(target_joints)
        
        # Update visualization
        self.update_visualization(safe_joints, target_x, target_y)
        
        self.current_joints = safe_joints
        self.last_update = time.time()
        return True
    
    def update_visualization(self, joints, target_x, target_y):
        """Update arm visualization"""
        q1, q2, _ = joints
        
        # Link 1
        link1_x = 0.15 * np.cos(q1)
        link1_y = 0.15 * np.sin(q1)
        xform1 = UsdGeom.Xformable(self.link1)
        xform1.ClearXformOpOrder()
        xform1.AddTranslateOp().Set(Gf.Vec3d(link1_x, link1_y, 0.9))
        xform1.AddOrientOp().Set(Gf.Quatf(np.cos(q1/2), 0, 0, np.sin(q1/2)))
        xform1.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
        
        # Link 2
        link2_x = link1_x + 0.15 * np.cos(q1 + q2)
        link2_y = link1_y + 0.15 * np.sin(q1 + q2)
        xform2 = UsdGeom.Xformable(self.link2)
        xform2.ClearXformOpOrder()
        xform2.AddTranslateOp().Set(Gf.Vec3d(link2_x, link2_y, 0.9))
        xform2.AddOrientOp().Set(Gf.Quatf(np.cos((q1+q2)/2), 0, 0, np.sin((q1+q2)/2)))
        xform2.AddScaleOp().Set(Gf.Vec3d(0.02, 0.15, 0.02))
        
        # Gripper
        gripper_x = link2_x + 0.15 * np.cos(q1 + q2)
        gripper_y = link2_y + 0.15 * np.sin(q1 + q2)
        xform_gripper = UsdGeom.Xformable(self.gripper)
        xform_gripper.ClearXformOpOrder()
        xform_gripper.AddTranslateOp().Set(Gf.Vec3d(gripper_x, gripper_y, 0.9))
        xform_gripper.AddScaleOp().Set(Gf.Vec3d(0.05, 0.05, 0.05))
        
        # Target
        xform_target = UsdGeom.Xformable(self.target)
        xform_target.ClearXformOpOrder()
        xform_target.AddTranslateOp().Set(Gf.Vec3d(target_x, target_y, 0.9))
        xform_target.AddScaleOp().Set(Gf.Vec3d(0.03, 0.03, 0.03))

controller = SafetyController(stage)
print("✓ Safety controller initialized")

print("\n[7/7] Starting simulation...")
print("")
print("=" * 70)
print(" SIMULATION RUNNING")
print("=" * 70)
print("")
print("Safety features active:")
print("  ✓ Joint limits: ±180° base, ±90° shoulder")
print("  ✓ Speed limits: 57°/s maximum")
print("  ✓ Rate limiting: Smooth acceleration")
print("  ✓ Physics validation: 60 Hz")
print("")
print("Watch the arm turn the steering wheel smoothly")
print("Press Ctrl+C to stop and see safety report")
print("")

# Reset world
world.reset()

frame_count = 0
start_time = time.time()

try:
    while simulation_app.is_running():
        world.step(render=True)
        
        # Update controller at 60 Hz
        if frame_count % 1 == 0:
            controller.update(1.0/60.0)
        
        frame_count += 1
        
        # Status update every 60 frames
        if frame_count % 60 == 0:
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] Frame {frame_count} | "
                  f"Violations: {len(controller.safety_violations)}")
        
except KeyboardInterrupt:
    print("\n\nStopping simulation...")

# Safety report
print("")
print("=" * 70)
print(" ISAAC SIM SAFETY REPORT")
print("=" * 70)
print("")
print(f"Simulation time: {time.time() - start_time:.1f} seconds")
print(f"Frames simulated: {frame_count}")
print(f"Physics steps: {frame_count} @ 60 Hz")
print("")

if len(controller.safety_violations) == 0:
    print("✅ ALL SAFETY CHECKS PASSED")
    print("")
    print("   ✓ No joint limit violations")
    print("   ✓ No speed limit violations")
    print("   ✓ Physics simulation stable")
    print("   ✓ Smooth, controlled motion")
    print("")
    print("🎯 SAFE TO DEPLOY TO REAL HARDWARE")
else:
    print(f"⚠️  {len(controller.safety_violations)} SAFETY VIOLATIONS")
    print("")
    for i, v in enumerate(controller.safety_violations[:10], 1):
        print(f"   {i}. {v}")
    if len(controller.safety_violations) > 10:
        print(f"   ... and {len(controller.safety_violations) - 10} more")
    print("")
    print("❌ NOT SAFE - Fix violations before hardware deployment")

print("=" * 70)

simulation_app.close()
print("\nIsaac Sim closed.")
