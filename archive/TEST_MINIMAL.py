#!/usr/bin/env python3
"""
MINIMAL TEST - Just load Isaac Sim and create a simple scene
This will help identify what's causing the crash
"""

import sys
import os

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

config = {"headless": False, "width": 1920, "height": 1080}
simulation_app = SimulationApp(config)

print("="*70)
print(" MINIMAL TEST - Isaac Sim Loaded Successfully")
print("="*70)

from omni.isaac.core import World
from omni.isaac.core.objects import FixedCuboid
import numpy as np

print("\n[1/2] Creating world...")
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

# Create a simple cube
cube = FixedCuboid(
    prim_path="/World/TestCube",
    name="test_cube",
    size=np.array([0.2, 0.2, 0.2]),
    position=np.array([0.0, 0.0, 0.5]),
    color=np.array([1.0, 0.0, 0.0])
)
world.scene.add(cube)

print("✓ World created with test cube")

print("\n[2/2] Initializing simulation...")
world.reset()
print("✓ Simulation ready")

print("\n" + "="*70)
print(" SUCCESS! Simulation is running.")
print(" You should see a red cube floating above the ground.")
print(" Close the window to exit.")
print("="*70 + "\n")

frame = 0
while simulation_app.is_running():
    world.step(render=True)
    
    if frame % 300 == 0:  # Every 5 seconds
        print(f"[{frame:06d}] Simulation running...")
    
    frame += 1

print("\nSimulation closed.")
simulation_app.close()
