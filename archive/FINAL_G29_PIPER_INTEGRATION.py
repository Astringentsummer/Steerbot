#!/usr/bin/env python3
"""
COMPLETE G29 + PIPER ARM INTEGRATION
- Loads Steerbot G29 USD scene
- Reads G29 hardware input via UDP
- Controls virtual steering wheel
- Moves Piper arm to follow wheel rotation using IK
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

import omni.usd
from pxr import UsdPhysics, UsdGeom, Sdf
from scipy.spatial.transform import Rotation as R

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
# LOAD G29 USD SCENE
# ============================================================================
stage = omni.usd.get_context().get_stage()
usd_path = r"C:\Users\rohit\Downloads\Steerbot-main\Steerbot-main\isaac\scenes\1stage.usd"

print("="*70)
print(" G29 + PIPER ARM - COMPLETE INTEGRATION")
print("="*70)
print(f"\n[1/4] Loading complete scene: {os.path.basename(usd_path)}")
print("       (This file contains all assets - may take a moment)")
omni.usd.get_context().open_stage(usd_path)
time.sleep(5)  # Longer wait for larger file
print("✓ Scene loaded")

# Get the revolute joint for the steering wheel
joint = UsdPhysics.RevoluteJoint.Get(stage, "/G29_root/RevoluteJoint")
drive = UsdPhysics.DriveAPI(joint.GetPrim(), "angular")

if not drive:
    print("⚠️  Warning: Could not find steering wheel drive")
else:
    print("✓ Steering wheel joint found")

# ============================================================================
# IMPORT PIPER ARM
# ============================================================================
print("\n[2/4] Importing Piper Arm...")

from omni.isaac.core import World
from omni.isaac.core.utils.extensions import enable_extension

enable_extension("isaacsim.asset.importer.urdf")
enable_extension("isaacsim.robot_motion.motion_generation")

from isaacsim.asset.importer.urdf import _urdf
from isaacsim.robot_motion.motion_generation.lula.kinematics import LulaKinematicsSolver
from isaacsim.robot_motion.motion_generation.articulation_kinematics_solver import ArticulationKinematicsSolver
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.xforms import get_world_pose
import omni.kit.commands

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

print(f"✓ Piper arm imported at: {piper_path}")

# Create World and add Piper
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
piper_arm = Articulation(prim_path=piper_path)
world.scene.add(piper_arm)

# ============================================================================
# SETUP IK SOLVER
# ============================================================================
print("\n[3/4] Setting up IK solver...")

descriptor_path = os.path.join(os.getcwd(), "piper_descriptor.yaml")
lula_solver = LulaKinematicsSolver(descriptor_path, urdf_path)
ik_solver = ArticulationKinematicsSolver(piper_arm, lula_solver, "link6")

print("✓ IK solver ready")

# ============================================================================
# INITIALIZE SIMULATION
# ============================================================================
print("\n[4/4] Initializing simulation...")

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
print("G29 Control: Physical G29 or Virtual Mode (g29_bridge.py)")
print("Piper Arm: Following steering wheel via IK")
print("Close window to exit")
print("="*70 + "\n")

frame = 0
last_print = time.time()

while simulation_app.is_running():
    simulation_app.update()
    world.step(render=True)
    
    # Get G29 steering input (-1.0 to 1.0)
    steer_input = g29_data["steer"]
    
    # Convert to degrees for the wheel joint (-90° to +90°)
    target_deg = steer_input * -90.0
    
    # Drive the virtual steering wheel
    if drive:
        drive.CreateTargetPositionAttr(target_deg)
    
    # Calculate IK target on steering wheel rim
    # Wheel is at approximately [0.5, 0, 0.3] with 27° tilt
    wheel_center = np.array([0.5, 0.0, 0.3])
    wheel_radius = 0.16
    
    # Apply 27° tilt
    tilt_rad = np.radians(27)
    wheel_rot = R.from_euler('y', tilt_rad)
    
    # Rotate by steering angle
    steer_rad = np.radians(target_deg)
    steer_rot = R.from_euler('z', steer_rad)
    
    # Combined rotation
    combined_rot = wheel_rot * steer_rot
    
    # Target at top of rim (local [0, radius, 0])
    local_target = np.array([0, wheel_radius, 0])
    world_target = wheel_center + combined_rot.apply(local_target)
    
    # Add safety offset
    world_target += np.array([0, 0, -0.05])
    
    # Solve IK
    action, success = ik_solver.compute_inverse_kinematics(target_position=world_target)
    
    if action:
        piper_arm.get_articulation_controller().apply_action(action)
    
    # Print status every 2 seconds
    if time.time() - last_print > 2.0:
        status_msg = "✓ OK" if success else "⚠ SEARCHING"
        print(f"[{frame:06d}] Steer: {target_deg:+6.1f}° | IK: {status_msg}")
        last_print = time.time()
    
    frame += 1

print("\nSimulation closed.")
simulation_app.close()
