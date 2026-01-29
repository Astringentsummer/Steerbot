#!/usr/bin/env python3
"""
Isaac Sim Piper Arm + Custom Gripper Integration
Loads the Piper Arm URDF and attaches the custom gripper.
"""

import sys
import os
import numpy as np

# Add Isaac Sim Python packages to path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

# Set ROS_PACKAGE_PATH for URDF mesh resolution
package_src = r"c:\Users\rohit\Downloads\Steerbot-Gripper\piper_ros\src"
os.environ["ROS_PACKAGE_PATH"] = package_src
print(f"Setting ROS_PACKAGE_PATH: {package_src}")

# Create simulation app
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
    "max_fps": 60,
}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, VisualSphere, FixedCuboid, VisualCylinder
from omni.isaac.core.utils.extensions import enable_extension
from isaacsim.core.utils.prims import create_prim
from isaacsim.core.utils.viewports import set_camera_view
import omni.kit.commands

# Enable URDF extension
enable_extension("isaacsim.asset.importer.urdf")
from isaacsim.asset.importer.urdf import _urdf

# Create world
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

# Add Light
create_prim(
    prim_path="/World/DistantLight",
    prim_type="DistantLight",
    position=np.array([1.0, 1.0, 1.0]),
    attributes={"inputs:intensity": 2000.0}
)

# --- SETUP ENVIRONMENT (TABLES) ---
table_height = 0.6
table_thickness = 0.05

# Piper Table
world.scene.add(
    FixedCuboid(
        prim_path="/World/Layout/PiperTable",
        name="piper_table",
        position=np.array([0.0, 0.0, table_height/2]),
        scale=np.array([0.4, 0.4, table_height]),
        color=np.array([0.4, 0.4, 0.45])
    )
)

# G29 Table (positioned at reach)
wheel_distance = 0.55
world.scene.add(
    FixedCuboid(
        prim_path="/World/Layout/WheelTable",
        name="wheel_table",
        position=np.array([wheel_distance, 0.0, table_height/2]),
        scale=np.array([0.4, 0.4, table_height]),
        color=np.array([0.4, 0.4, 0.45])
    )
)

# --- IMPORT PIPER ARM ---
print("Importing Piper Arm URDF...")
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.fix_base = True
import_config.make_default_prim = True

# URDF Path
package_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description"
urdf_file = os.path.join(package_path, "urdf", "piper_description.urdf")

status, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=urdf_file,
    import_config=import_config,
)

if not status:
    print("FAILED to import Piper Arm URDF!")
    simulation_app.close()
    sys.exit(1)

# Position Arm on Table
from isaacsim.core.prims import XFormPrim
arm_prim = XFormPrim(prim_path)
arm_prim.set_world_poses(positions=np.array([[0, 0, table_height]]))

# --- ATTACH CUSTOM GRIPPER ---
from omni.isaac.core.articulations import Articulation
piper_arm = Articulation(prim_path="/piper")
world.scene.add(piper_arm)

# Custom Gripper Base
gripper_base = world.scene.add(
    DynamicCuboid(
        prim_path="/World/CustomGripper/Base",
        name="gripper_base",
        position=np.array([0.0, 0.0, 1.0]), # Initial pos (will be snapped)
        scale=np.array([0.15, 0.1, 0.05]),
        color=np.array([0.3, 0.3, 0.35]),
        mass=0.1
    )
)

left_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/CustomGripper/LeftFinger",
        name="left_finger",
        position=np.array([-0.05, 0.0, 0.9]),
        scale=np.array([0.02, 0.03, 0.15]),
        color=np.array([0.1, 0.1, 0.1]),
    )
)

right_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/CustomGripper/RightFinger",
        name="right_finger",
        position=np.array([0.05, 0.0, 0.9]),
        scale=np.array([0.02, 0.03, 0.15]),
        color=np.array([0.1, 0.1, 0.1]),
    )
)

# --- PHYSICAL JOINT (FIXED) ---
# Create a fixed joint between arm wrist (Link6) and gripper base
from omni.physx.scripts import utils as physx_utils
from isaacsim.core.utils.xforms import get_world_pose
from isaacsim.core.utils.stage import get_current_stage

# Get wrist pose for initial alignment
ee_pos, ee_ori = get_world_pose("/piper/link6")
# In Isaac Sim 4.5.0, DynamicCuboid (from omni.isaac.core.objects) still uses singular set_world_pose
gripper_base.set_world_pose(position=ee_pos, orientation=ee_ori)

# Create physical link
stage = get_current_stage()
# Attachment to wrist
physx_utils.createJoint(
    stage, 
    "Fixed", 
    stage.GetPrimAtPath("/piper/link6"), 
    stage.GetPrimAtPath("/World/CustomGripper/Base")
)
# Attachment for Fingers
physx_utils.createJoint(
    stage,
    "Fixed",
    stage.GetPrimAtPath("/World/CustomGripper/Base"),
    stage.GetPrimAtPath("/World/CustomGripper/LeftFinger")
)
physx_utils.createJoint(
    stage,
    "Fixed",
    stage.GetPrimAtPath("/World/CustomGripper/Base"),
    stage.GetPrimAtPath("/World/CustomGripper/RightFinger")
)

# --- STEERING WHEEL ---
wheel_tilt_deg = 20
from scipy.spatial.transform import Rotation as R
# Rotation around Y axis for tilt
r = R.from_euler('y', wheel_tilt_deg, degrees=True)
q = r.as_quat() # [x, y, z, w]
# Isaac Sim uses [w, x, y, z]
q_isaac = np.array([q[3], q[0], q[1], q[2]])

wheel_rim = world.scene.add(
    VisualCylinder(
        prim_path="/World/SteeringWheel/Rim",
        name="wheel_rim",
        position=np.array([wheel_distance, 0.0, table_height + 0.15]),
        orientation=q_isaac,
        radius=0.15,
        height=0.04,
        color=np.array([0.1, 0.1, 0.1]),
    )
)

# Set camera
set_camera_view(eye=[1.5, 1.2, 1.2], target=[0.3, 0.0, 0.6])

# Init world
world.reset()

print("Ready! Starting simulation...")

frame = 0
while simulation_app.is_running():
    world.step(render=True)
    frame += 1
    
    # Move the arm slightly (sinusoidal demo)
    if frame > 60:
        try:
            controller = piper_arm.get_articulation_controller()
            if controller:
                from omni.isaac.core.utils.types import ArticulationAction
                targets = np.zeros(piper_arm.num_dof)
                # target base and wrist to point at wheel
                targets[0] = np.sin(frame * 0.03) * 0.4 
                targets[1] = 0.2
                targets[2] = 0.5
                controller.apply_action(ArticulationAction(joint_positions=targets))
        except Exception as e:
            if frame % 100 == 0: print(f"Control error: {e}")

    if frame % 200 == 0:
        print(f"Simulation frame: {frame}")

simulation_app.close()
