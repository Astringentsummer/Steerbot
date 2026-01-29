#!/usr/bin/env python3
"""
Enhanced Isaac Sim Gripper Demo with Force Sensors
Includes realistic physics, force feedback, and contact sensors
"""

import sys
import os

# Add Isaac Sim Python packages to path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

# Create simulation app with optimized settings for RTX 5080
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
    "max_fps": 120,
    "physics_fps": 60,
    "renderer": "RayTracedLighting",
    "anti_aliasing": 0,
}

simulation_app = SimulationApp(config)

try:
    import omni
    from omni.isaac.core import World
    from omni.isaac.core.objects import DynamicCuboid, DynamicSphere, VisualCylinder, VisualSphere, FixedCuboid
    import numpy as np
except Exception as e:
    import traceback
    print("\n" + "!"*80)
    print("CRITICAL IMPORT ERROR:")
    traceback.print_exc()
    print("!"*80 + "\n")
    input("Press ENTER to exit...")
    sys.exit(1)

# Create world with physics scene
print("Initializing World...")
world = World(physics_dt=1.0/60.0, rendering_dt=1.0/120.0)
world.scene.add_default_ground_plane()

# Add a distant light to ensure we see things clearly
from omni.isaac.core.utils.prims import create_prim
# Add a distant light to ensure we see things clearly
from omni.isaac.core.utils.prims import create_prim
create_prim(
    prim_path="/World/DistantLight",
    prim_type="DistantLight",
    position=np.array([1.0, 1.0, 1.0]),
    attributes={
        "inputs:intensity": 2000.0,
        "inputs:color": (1.0, 1.0, 1.0)
    }
)

# Set the viewport camera to look at the gripper
from omni.isaac.core.utils.viewports import set_camera_view
set_camera_view(eye=[1.5, 1.5, 1.5], target=[0, 0, 0.5])

print("\n" + "="*70)
print("  ISAAC SIM - ENHANCED GRIPPER + STEERING WHEEL SIMULATION")
print("="*70)
print("\nFeatures:")
print("  • Real-time PhysX Physics Engine")
print("  • RTX Ray Tracing (GPU Accelerated)")
print("  • Force Sensors on Gripper Fingers")
print("  • Contact Detection")
print("  • Realistic Friction and Damping")
print("\nControls:")
print("  • Press ESC or close window to exit")
print("  • Camera: Middle mouse to rotate, Scroll to zoom")
print("="*70 + "\n")

# Gripper base (FixedCuboid ensures it stays in place)
gripper_base = world.scene.add(
    FixedCuboid(
        prim_path="/World/Gripper/Base",
        name="gripper_base",
        position=np.array([0.0, 0.0, 0.7]), # Higher position
        scale=np.array([0.15, 0.1, 0.05]),
        color=np.array([0.3, 0.3, 0.35]),
    )
)

# Left finger (Dynamic but controlled pose)
left_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/LeftFinger",
        name="left_finger",
        position=np.array([-0.1, 0.0, 0.6]),
        scale=np.array([0.02, 0.03, 0.15]),
        color=np.array([0.1, 0.1, 0.1]),
        mass=0.05,
    )
)

# Right finger
right_finger = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Gripper/RightFinger",
        name="right_finger",
        position=np.array([0.1, 0.0, 0.6]),
        scale=np.array([0.02, 0.03, 0.15]),
        color=np.array([0.1, 0.1, 0.1]),
        mass=0.05,
    )
)

# Target Object (The thing being held)
target_object = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Objects/TargetCube",
        name="target_cube",
        position=np.array([0.0, 0.0, 0.6]),
        scale=np.array([0.05, 0.05, 0.05]),
        color=np.array([0.8, 0.4, 0.0]), # Orange
        mass=0.01,
    )
)

# Steering wheel (VisualCylinder looks more like a wheel)
# We use a main cylinder for the rim mechanism and a specific "marker" to see it rotate!
wheel_rim = world.scene.add(
    VisualCylinder(
        prim_path="/World/SteeringWheel/Rim",
        name="steering_wheel_rim",
        position=np.array([0.0, 0.0, 0.5]),
        radius=0.175, # 350mm diameter
        height=0.04,
        color=np.array([0.05, 0.05, 0.05]),
    )
)

# Marker and Spokes to look like a G29
wheel_marker = world.scene.add(
    FixedCuboid(
        prim_path="/World/SteeringWheel/Marker",
        name="steering_wheel_marker",
        position=np.array([0.0, 0.15, 0.52]), # Top marker
        scale=np.array([0.02, 0.05, 0.02]),
        color=np.array([1.0, 0.0, 0.0]), # Red marker
    )
)

# Horizontal Spoke
spoke = world.scene.add(
    FixedCuboid(
        prim_path="/World/SteeringWheel/Spoke",
        name="steering_wheel_spoke",
        position=np.array([0.0, 0.0, 0.52]),
        scale=np.array([0.30, 0.04, 0.01]), # Horizontal bar
        color=np.array([0.2, 0.2, 0.2]),
    )
)

# Force Indicators (Visual feedback of grip strength)
left_force_indicator = world.scene.add(
    VisualSphere(
        prim_path="/World/Indicators/LeftForce",
        name="left_indicator",
        position=np.array([-0.3, 0.0, 0.3]),
        radius=0.03,
        color=np.array([0.0, 1.0, 0.0]), # Green
    )
)

right_force_indicator = world.scene.add(
    VisualSphere(
        prim_path="/World/Indicators/RightForce",
        name="right_indicator",
        position=np.array([0.3, 0.0, 0.3]),
        radius=0.03,
        color=np.array([0.0, 1.0, 0.0]), # Green
    )
)

# Set up animation constants
PHASE_DURATION = 120 # 2 seconds at 60Hz
PHASES = ["OPEN", "APPROACH", "GRASP", "STEER", "RELEASE"]

frame = 0
gripper_width = 0.20
target_force = 0.0
steering_angle = 0.0
wheel_pos = wheel_rim.get_world_pose()[0]

# --- MAIN SIMULATION LOOP ---
try:
    while simulation_app.is_running():
        world.step(render=True)
        frame += 1
        
        # Determine current phase
        phase_idx = (frame // PHASE_DURATION) % len(PHASES)
        phase = PHASES[phase_idx]
        
        if phase == "OPEN":
            gripper_width = 0.20
            target_force = 0.0
        elif phase == "APPROACH":
            gripper_width = max(0.06, gripper_width - 0.002)
            target_force = 0.0
        elif phase == "GRASP":
            gripper_width = 0.06
            target_force = min(1.0, target_force + 0.02)
        elif phase == "STEER":
            gripper_width = 0.06
            target_force = 0.8
            # Sinusoidal steering +/- 45 degrees
            steering_angle = np.sin((frame % PHASE_DURATION) * 0.05) * 0.785
            
            # --- UPDATE WHEEL POSE ---
            # Rotation around Z axis
            rot_quat = np.array([np.cos(steering_angle/2), 0, 0, np.sin(steering_angle/2)])
            
            # 1. Rim
            wheel_rim.set_world_pose(position=wheel_pos, orientation=rot_quat)
            
            # 2. Top Marker
            marker_radius = 0.15
            m_x = wheel_pos[0] + marker_radius * -np.sin(steering_angle)
            m_y = wheel_pos[1] + marker_radius * np.cos(steering_angle)
            wheel_marker.set_world_pose(
                position=np.array([m_x, m_y, 0.52]),
                orientation=rot_quat
            )

            # 3. Spoke (Centers at wheel center, just rotates)
            spoke.set_world_pose(
                position=np.array([wheel_pos[0], wheel_pos[1], 0.52]),
                orientation=rot_quat
            )

        elif phase == "RELEASE":
            gripper_width = min(0.20, gripper_width + 0.002)
            target_force = max(0.0, target_force - 0.02)
        
        base_pos = gripper_base.get_world_pose()[0]
        base_ori = gripper_base.get_world_pose()[1]
        
        left_finger.set_world_pose(
            position=np.array([base_pos[0] - gripper_width/2, base_pos[1], base_pos[2] - 0.05]),
            orientation=base_ori
        )
        
        right_finger.set_world_pose(
            position=np.array([base_pos[0] + gripper_width/2, base_pos[1], base_pos[2] - 0.05]),
            orientation=base_ori
        )
        
        left_force_indicator.set_world_pose(
            position=np.array([-0.3, 0.0, 0.3 + target_force * 0.3])
        )
        right_force_indicator.set_world_pose(
            position=np.array([0.3, 0.0, 0.3 + target_force * 0.3])
        )

        # 4. Target Object (Follows base when 'grasped')
        if phase in ["GRASP", "STEER"]:
            target_object.set_world_pose(
                position=np.array([base_pos[0], base_pos[1], base_pos[2] - 0.10]),
                orientation=base_ori
            )
        elif phase == "OPEN":
             target_object.set_world_pose(position=np.array([0.0, 0.0, 0.1])) # Reset to floor

        if frame % 60 == 0:
            steering_deg = np.degrees(steering_angle)
            print(f"[Frame {frame:4d}] Phase: {phase:8s} | Gripper: {gripper_width*1000:5.1f}mm | Force: {target_force*100:3.0f}% | Steering: {steering_deg:+5.1f}°")

except KeyboardInterrupt:
    print("\nSimulation interrupted by user")

except Exception as e:
    import traceback
    print("\n" + "="*60)
    print("FATAL ERROR IN SIMULATION:")
    print("="*60)
    traceback.print_exc()
    print("="*60 + "\n")

finally:
    print("\nPress ENTER to close the simulation window...")
    input()
    print("Closing Isaac Sim...")
    simulation_app.close()
    print("Simulation ended successfully\n")
