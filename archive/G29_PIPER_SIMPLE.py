#!/usr/bin/env python3
"""
G29 + PIPER ARM - SIMPLIFIED WORKING VERSION
Direct G29 steering wheel control of Piper arm with IK
"""

import sys
import os
import numpy as np
import socket
import json
import threading
import time

# Isaac Sim Path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

config = {"headless": False, "width": 1920, "height": 1080"}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from omni.isaac.core.utils.extensions import enable_extension
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.stage import add_reference_to_stage
import omni.isaac.core.utils.numpy.rotations as rot_utils

# ============================================================================
# UDP LISTENER FOR G29 INPUT
# ============================================================================
UDP_IP = "127.0.0.1"
UDP_PORT = 5006
g29_data = {"steer": 0.0}
udp_running = True

def udp_listener():
    global g29_data, udp_running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(False)
        sock.settimeout(0.1)
        print(f"[UDP] Listening on {UDP_IP}:{UDP_PORT}")
        
        while udp_running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                g29_data["steer"] = msg.get("steer", 0.0)
            except socket.timeout:
                pass
            except Exception as e:
                pass
    finally:
        sock.close()

# Start UDP thread
udp_thread = threading.Thread(target=udp_listener, daemon=True)
udp_thread.start()

# ============================================================================
# CREATE WORLD
# ============================================================================
print("="*70)
print(" G29 + PIPER ARM - SIMPLIFIED VERSION")
print("="*70)
print("\n[1/3] Creating world...")

world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
world.scene.add_default_ground_plane()

print("✓ World created")

# ============================================================================
# LOAD PIPER ARM
# ============================================================================
print("\n[2/3] Loading Piper arm...")

# Path to Piper URDF
piper_urdf = r"C:\Users\rohit\Downloads\Steerbot-Gripper\piper_description\urdf\piper_v3.urdf"

if not os.path.exists(piper_urdf):
    print(f"ERROR: Piper URDF not found at: {piper_urdf}")
    simulation_app.close()
    sys.exit(1)

# Import URDF
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.importer.urdf")

import omni.kit.commands
from pxr import UsdPhysics

# Import Piper URDF
omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=piper_urdf,
    import_config=omni.isaac.core.utils.extensions.get_extension_path_from_name("omni.importer.urdf") + "/data/urdf/config/piper.json",
    dest_path="/World/piper"
)

# Get articulation
piper = world.scene.add(Articulation(prim_path="/World/piper/base_link", name="piper"))

print("✓ Piper arm loaded")

# ============================================================================
# SIMPLE IK SOLVER
# ============================================================================
print("\n[3/3] Setting up IK control...")

def simple_ik(target_x, target_y):
    """
    Simple 2-DOF IK for Piper arm
    Maps X,Y target to joint angles
    """
    # Arm parameters (approximate)
    L1 = 0.2  # Link 1 length
    L2 = 0.2  # Link 2 length
    
    # Distance to target
    r = np.sqrt(target_x**2 + target_y**2)
    
    # Clamp to reachable workspace
    r = np.clip(r, 0.05, L1 + L2 - 0.05)
    
    # Angle to target
    theta = np.arctan2(target_y, target_x)
    
    # Cosine law for elbow angle
    cos_q2 = (r**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_q2 = np.clip(cos_q2, -1, 1)
    q2 = np.arccos(cos_q2)
    
    # Shoulder angle
    beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    q1 = theta - beta
    
    return q1, q2

print("✓ IK solver ready")

# ============================================================================
# RESET AND RUN
# ============================================================================
print("\n" + "="*70)
print(" SYSTEM READY!")
print("="*70)
print("\nControls:")
print("  - Turn G29 steering wheel left/right")
print("  - Piper arm will track the wheel position")
print("\nPress Ctrl+C to stop")
print("="*70 + "\n")

world.reset()

# Main control loop
try:
    step_count = 0
    while simulation_app.is_running():
        world.step(render=True)
        
        # Get G29 steering angle (-1 to 1)
        steer = g29_data["steer"]
        
        # Map steering to target position
        # Steering left/right moves arm left/right
        target_x = 0.3  # Forward distance
        target_y = steer * 0.2  # Left/right based on steering
        
        # Compute IK
        q1, q2 = simple_ik(target_x, target_y)
        
        # Set joint positions (first 2 joints)
        joint_positions = [q1, q2, 0, 0, 0, 0]  # 6 joints total
        piper.set_joint_positions(joint_positions)
        
        # Print status every 60 frames (1 second)
        if step_count % 60 == 0:
            print(f"Steer: {steer:+.2f} | Target: ({target_x:.2f}, {target_y:.2f}) | Joints: ({np.degrees(q1):.1f}°, {np.degrees(q2):.1f}°)")
        
        step_count += 1

except KeyboardInterrupt:
    print("\n\nStopping...")

# Cleanup
udp_running = False
udp_thread.join(timeout=1)
simulation_app.close()
print("Done!")
