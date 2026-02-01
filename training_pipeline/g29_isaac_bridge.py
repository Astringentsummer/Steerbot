#!/usr/bin/env python3
"""
G29 Hardware Bridge - Real-time G29 Wheel → Isaac Sim
Synchronizes physical G29 steering wheel with virtual wheel in Isaac Sim
"""
import sys
import os

# Isaac Sim Windows path
ISAAC_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_PATH, "exts", "omni.isaac.kit", "omni", "isaac", "kit"))

from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})  # GUI mode to see wheel

import numpy as np
from omni.isaac.core import World
from omni.isaac.core.prims import RigidPrim
from omni.isaac.core.utils.stage import add_reference_to_stage
from pxr import Usd, UsdGeom, Gf
import threading
import time

# Import G29 reader (your existing code)
try:
    import inputs  # pip install inputs
    G29_AVAILABLE = True
except ImportError:
    G29_AVAILABLE = False
    print("[WARNING] 'inputs' library not found. Install with: pip install inputs")


class G29Reader:
    """Read G29 steering wheel angle in real-time"""
    
    def __init__(self):
        self.current_angle = 0.0  # Radians
        self.running = False
        self.thread = None
        
        if not G29_AVAILABLE:
            print("[WARNING] G29 hardware not available, using simulated input")
    
    def start(self):
        """Start reading G29 in background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print(" G29 reader started")
    
    def stop(self):
        """Stop reading G29"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _read_loop(self):
        """Background loop to read G29"""
        if not G29_AVAILABLE:
            # Simulate sinusoidal input for testing
            t = 0
            while self.running:
                self.current_angle = np.sin(t * 0.5) * np.radians(55)
                t += 0.01
                time.sleep(0.01)
            return
        
        # Real G29 reading
        while self.running:
            try:
                events = inputs.get_gamepad()
                for event in events:
                    if event.code == 'ABS_X':  # Steering axis
                        # Convert to radians (-900° to +900° → radians)
                        raw_value = event.state
                        angle_deg = (raw_value / 32768.0) * 450.0  # Max 450° each direction
                        self.current_angle = np.radians(angle_deg)
            except Exception as e:
                print(f"[ERROR] G29 read error: {e}")
                time.sleep(0.1)
    
    def get_angle(self):
        """Get current wheel angle in radians"""
        return self.current_angle


class VirtualG29Wheel:
    """Virtual G29 steering wheel in Isaac Sim"""
    
    def __init__(self, world):
        self.world = world
        self.wheel_prim = None
        self.create_wheel()
    
    def create_wheel(self):
        """Create virtual steering wheel in Isaac Sim"""
        stage = self.world.stage
        
        # Create wheel as cylinder
        wheel_path = "/World/G29_Wheel"
        wheel_geom = UsdGeom.Cylinder.Define(stage, wheel_path)
        wheel_geom.CreateRadiusAttr(0.15)  # 15cm radius
        wheel_geom.CreateHeightAttr(0.05)  # 5cm thick
        wheel_geom.CreateAxisAttr("Z")  # Rotate around Z axis
        
        # Set position
        xform = UsdGeom.Xformable(wheel_geom)
        xform.AddTranslateOp().Set(Gf.Vec3d(0.5, 0, 1.0))  # 50cm forward, 1m high
        
        # Add physics
        self.wheel_prim = RigidPrim(prim_path=wheel_path, name="g29_wheel")
        self.world.scene.add(self.wheel_prim)
        
        print(" Virtual G29 wheel created")
    
    def set_angle(self, angle_rad):
        """Set wheel rotation angle"""
        if self.wheel_prim:
            # Set rotation around Z axis
            quat = self._angle_to_quaternion(angle_rad)
            self.wheel_prim.set_world_pose(orientation=quat)
    
    def _angle_to_quaternion(self, angle_rad):
        """Convert angle to quaternion for Z-axis rotation"""
        half_angle = angle_rad / 2.0
        return np.array([
            np.cos(half_angle),  # w
            0,                    # x
            0,                    # y
            np.sin(half_angle)    # z
        ])


def run_g29_bridge():
    """Main loop for G29 hardware bridge"""
    
    print("=" * 80)
    print("G29 HARDWARE BRIDGE - Real Wheel → Isaac Sim")
    print("=" * 80)
    
    # Create world
    world = World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()
    
    # Create virtual wheel
    virtual_wheel = VirtualG29Wheel(world)
    
    # Start G29 reader
    g29 = G29Reader()
    g29.start()
    
    # Reset world
    world.reset()
    
    print("\n" + "=" * 80)
    print("BRIDGE ACTIVE - Turn your G29 wheel!")
    print("Press Ctrl+C to stop")
    print("=" * 80 + "\n")
    
    try:
        frame = 0
        while simulation_app.is_running():
            # Read G29 angle
            angle = g29.get_angle()
            
            # Update virtual wheel
            virtual_wheel.set_angle(angle)
            
            # Step simulation
            world.step(render=True)
            
            # Print status every 60 frames (~1 second)
            if frame % 60 == 0:
                print(f"G29 Angle: {np.degrees(angle):+7.2f}° ({angle:+.4f} rad)")
            
            frame += 1
    
    except KeyboardInterrupt:
        print("\n\nStopping bridge...")
    
    finally:
        g29.stop()
        simulation_app.close()
        print(" Bridge closed")


if __name__ == "__main__":
    run_g29_bridge()
