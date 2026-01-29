import sys
import os
import omni.usd

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": True})

usd_path = r"C:\Users\rohit\Downloads\Steerbot-main\Steerbot-main\isaac\scenes\Flattendpiper_Roehl.usd"
print(f"Inspecting: {usd_path}")

omni.usd.get_context().open_stage(usd_path)
stage = omni.usd.get_context().get_stage()

for prim in stage.Traverse():
    print(f"Prim: {prim.GetPath()} [{prim.GetTypeName()}]")

simulation_app.close()
