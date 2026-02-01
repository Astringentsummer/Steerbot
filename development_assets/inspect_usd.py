import os
import sys

# Standard Isaac Sim metadata
ISAAC_PATH = "/mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64"
sys.path.insert(0, os.path.join(ISAAC_PATH, "python_packages"))

from isaacsim import SimulationApp
sim = SimulationApp({"headless": True})

from pxr import Usd, UsdGeom
import omni.usd

G29_PATH = "/root/projects/Steerbot-Gripper/Steerbot/isaac/scenes/g29.usd"
print(f"[LOAD] - Inspecting: {G29_PATH}")

omni.usd.get_context().open_stage(G29_PATH)
stage = omni.usd.get_context().get_stage()

for prim in stage.Traverse():
    if prim.IsA(UsdGeom.Xform):
        print(f"Xform: {prim.GetPath()}")
    if prim.GetTypeName() == "PhysicsRevoluteJoint":
        print(f"JOINT FOUND: {prim.GetPath()}")

sim.close()
