#!/usr/bin/env python3
import sys
import os

ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.extensions import enable_extension
import omni.kit.commands

enable_extension("isaacsim.asset.importer.urdf")
from isaacsim.asset.importer.urdf import _urdf

world = World()

print("Attempting to import Piper Arm...")
import_config = _urdf.ImportConfig()
import_config.fix_base = True

package_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description"
import_config.package_paths = [package_path]
urdf_file = os.path.join(package_path, "urdf", "piper_description.urdf")

print(f"URDF Path: {urdf_file}")

status, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=urdf_file,
    import_config=import_config,
)

if status:
    print(f"SUCCESS: Imported to {prim_path}")
else:
    print("FAILED to import.")

for i in range(100):
    world.step(render=True)

simulation_app.close()
