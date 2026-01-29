#!/usr/bin/env python3
"""
Isaac Sim Piper Arm + G29 Steering Integration
FINAL WORKING VERSION - Uses proven import paths
"""

import sys
import os
import numpy as np
import socket
import json
import threading

# Add Isaac Sim Python packages to path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

# Create simulation app
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, FixedCuboid, DynamicCylinder
from omni.isaac.core.utils.extensions import enable_extension
from isaacsim.core.utils.prims import create_prim
from isaacsim.core.utils.viewports import set_camera_view
from omni.isaac.core.utils.stage import get_current_stage
from omni.isaac.core.utils.xforms import get_world_pose
import omni.physx.scripts.utils as physx_utils
from scipy.spatial.transform import Rotation as R
import omni.kit.commands

# Enable extensions
enable_extension("isaacsim.asset.importer.urdf")
enable_extension("isaacsim.robot_motion.motion_generation")

from isaacsim.asset.importer.urdf import _urdf
from isaacsim.robot_motion.motion_generation.lula.kinematics import LulaKinematicsSolver
from isaacsim.robot_motion.motion_generation.articulation_kinematics_solver import ArticulationKinematicsSolver

def log_info(msg):
    print(f"[INFO] {msg}")

# UDP Listener for G29
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
current_g29_data = {"steer": 0.0, "buttons": []}

def udp_listener():
    global current_g29_data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)
    log_info(f"UDP Listener started on {UDP_IP}:{UDP_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            current_g29_data = json.loads(data.decode('utf-8'))
        except BlockingIOError:
            pass
        except Exception as e:
            pass

listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Create World
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

# Lighting
create_prim("/World/Light", "DistantLight", attributes={"inputs:intensity": 5000.0})

# Import Piper Arm
log_info("Importing Piper Arm URDF...")
urdf_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description/urdf/piper_description.urdf"

import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.fix_base = True

status, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=urdf_path,
    import_config=import_config,
)

log_info(f"Piper Arm imported at: {prim_path}")

# Add to scene
from omni.isaac.core.articulations import Articulation
piper_arm = Articulation(prim_path=prim_path)
world.scene.add(piper_arm)

# Wrist path
wrist_path = f"{prim_path}/link6"
log_info(f"Using Wrist Path: {wrist_path}")

# Attach Custom Gripper
log_info("Attaching Custom Gripper...")
gripper_base = world.scene.add(DynamicCuboid(
    "/World/CustomGripper/Base",
    name="gripper_base",
    position=np.array([0, 0, 0.5]),
    scale=np.array([0.15, 0.1, 0.05]),
    color=np.array([0.3, 0.3, 0.35]),
    mass=0.1
))

# Align to wrist
ee_pos, ee_ori = get_world_pose(wrist_path)
gripper_base.set_world_pose(position=ee_pos, orientation=ee_ori)

stage = get_current_stage()
physx_utils.createJoint(stage, "Fixed", stage.GetPrimAtPath(wrist_path), stage.GetPrimAtPath("/World/CustomGripper/Base"))

# G29 Steering Wheel
wheel_distance = 0.4
wheel_tilt_deg = 45
r_tilt = R.from_euler('y', wheel_tilt_deg, degrees=True)
q_tilt = r_tilt.as_quat()
q_isaac = np.array([q_tilt[3], q_tilt[0], q_tilt[1], q_tilt[2]])

wheel_pos = np.array([wheel_distance, 0.0, 0.2])

hub = world.scene.add(FixedCuboid(
    "/World/SteeringWheel/Hub",
    position=wheel_pos,
    orientation=q_isaac,
    scale=np.array([0.05, 0.05, 0.05]),
    color=np.array([0.2, 0.2, 0.2])
))

rim = world.scene.add(DynamicCylinder(
    "/World/SteeringWheel/Rim",
    position=wheel_pos,
    orientation=q_isaac,
    radius=0.16,
    height=0.04,
    color=np.array([0.1, 0.1, 0.1]),
    mass=0.5
))

# Create Revolute Joint
hub_path = "/World/SteeringWheel/Hub"
wheel_rim_path = "/World/SteeringWheel/Rim"
physx_utils.createJoint(stage, "Revolute", stage.GetPrimAtPath(hub_path), stage.GetPrimAtPath(wheel_rim_path))
wheel_joint_prim = stage.GetPrimAtPath(f"{hub_path}/RevoluteJoint")

if wheel_joint_prim.IsValid():
    from pxr import UsdPhysics
    joint_attr = wheel_joint_prim.GetAttribute("physics:axis")
    joint_attr.Set("Z")
    
    # Add Position Drive
    drive = UsdPhysics.DriveAPI.Apply(wheel_joint_prim, "angular")
    drive.CreateTypeAttr("position")
    drive.CreateStiffnessAttr(500.0)
    drive.CreateDampingAttr(50.0)
    log_info("Wheel Joint Drive initialized.")

# Setup IK
log_info("Setting up Lula IK Solver...")
descriptor_path = os.path.join(os.getcwd(), "piper_descriptor.yaml")
lula_solver = LulaKinematicsSolver(descriptor_path, urdf_path)
ik_solver = ArticulationKinematicsSolver(piper_arm, lula_solver, "link6")

# Camera
set_camera_view(eye=[1.0, 1.0, 1.2], target=wheel_pos)

# Reset
world.reset()

# Initial pose
init_pos = np.zeros(piper_arm.num_dof)
if piper_arm.num_dof >= 3:
    init_pos[1] = 0.5
    init_pos[2] = -0.5
piper_arm.set_joint_positions(init_pos)

log_info("Starting simulation loop...")
frame = 0

while simulation_app.is_running():
    world.step(render=True)
    
    # Get steering input
    steer_input = current_g29_data["steer"]
    target_angle_rad = steer_input * (np.pi / 2) * -1
    
    # Drive wheel joint
    wheel_joint_prim.GetAttribute("physics:angular:targetPosition").Set(np.degrees(target_angle_rad))
    
    # Calculate IK target
    rim_pos, rim_ori = get_world_pose("/World/SteeringWheel/Rim")
    rim_rot = R.from_quat([rim_ori[1], rim_ori[2], rim_ori[3], rim_ori[0]])
    
    # Target at top of rim
    local_target = np.array([0, 0.16, 0])
    offset = np.array([0, 0, -0.05])
    world_target_pos = rim_pos + rim_rot.apply(local_target + offset)
    
    # Solve IK
    action, success = ik_solver.compute_inverse_kinematics(target_position=world_target_pos)
    
    if action:
        piper_arm.get_articulation_controller().apply_action(action)
        
        # Update gripper visual
        w_pos, w_ori = get_world_pose(wrist_path)
        gripper_base.set_world_pose(w_pos, w_ori)
    
    if frame % 60 == 0:
        status_msg = "OK" if success else "SEARCHING"
        log_info(f"Angle: {np.degrees(target_angle_rad):.1f} deg | IK: {status_msg}")
    
    frame += 1

simulation_app.close()
