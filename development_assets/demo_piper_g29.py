#!/usr/bin/env python3
"""
Piper + G29 Demo with Proper Camera Setup
Shows both models clearly in Isaac Sim viewport
"""
import sys
import os

ISAAC_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_PATH, "exts", "omni.isaac.kit", "omni", "isaac", "kit"))

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False, "width": 1920, "height": 1080})

import numpy as np
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.utils.viewports import set_camera_view
from pxr import Gf, UsdGeom
import omni.usd

print("="*80)
print("PIPER ARM + G29 STEERING WHEEL DEMO")
print("="*80)

# Create world
world = World(stage_units_in_meters=1.0)
stage = omni.usd.get_context().get_stage()

# Add ground
world.scene.add_default_ground_plane()

# Add lighting
distant_light = UsdGeom.DistantLight.Define(stage, "/World/DistantLight")
distant_light.CreateIntensityAttr(1000)

# Load Piper arm USD
piper_usd = r"C:\Users\rohit\Downloads\Steerbot-Gripper\Steerbot-Gripper\dev\piper_isaac_sim\usd\piper_description.usd"
if os.path.exists(piper_usd):
    print(f"\n✓ Loading Piper arm from: {piper_usd}")
    add_reference_to_stage(piper_usd, "/World/Piper")
    
    # Position Piper on the right
    piper_prim = stage.GetPrimAtPath("/World/Piper")
    UsdGeom.XformCommonAPI(piper_prim).SetTranslate(Gf.Vec3d(0.4, 0.0, 0.0))
    
    piper = world.scene.add(Articulation("/World/Piper", name="piper"))
    print(f"✓ Piper arm loaded! DOF: {piper.num_dof}")
else:
    print(f"✗ Piper USD not found: {piper_usd}")
    piper = None

# Load G29 wheel USD
g29_usd = r"C:\Users\rohit\Downloads\Steerbot-Gripper\Steerbot-Gripper\isaac\scenes\g29.usd"
if os.path.exists(g29_usd):
    print(f"✓ Loading G29 wheel from: {g29_usd}")
    add_reference_to_stage(g29_usd, "/World/G29")
    
    # Position G29 on the left
    g29_prim = stage.GetPrimAtPath("/World/G29")
    UsdGeom.XformCommonAPI(g29_prim).SetTranslate(Gf.Vec3d(-0.6, 0.0, 0.5))
    
    print("✓ G29 wheel loaded!")
else:
    print(f"✗ G29 USD not found: {g29_usd}")

# Reset world
world.reset()

# Set camera to view the scene
print("\n✓ Setting camera view...")
set_camera_view(
    eye=np.array([2.0, 2.0, 1.5]),      # Camera position (back and to the side)
    target=np.array([0.0, 0.0, 0.5]),   # Look at center
    camera_prim_path="/OmniverseKit_Persp"
)

print("\n" + "="*80)
print("SCENE READY!")
print("="*80)

if piper:
    # Set to grasp pose
    grasp_joints = [0.8, -1.2, 1.5, 0.0, 1.3, 0.0, 0.02, -0.02]
    piper.set_joint_positions(grasp_joints[:piper.num_dof])
    print(f"\n✓ Piper set to grasp pose")
    print(f"  Joint positions: {np.round(grasp_joints[:piper.num_dof], 3)}")

print("\n" + "="*80)
print("SIMULATION RUNNING")
print("You should now see:")
print("  - Piper robotic arm (right side)")
print("  - G29 steering wheel (left side)")
print("  - Ground plane")
print("\nPress Ctrl+C to stop")
print("="*80 + "\n")

# Run simulation
step = 0
try:
    while simulation_app.is_running():
        world.step(render=True)
        
        if step % 500 == 0 and piper:
            joint_pos = piper.get_joint_positions()
            print(f"Step {step}: Piper active, joints: {np.round(joint_pos, 3)}")
        
        step += 1
        
except KeyboardInterrupt:
    print("\n\nSimulation stopped by user")

simulation_app.close()
print("\n✓ Demo complete!")
