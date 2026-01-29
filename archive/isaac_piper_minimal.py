import os
import sys
import numpy as np

# Set Isaac Sim standalone path
isaac_path = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.append(os.path.join(isaac_path, "exts", "isaacsim.simulation_app"))

from isaacsim.simulation_app import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.extensions import enable_extension
from isaacsim.core.utils.types import ArticulationAction
import omni.kit.commands
from isaacsim.core.prims import XFormPrim

def log_info(msg):
    print(msg, flush=True)

# Enable extensions
enable_extension("isaacsim.asset.importer.urdf")
from isaacsim.asset.importer.urdf import _urdf

# Create world
world = World()
world.scene.add_default_ground_plane()

# --- IMPORT PIPER ARM ---
log_info("Starting Minimal URDF Import Test...")
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.fix_base = True
import_config.make_default_prim = True

package_path = r"C:\Users\rohit\Downloads\Steerbot-Gripper\piper_ros\src\piper_description"
urdf_file_raw = os.path.join(package_path, "urdf", "piper_description.urdf")

# Use the absolute path logic that looked good in the file
with open(urdf_file_raw, 'r') as f:
    urdf_content = f.read()

# Flat Mesh Strategy: Copy meshes to URDF folder and use simple filenames
import shutil
mesh_src = os.path.join(package_path, "meshes")
urdf_dest = os.path.join(package_path, "urdf")
for f in os.listdir(mesh_src):
    if f.endswith(".STL") or f.endswith(".stl"):
        shutil.copy2(os.path.join(mesh_src, f), os.path.join(urdf_dest, f))

# Replace package path with nothing, just filename remains
urdf_content = urdf_content.replace("package://piper_description/meshes/", "")

temp_urdf = os.path.join(package_path, "urdf", "test_minimal.urdf")
with open(temp_urdf, 'w') as f:
    f.write(urdf_content)

log_info(f"Importing: {temp_urdf}")
status, prim_path = omni.kit.commands.execute("URDFParseAndImportFile", urdf_path=temp_urdf, import_config=import_config)
log_info(f"Import Status: {status}, Path: {prim_path}")

if status:
    from omni.isaac.core.articulations import Articulation
    piper = Articulation(prim_path=prim_path)
    world.scene.add(piper)
    world.reset()
    dof_count = piper.num_dof
    log_info(f"Simulation Started. Joints: {dof_count}. Moving Joint 1...")
    
    frame = 0
    while simulation_app.is_running():
        world.step(render=True)
        frame += 1
        
        # Simple sinusoidal move for joint 1
        val = np.sin(frame * 0.05) * 1.0
        actions = np.zeros(dof_count)
        if dof_count > 0:
            actions[0] = val
            
        piper.get_articulation_controller().apply_action(
            ArticulationAction(joint_positions=actions)
        )
        
        if frame % 60 == 0:
            log_info(f"Frame {frame} | Joint1: {val:.2f}")

simulation_app.close()
