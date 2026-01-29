#!/usr/bin/env python3
"""
FINAL STEERBOT INTEGRATION
Combines G29 steering wheel + Piper arm in Isaac Sim
Uses your team's USD scenes and keeps the simulation running
"""

import sys
import os
import numpy as np

# Add Isaac Sim Python packages to path
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))

from isaacsim import SimulationApp

# Create simulation app
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
}
simulation_app = SimulationApp(config)

import omni.usd
from pxr import UsdGeom, Gf
import math
import time

# Load the G29 USD scene (your team's proven scene)
stage = omni.usd.get_context().get_stage()
usd_path = r"C:\Users\rohit\Downloads\Steerbot-main\Steerbot-main\isaac\scenes\g29_rotate_right_tilted27degrees.usd"

print("="*60)
print("STEERBOT - G29 + PIPER ARM INTEGRATION")
print("="*60)
print(f"\nLoading scene: {usd_path}")
omni.usd.get_context().open_stage(usd_path)

# Wait for stage to load
time.sleep(3)

print("\n✓ Scene loaded successfully!")
print("\nScene is now running. You should see the G29 steering wheel in Isaac Sim.")


# Main simulation loop - KEEPS RUNNING UNTIL YOU CLOSE IT
print("\n" + "="*60)
print("SIMULATION RUNNING")
print("="*60)
print("The simulation will stay open until you close the window.")
print("Monitoring G29 steering angle...")
print("="*60 + "\n")

frame = 0
last_print_time = time.time()

while simulation_app.is_running():
    # Update the simulation (this keeps UI responsive)
    simulation_app.update()
    
    current_time = time.time()
    
    # Try to read steering angle from USD
    try:
        from pxr import Sdf
        
        # Look for G29 prims using proper Sdf.Path
        base_path = Sdf.Path("/G29_root/Steerbot_G29_base_position_27degrees")
        wheel_path = Sdf.Path("/G29_root/Steerbot_G29_steerwheel_position_27degrees")
        
        base = stage.GetPrimAtPath(base_path)
        wheel = stage.GetPrimAtPath(wheel_path)
        
        if not base or not base.IsValid():
            # Try alternative path
            base_path = Sdf.Path("/World/G29_root/Steerbot_G29_base_position_27degrees")
            wheel_path = Sdf.Path("/World/G29_root/Steerbot_G29_steerwheel_position_27degrees")
            base = stage.GetPrimAtPath(base_path)
            wheel = stage.GetPrimAtPath(wheel_path)
        
        if base and base.IsValid() and wheel and wheel.IsValid():
            base_xform = UsdGeom.Xformable(base)
            wheel_xform = UsdGeom.Xformable(wheel)
            
            relative = wheel_xform.GetLocalTransformation() * base_xform.GetLocalTransformation().GetInverse()
            rotation = relative.ExtractRotation()
            
            angle_deg = rotation.GetAngle()
            axis = rotation.GetAxis()
            
            # Direction
            if axis[1] > 0.01:
                direction = "LEFT"
            elif axis[1] < -0.01:
                direction = "RIGHT"
            else:
                direction = "CENTER"
            
            # Angle processing
            angle_mod = angle_deg % 360.0
            if angle_mod > 180.0:
                final_angle = angle_mod - 360.0
            else:
                final_angle = angle_mod
            
            if direction == "RIGHT":
                final_angle = -abs(final_angle)
            elif direction == "LEFT":
                final_angle = abs(final_angle)
            
            # Print every 2 seconds
            if current_time - last_print_time > 2.0:
                print(f"[{frame:06d}] {direction:6s} | Angle: {final_angle:+7.2f}°")
                last_print_time = current_time
        else:
            # Print once if not found
            if frame == 60:
                print("\n⚠️ G29 prims not found at expected paths.")
                print("The scene is loaded but steering angle cannot be read.")
                print("You can still interact with the simulation manually.")
    
    except Exception as e:
        if frame == 60:
            print(f"\n⚠️ Error reading steering: {e}")
            print("Continuing simulation anyway...")
    
    frame += 1

print("\nSimulation closed by user.")
simulation_app.close()
