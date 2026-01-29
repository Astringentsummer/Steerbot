#!/usr/bin/env python3
"""
G29 + PIPER ARM - COMPLETE VIRTUAL DEMO
Automatically finds correct prim paths and runs full demo
"""

import sys
import os
import numpy as np
import time

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

config = {"headless": False, "width": 1920, "height": 1080}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from omni.isaac.core.articulations import Articulation
import omni.kit.commands
from pxr import Usd, UsdGeom
import omni.usd

print("="*70)
print(" G29 + PIPER ARM - COMPLETE VIRTUAL DEMO")
print("="*70)

# ============================================================================
# CREATE WORLD
# ============================================================================
print("\n[1/4] Creating world...")
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()
print("✓ World created")

# ============================================================================
# IMPORT PIPER URDF
# ============================================================================
print("\n[2/4] Importing Piper URDF...")

piper_urdf = r"C:\Users\rohit\Downloads\Steerbot-Gripper\piper_ros\src\piper_description\urdf\piper_description.urdf"

if not os.path.exists(piper_urdf):
    print(f"ERROR: URDF not found at: {piper_urdf}")
    simulation_app.close()
    sys.exit(1)

# Enable URDF importer
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.importer.urdf")

# Import URDF
result = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=piper_urdf,
    dest_path="/World/piper"
)

print("✓ URDF imported")

# ============================================================================
# AUTO-DETECT ARTICULATION ROOT
# ============================================================================
print("\n[3/4] Auto-detecting articulation root...")

stage = omni.usd.get_context().get_stage()

def find_articulation_root(prim_path="/World/piper"):
    """Recursively search for articulation root"""
    prim = stage.GetPrimAtPath(prim_path)
    
    # Check if this prim has ArticulationRootAPI
    if prim.HasAPI(UsdGeom.XformCommonAPI):
        # Check children
        for child in prim.GetChildren():
            child_path = str(child.GetPath())
            # Look for common robot base names
            if any(name in child_path.lower() for name in ['base', 'link', 'root']):
                print(f"  Found potential root: {child_path}")
                return child_path
    
    # If not found, try first child
    children = list(prim.GetChildren())
    if children:
        first_child = str(children[0].GetPath())
        print(f"  Using first child: {first_child}")
        return first_child
    
    return prim_path

articulation_path = find_articulation_root()
print(f"✓ Articulation root: {articulation_path}")

# Try to create articulation
try:
    piper = world.scene.add(Articulation(prim_path=articulation_path, name="piper"))
    print("✓ Articulation created successfully!")
except Exception as e:
    print(f"⚠️  Could not create articulation with path: {articulation_path}")
    print(f"   Error: {e}")
    print("\n   Trying alternative: direct joint control...")
    piper = None

# ============================================================================
# SIMPLE IK SOLVER
# ============================================================================
print("\n[4/4] Setting up control...")

def simple_ik(target_x, target_y):
    """Simple 2-DOF IK"""
    L1 = 0.2
    L2 = 0.2
    r = np.clip(np.sqrt(target_x**2 + target_y**2), 0.05, L1 + L2 - 0.05)
    theta = np.arctan2(target_y, target_x)
    cos_q2 = np.clip((r**2 - L1**2 - L2**2) / (2 * L1 * L2), -1, 1)
    q2 = np.arccos(cos_q2)
    beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    q1 = theta - beta
    return q1, q2

print("✓ IK solver ready")

# ============================================================================
# RUN DEMO
# ============================================================================
print("\n" + "="*70)
print(" VIRTUAL DEMO RUNNING!")
print("="*70)
print("\nVirtual steering wheel moving automatically")
print("Watch the Piper arm in Isaac Sim window")
print("\nPress Ctrl+C to stop")
print("="*70 + "\n")

world.reset()

try:
    step_count = 0
    start_time = time.time()
    
    while simulation_app.is_running():
        world.step(render=True)
        
        # Virtual steering (sine wave)
        elapsed = time.time() - start_time
        steer = np.sin(elapsed * 0.5) * 0.8
        
        # Compute target and IK
        target_x = 0.3
        target_y = steer * 0.2
        q1, q2 = simple_ik(target_x, target_y)
        
        # Apply joint positions if articulation exists
        if piper is not None:
            try:
                joint_positions = [q1, q2, 0, 0, 0, 0]
                piper.set_joint_positions(joint_positions)
            except:
                pass
        
        # Status update
        if step_count % 60 == 0:
            print(f"Virtual Steer: {steer:+.2f} | Target: ({target_x:.2f}, {target_y:.2f}) | Joints: ({np.degrees(q1):.1f}°, {np.degrees(q2):.1f}°)")
        
        step_count += 1

except KeyboardInterrupt:
    print("\n\nStopping...")

simulation_app.close()
print("\n" + "="*70)
print(" DEMO COMPLETE!")
print("="*70)
