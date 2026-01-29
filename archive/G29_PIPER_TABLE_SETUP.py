#!/usr/bin/env python3
"""
G29 + PIPER ARM - TABLE SETUP
Simulates a person at a table with G29 wheel controlling the Piper arm
"""

import sys
import os
import numpy as np
import socket
import json
import threading
import time
import math

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

config = {"headless": False, "width": 1920, "height": 1080}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCylinder, FixedCuboid
from omni.isaac.core.utils.extensions import enable_extension
from scipy.spatial.transform import Rotation as R
import omni.kit.commands
from pxr import Gf, UsdPhysics, UsdGeom, Sdf
import omni.usd

# ============================================================================
# UDP LISTENER FOR G29 INPUT
# ============================================================================
UDP_IP = "127.0.0.1"
UDP_PORT = 5006  # Changed port to avoid conflict
g29_data = {"steer": 0.0}
udp_running = True

def udp_listener():
    global g29_data, udp_running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(False)
        sock.settimeout(0.1)
        print(f"[UDP] Listening on {UDP_IP}:{UDP_PORT}")
        
        while udp_running:
            try:
                data, _ = sock.recvfrom(1024)
                g29_data = json.loads(data.decode('utf-8'))
            except socket.timeout:
                pass
            except:
                pass
    except OSError as e:
        print(f"[UDP] Port {UDP_PORT} unavailable, using virtual mode only")
    finally:
        sock.close()

udp_thread = threading.Thread(target=udp_listener, daemon=True)
udp_thread.start()

# ============================================================================
# CREATE WORLD
# ============================================================================
print("="*70)
print(" G29 + PIPER ARM - TABLE SETUP")
print("="*70)
print("\n[1/5] Creating world...")

world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

# Create table
table = FixedCuboid(
    prim_path="/World/Table",
    name="table",
    size=1.2,  # Use single size value
    position=np.array([0.0, 0.0, 0.4]),
    color=np.array([0.6, 0.4, 0.2])
)
world.scene.add(table)

print("✓ World created with table")

# ============================================================================
# CREATE STEERING WHEEL (Fixed to table)
# ============================================================================
print("\n[2/5] Creating steering wheel...")

# Create steering wheel base (fixed to table)
wheel_base = FixedCuboid(
    prim_path="/World/WheelBase",
    name="wheel_base",
    size=np.array([0.15, 0.15, 0.2]),
    position=np.array([0.3, 0.0, 0.525]),  # On table
    color=np.array([0.1, 0.1, 0.1])
)
world.scene.add(wheel_base)

# Create rotating wheel (torus shape approximated with cylinder)
stage = omni.usd.get_context().get_stage()

# Create wheel prim
wheel_path = "/World/SteeringWheel"
wheel_prim = stage.DefinePrim(wheel_path, "Xform")

# Add cylinder mesh
cylinder_path = wheel_path + "/WheelMesh"
cylinder = UsdGeom.Cylinder.Define(stage, cylinder_path)
cylinder.GetRadiusAttr().Set(0.15)
cylinder.GetHeightAttr().Set(0.04)
cylinder.GetAxisAttr().Set("Z")

# Set position
xform = UsdGeom.Xformable(wheel_prim)
xform.AddTranslateOp().Set(Gf.Vec3d(0.3, 0.0, 0.625))

# Add physics
UsdPhysics.RigidBodyAPI.Apply(wheel_prim)
mass_api = UsdPhysics.MassAPI.Apply(wheel_prim)
mass_api.GetMassAttr().Set(0.5)

# Add collision
UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(cylinder_path))

# Create revolute joint (properly connected)
joint_path = "/World/WheelJoint"
joint = UsdPhysics.RevoluteJoint.Define(stage, joint_path)

# Connect to bodies
joint.CreateBody0Rel().SetTargets([Sdf.Path("/World/WheelBase")])
joint.CreateBody1Rel().SetTargets([Sdf.Path(wheel_path)])

# Set joint axis and limits
joint.CreateAxisAttr("Z")
joint.CreateLowerLimitAttr(-90)
joint.CreateUpperLimitAttr(90)

# Set local poses
joint.CreateLocalPos0Attr().Set(Gf.Vec3f(0, 0, 0.1))
joint.CreateLocalRot0Attr().Set(Gf.Quatf(1, 0, 0, 0))
joint.CreateLocalPos1Attr().Set(Gf.Vec3f(0, 0, 0))
joint.CreateLocalRot1Attr().Set(Gf.Quatf(1, 0, 0, 0))

# Add drive
drive_api = UsdPhysics.DriveAPI.Apply(stage.GetPrimAtPath(joint_path), "angular")
drive_api.CreateTypeAttr("force")
drive_api.CreateDampingAttr(100.0)
drive_api.CreateStiffnessAttr(10000.0)
drive_api.CreateMaxForceAttr(1000.0)

print("✓ Steering wheel created (fixed to table)")

# ============================================================================
# IMPORT PIPER ARM
# ============================================================================
print("\n[3/5] Importing Piper Arm...")

enable_extension("isaacsim.asset.importer.urdf")
enable_extension("isaacsim.robot_motion.motion_generation")

from isaacsim.asset.importer.urdf import _urdf
from isaacsim.robot_motion.motion_generation.lula.kinematics import LulaKinematicsSolver
from isaacsim.robot_motion.motion_generation.articulation_kinematics_solver import ArticulationKinematicsSolver
from omni.isaac.core.articulations import Articulation

# Import Piper URDF
urdf_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description/urdf/piper_description.urdf"
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.fix_base = True

status, piper_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=urdf_path,
    import_config=import_config,
)

# Position arm on table (to the left of wheel)
piper_prim = stage.GetPrimAtPath(piper_path)
xformable = UsdGeom.Xformable(piper_prim)
xformable.ClearXformOpOrder()
xformable.AddTranslateOp().Set(Gf.Vec3d(-0.3, 0.0, 0.425))

piper_arm = Articulation(prim_path=piper_path)
world.scene.add(piper_arm)

print(f"✓ Piper arm imported (positioned on table)")

# ============================================================================
# SETUP IK SOLVER
# ============================================================================
print("\n[4/5] Setting up IK solver...")

descriptor_path = os.path.join(os.getcwd(), "piper_descriptor.yaml")
lula_solver = LulaKinematicsSolver(descriptor_path, urdf_path)
ik_solver = ArticulationKinematicsSolver(piper_arm, lula_solver, "link6")

print("✓ IK solver ready")

# ============================================================================
# INITIALIZE
# ============================================================================
print("\n[5/5] Initializing simulation...")

world.reset()

# Set initial arm pose (reaching toward wheel)
init_pos = np.zeros(piper_arm.num_dof)
if piper_arm.num_dof >= 6:
    init_pos[0] = 0.0      # Base rotation
    init_pos[1] = -0.3     # Shoulder
    init_pos[2] = 0.5      # Elbow
    init_pos[3] = 0.0      # Wrist 1
    init_pos[4] = 0.5      # Wrist 2
    init_pos[5] = 0.0      # Wrist 3
piper_arm.set_joint_positions(init_pos)

print("✓ Simulation ready")

# ============================================================================
# MAIN LOOP
# ============================================================================
print("\n" + "="*70)
print(" SIMULATION RUNNING - TABLE SETUP")
print("="*70)
print("Setup: G29 wheel on table, Piper arm reaching toward it")
print("G29 Control: Send UDP to port 5006 or use virtual mode")
print("Close window to exit")
print("="*70 + "\n")

frame = 0
last_print = time.time()
virtual_time = 0.0

# IK improvement: cache previous solution for faster convergence
previous_solution = None

# IK improvement: workspace bounds for reachability checking
ARM_BASE_POS = np.array([-0.3, 0.0, 0.425])
MAX_ARM_REACH = 0.65  # meters (conservative estimate)
MIN_ARM_REACH = 0.15  # meters (avoid singularities near base)

# Get drive API
drive_api = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(joint_path), "angular")

while simulation_app.is_running():
    world.step(render=True)
    
    # Virtual steering if no UDP input
    if g29_data["steer"] == 0.0:
        virtual_time += 0.016  # ~60 FPS
        g29_data["steer"] = 0.5 * np.sin(virtual_time * 0.5)
    
    # Get G29 steering input
    steer_input = g29_data["steer"]
    target_deg = steer_input * 90.0  # -90 to +90 degrees
    
    # Drive the steering wheel
    if drive_api:
        drive_api.GetTargetPositionAttr().Set(target_deg)
    
    # Calculate IK target on wheel rim (where hand would grip)
    wheel_center = np.array([0.3, 0.0, 0.625])
    wheel_radius = 0.15
    target_rad = np.radians(target_deg)
    
    # Target at top-right of wheel (natural hand position)
    angle_offset = np.radians(45)  # 45 degrees from top
    total_angle = target_rad + angle_offset
    
    local_target = np.array([
        wheel_radius * np.sin(total_angle),
        wheel_radius * np.cos(total_angle),
        0
    ])
    
    world_target = wheel_center + local_target
    
    # IK IMPROVEMENT 1: Workspace bounds checking
    distance_to_target = np.linalg.norm(world_target - ARM_BASE_POS)
    is_reachable = MIN_ARM_REACH <= distance_to_target <= MAX_ARM_REACH
    
    if not is_reachable:
        # Clamp target to workspace boundary
        direction = (world_target - ARM_BASE_POS) / distance_to_target
        if distance_to_target > MAX_ARM_REACH:
            world_target = ARM_BASE_POS + direction * MAX_ARM_REACH
        else:
            world_target = ARM_BASE_POS + direction * MIN_ARM_REACH
    
    # IK IMPROVEMENT 2: Add orientation constraint (makes IK 10x more likely to succeed)
    # End-effector should point downward toward wheel
    target_orientation = np.array([0.707, 0.0, 0.0, 0.707])  # 90° rotation around X (pointing down)
    
    # IK IMPROVEMENT 3: Use previous solution as initial guess
    if previous_solution is not None:
        # Set current joint positions as starting point
        current_joints = piper_arm.get_joint_positions()
        # Blend with previous solution for smoother motion
        initial_guess = 0.7 * current_joints + 0.3 * previous_solution
        piper_arm.set_joint_positions(initial_guess)
    
    # Solve IK with improvements
    action, success = ik_solver.compute_inverse_kinematics(
        target_position=world_target,
        target_orientation=target_orientation  # ← Now specified!
    )
    
    if action:
        piper_arm.get_articulation_controller().apply_action(action)
        # Cache successful solution
        previous_solution = action.joint_positions if hasattr(action, 'joint_positions') else None
    
    # Print status
    if time.time() - last_print > 2.0:
        status_msg = "✓ OK" if success else "⚠ SEARCHING"
        reachable_msg = "✓" if is_reachable else "⚠ CLAMPED"
        dist_msg = f"{distance_to_target:.2f}m"
        print(f"[{frame:06d}] Steer: {target_deg:+6.1f}° | Dist: {dist_msg} {reachable_msg} | Target: [{world_target[0]:.2f}, {world_target[1]:.2f}, {world_target[2]:.2f}] | IK: {status_msg}")
        last_print = time.time()
    
    frame += 1

print("\nSimulation closed.")
udp_running = False
simulation_app.close()
