#!/usr/bin/env python3
"""
WORKING G29 + PIPER ARM INTEGRATION
Builds scene from scratch to avoid broken USD references
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
from pxr import Gf, UsdPhysics, UsdGeom

# ============================================================================
# UDP LISTENER FOR G29 INPUT
# ============================================================================
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
g29_data = {"steer": 0.0}

def udp_listener():
    global g29_data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)
    print(f"[UDP] Listening on {UDP_IP}:{UDP_PORT}")
    
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            g29_data = json.loads(data.decode('utf-8'))
        except:
            pass

threading.Thread(target=udp_listener, daemon=True).start()

# ============================================================================
# CREATE WORLD
# ============================================================================
print("="*70)
print(" G29 + PIPER ARM - CLEAN INTEGRATION")
print("="*70)
print("\n[1/5] Creating world...")

world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

print("✓ World created")

# ============================================================================
# CREATE STEERING WHEEL (Simple Cylinder)
# ============================================================================
print("\n[2/5] Creating steering wheel...")

# Create a simple cylinder as steering wheel
wheel = DynamicCylinder(
    prim_path="/World/SteeringWheel",
    name="steering_wheel",
    radius=0.16,
    height=0.05,
    position=np.array([0.5, 0.0, 0.5]),
    color=np.array([0.2, 0.2, 0.2])
)
world.scene.add(wheel)

# Add revolute joint for rotation
stage = omni.usd.get_context().get_stage()
wheel_prim = stage.GetPrimAtPath("/World/SteeringWheel")

# Create joint
omni.kit.commands.execute(
    "AddPhysicsComponent",
    usd_prim=wheel_prim,
    component="PhysicsRevoluteJoint"
)

# Get the joint and configure it
joint_prim = stage.GetPrimAtPath("/World/SteeringWheel/RevoluteJoint")
if not joint_prim.IsValid():
    # Create it manually
    from pxr import Sdf
    joint_prim = stage.DefinePrim("/World/SteeringWheel/RevoluteJoint", "PhysicsRevoluteJoint")

revolute_joint = UsdPhysics.RevoluteJoint(joint_prim)
revolute_joint.CreateAxisAttr("Z")
revolute_joint.CreateLowerLimitAttr(-90)
revolute_joint.CreateUpperLimitAttr(90)

# Add drive
drive_api = UsdPhysics.DriveAPI.Apply(joint_prim, "angular")
drive_api.CreateTypeAttr("force")
drive_api.CreateDampingAttr(10.0)
drive_api.CreateStiffnessAttr(1000.0)

print("✓ Steering wheel created")

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
from omni.isaac.core.utils.xforms import get_world_pose

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

piper_arm = Articulation(prim_path=piper_path)
world.scene.add(piper_arm)

print(f"✓ Piper arm imported")

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

# Set initial arm pose
init_pos = np.zeros(piper_arm.num_dof)
if piper_arm.num_dof >= 3:
    init_pos[1] = 0.5
    init_pos[2] = -0.5
piper_arm.set_joint_positions(init_pos)

print("✓ Simulation ready")

# ============================================================================
# MAIN LOOP
# ============================================================================
print("\n" + "="*70)
print(" SIMULATION RUNNING")
print("="*70)
print("G29 Control: Physical G29 or Virtual Mode")
print("Piper Arm: Following steering wheel via IK")
print("Close window to exit")
print("="*70 + "\n")

frame = 0
last_print = time.time()

while simulation_app.is_running():
    world.step(render=True)
    
    # Get G29 steering input
    steer_input = g29_data["steer"]
    target_deg = steer_input * -90.0
    target_rad = np.radians(target_deg)
    
    # Drive the steering wheel
    if drive_api:
        drive_api.CreateTargetPositionAttr(target_deg)
    
    # Calculate IK target on wheel rim
    wheel_pos, wheel_rot = get_world_pose("/World/SteeringWheel")
    wheel_radius = 0.16
    
    # Target at top of rim (rotated by steering angle)
    local_target = np.array([0, wheel_radius * np.cos(target_rad), wheel_radius * np.sin(target_rad)])
    world_target = wheel_pos + local_target
    world_target[2] -= 0.05  # Safety offset
    
    # Solve IK
    action, success = ik_solver.compute_inverse_kinematics(target_position=world_target)
    
    if action:
        piper_arm.get_articulation_controller().apply_action(action)
    
    # Print status
    if time.time() - last_print > 2.0:
        status_msg = "✓ OK" if success else "⚠ SEARCHING"
        print(f"[{frame:06d}] Steer: {target_deg:+6.1f}° | IK: {status_msg}")
        last_print = time.time()
    
    frame += 1

print("\nSimulation closed.")
simulation_app.close()
