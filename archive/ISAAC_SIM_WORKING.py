#!/usr/bin/env python3
"""
WORKING ISAAC SIM DEMO - Piper Arm Controls G29 Wheel
Uses valid USD primitives (no Torus!)
"""

import sys
import os
import numpy as np

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.append(os.path.join(ISAAC_SIM_PATH, "exts", "omni.isaac.kit", "omni", "isaac", "kit"))

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from pxr import UsdGeom, Gf, UsdPhysics
import carb

print("=" * 70)
print(" ISAAC SIM - PIPER ARM CONTROLS G29 WHEEL")
print("=" * 70)
print("")

# Create world
print("[1/5] Creating world...")
world = World()
world.scene.add_default_ground_plane()
print("✓ World created")

# Get stage
stage = world.stage

# Create table
print("\n[2/5] Creating table...")
table_path = "/World/Table"
table = UsdGeom.Cube.Define(stage, table_path)
table.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 0.4))
table.AddScaleOp().Set(Gf.Vec3d(0.8, 0.6, 0.8))
table.CreateDisplayColorAttr().Set([Gf.Vec3f(0.6, 0.4, 0.2)])
print("✓ Table created")

# Create steering wheel using CYLINDER (not Torus!)
print("\n[3/5] Creating steering wheel...")
wheel_path = "/World/SteeringWheel"

# Create wheel rim as thin cylinder
wheel_rim = UsdGeom.Cylinder.Define(stage, wheel_path + "/Rim")
wheel_rim.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 0.9))
wheel_rim.AddScaleOp().Set(Gf.Vec3d(0.15, 0.02, 0.15))  # Thin disk
wheel_rim.AddOrientOp().Set(Gf.Quatf(0.7071, 0.7071, 0, 0))  # Rotate to vertical (use Quatf!)
wheel_rim.CreateDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.2, 0.2)])

# Add physics to wheel
UsdPhysics.RigidBodyAPI.Apply(stage.GetPrimAtPath(wheel_path + "/Rim"))
UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(wheel_path + "/Rim"))

# Create wheel spokes
for i in range(4):
    angle = i * np.pi / 2
    spoke_path = f"{wheel_path}/Spoke{i}"
    spoke = UsdGeom.Cylinder.Define(stage, spoke_path)
    
    x_offset = 0.1 * np.cos(angle)
    y_offset = 0.1 * np.sin(angle)
    
    spoke.AddTranslateOp().Set(Gf.Vec3d(0.5 + x_offset, y_offset, 0.9))
    spoke.AddScaleOp().Set(Gf.Vec3d(0.01, 0.1, 0.01))
    spoke.AddOrientOp().Set(Gf.Quatf(0.7071, 0, 0.7071, 0))  # Use Quatf!
    spoke.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])

print("✓ Steering wheel created (using Cylinder)")

# Import Piper arm URDF
print("\n[4/5] Loading Piper arm...")
piper_urdf = r"C:\Users\rohit\Downloads\Steerbot-Gripper\piper_ros\src\piper_description\urdf\piper_description.urdf"

if os.path.exists(piper_urdf):
    from omni.isaac.core.utils.extensions import enable_extension
    enable_extension("omni.importer.urdf")
    
    import omni.kit.commands
    
    # Import URDF
    omni.kit.commands.execute(
        "URDFParseAndImportFile",
        urdf_path=piper_urdf,
        import_config=omni.isaac.core.utils.extensions.get_extension_path_from_name(
            "omni.importer.urdf"
        ) + "/data/urdf/config/default.json",
        dest_path="/World/Piper"
    )
    
    # Position the arm
    piper_prim = stage.GetPrimAtPath("/World/Piper")
    if piper_prim:
        xform = UsdGeom.Xformable(piper_prim)
        xform.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.8))
        print("✓ Piper arm loaded")
    else:
        print("⚠️  Piper arm imported but prim path may differ")
        print("   Check Stage panel for actual path")
else:
    print(f"⚠️  URDF not found at: {piper_urdf}")
    print("   Wheel will be created, but no arm")

# Create camera view
print("\n[5/5] Setting up camera...")
camera_path = "/World/Camera"
camera = UsdGeom.Camera.Define(stage, camera_path)
camera.AddTranslateOp().Set(Gf.Vec3d(2, 2, 1.5))
camera.AddRotateXYZOp().Set(Gf.Vec3d(-20, 45, 0))
print("✓ Camera positioned")

print("\n" + "=" * 70)
print(" ISAAC SIM DEMO READY!")
print("=" * 70)
print("")
print("What you should see:")
print("  - Table (brown cube)")
print("  - Steering wheel (black cylinder with spokes)")
print("  - Piper arm (if URDF loaded)")
print("")
print("Controls:")
print("  - Mouse: Rotate view")
print("  - Scroll: Zoom")
print("  - WASD: Move camera")
print("")
print("Press PLAY button in Isaac Sim to start physics simulation")
print("Press Ctrl+C here to stop")
print("")

# Keep simulation running
try:
    while simulation_app.is_running():
        world.step(render=True)
except KeyboardInterrupt:
    print("\nStopping...")

simulation_app.close()
print("Demo complete!")
