#!/usr/bin/env python3
"""
Professional Isaac Sim Demonstration: Piper Arm & G29 Integration (Diagnostic Version)
High-Fidelity CAD Integration and Procedural Workspace Design
"""

import sys
import os
import numpy as np
import traceback
import time

# Isaac Sim configuration
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

# Start simulation app
print("Starting Simulation App...")
simulation_app = SimulationApp({"headless": False, "width": 1920, "height": 1080})

try:
    import omni.usd
    from pxr import UsdGeom, Gf, Sdf, UsdPhysics
    from omni.isaac.core import World
    from omni.isaac.core.articulations import Articulation
    from omni.isaac.core.utils.stage import add_reference_to_stage

    print("=" * 80)
    print(" PROFESSIONAL ROBOTICS SIMULATION: PIPER & G29")
    print("=" * 80)

    # Initialize world
    print("Initializing World...")
    world = World(physics_prim_path="/World/physicsScene", stage_units_in_meters=1.0)
    stage = omni.usd.get_context().get_stage()

    # ============================================================================
    # LABORATORY WORKSPACE
    # ============================================================================
    print("[1/4] Designing professional workspace...")

    # Ground plane
    world.scene.add_default_ground_plane()

    # Lab Table (Using standard Cube for stability)
    table = UsdGeom.Cube.Define(stage, "/World/LabTable")
    table.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.35))
    table.AddScaleOp().Set(Gf.Vec3d(1.0, 0.75, 0.35))

    # ============================================================================
    # STEERING WHEEL ASSEMBLY (G29)
    # ============================================================================
    print("[2/4] Constructing steering wheel mount...")

    # Mount Base
    mount_base = UsdGeom.Cube.Define(stage, "/World/G29Mount")
    mount_base.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.9))
    mount_base.AddScaleOp().Set(Gf.Vec3d(0.1, 0.1, 0.15))

    # Wheel Rim
    wheel_rim = UsdGeom.Cylinder.Define(stage, "/World/SteeringWheel/Rim")
    wheel_rim.GetRadiusAttr().Set(0.14)
    wheel_rim.GetHeightAttr().Set(0.02)
    wheel_rim.AddTranslateOp().Set(Gf.Vec3d(0, 0.1, 1.05))
    wheel_rim.AddRotateXYZOp().Set(Gf.Vec3d(90, 0, 0))

    # Spokes
    for i in range(3):
        spoke = UsdGeom.Cube.Define(stage, f"/World/SteeringWheel/Spoke_{i}")
        spoke.AddTranslateOp().Set(Gf.Vec3d(0, 0.1, 1.05))
        spoke.AddRotateXYZOp().Set(Gf.Vec3d(90, 0, i * 120))
        spoke.AddScaleOp().Set(Gf.Vec3d(0.12, 0.015, 0.005))

    # = :===========================================================================
    # AUTHENTIC PIPER ROBOTIC ARM
    # ============================================================================
    piper_usd_path = r"C:\Users\rohit\Downloads\piper_isaac_sim-master\piper_isaac_sim-master\usd\piper_description.usd"
    piper_usd_path = piper_usd_path.replace("\\", "/")
    print(f"[3/4] Loading authentic Piper USD: {os.path.basename(piper_usd_path)}")

    if not os.path.exists(piper_usd_path):
        print(f"CRITICAL ERROR: Could not find Piper USD at {piper_usd_path}")
        simulation_app.close()
        sys.exit(1)

    add_reference_to_stage(usd_path=piper_usd_path, prim_path="/World/Piper")

    # Wait for assets to load
    print("Waiting for assets to load...")
    for i in range(30):
        simulation_app.update()

    # Articulation test (wrapped in sub-try)
    try:
        print("Checking for Articulation Root...")
        # Check if /World/Piper or a child has ArticulationRoot
        piper_robot = Articulation(prim_path="/World/Piper")
        world.scene.add(piper_robot)
        piper_robot.set_world_pose(position=np.array([-0.35, 0.1, 0.75]))
    except Exception as e:
        print(f"Warning: Could not initialize Articulation on /World/Piper: {e}")
        print("Continuing with visual-only model for now.")

    # ============================================================================
    # CAMERA AND ILLUMINATION
    # ============================================================================
    print("[4/4] Setting professional camera angles...")

    camera_path = "/World/MainCamera"
    camera = UsdGeom.Camera.Define(stage, camera_path)
    camera.AddTranslateOp().Set(Gf.Vec3d(-1.2, -1.5, 1.8))
    camera.AddRotateXYZOp().Set(Gf.Vec3d(-25, 15, 0))

    # Lighting (Fixed: UsdLux for lights)
    from pxr import UsdLux
    light = UsdLux.DistantLight.Define(stage, "/World/DefaultLight")
    light.GetIntensityAttr().Set(2000)

    print("\n" + "=" * 80)
    print(" SIMULATION LIVE: PRESS CTRL+C TO CLOSE")
    print("=" * 80)

    world.reset()

    while simulation_app.is_running():
        world.step(render=True)

except Exception:
    print("\n" + "!" * 80)
    print(" AN UNEXPECTED ERROR OCCURRED")
    print("!" * 80)
    traceback.print_exc()
    print("!" * 80)

finally:
    print("Shutting down simulation...")
    simulation_app.close()
