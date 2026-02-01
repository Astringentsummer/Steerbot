import argparse
import os
import sys

# Set up Isaac Sim path from metadata
ISAAC_SIM_PATH = "/mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64"
sys.path.append(os.path.join(ISAAC_SIM_PATH, "exts/omni.isaac.examples/python_samples"))

from omni.isaac.kit import SimulationApp

# 1. Initialize Simulation App
CONFIG = {
    "width": 1280,
    "height": 720,
    "window_width": 1920,
    "window_height": 1080,
    "headless": False,
    "renderer": "RayTracedLighting",
    "display_options": 32768,  # Show joints by default
}

simulation_app = SimulationApp(CONFIG)

# 2. Import Isaac Sim core modules
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.extensions import enable_extension
import numpy as np

# 3. Enable ROS 2 Bridge
enable_extension("omni.isaac.ros2_bridge")

# 4. Import our custom bridge
sys.path.append(os.getcwd())
try:
    from digital_twin.isaac_ros2_bridge import bridge_factory
except ImportError:
    print("Warning: digital_twin.isaac_ros2_bridge not found. ROS 2 bridge will not be active.")
    bridge_factory = None

class Mission55Sim:
    def __init__(self):
        self._world = World(stage_units_in_meters=1.0)
        self._setup_scene()
        self._bridge = None
        
    def _setup_scene(self):
        # Paths to USD assets (using WSL mount points)
        PROJECT_ROOT = "/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper"
        PIPER_USD = os.path.join(PROJECT_ROOT, "dev/piper_isaac_sim/usd/piper_description.usd")
        G29_USD = os.path.join(PROJECT_ROOT, "isaac/scenes/g29.usd")
        
        # Ground Plane
        self._world.scene.add_default_ground_plane()
        
        # Load Piper Arm
        add_reference_to_stage(usd_path=PIPER_USD, prim_path="/World/Piper")
        self._piper = self._world.scene.add(Articulation(prim_path="/World/Piper", name="piper_arm"))
        
        # Load G29 Wheel
        add_reference_to_stage(usd_path=G29_USD, prim_path="/World/G29")
        self._g29 = self._world.scene.add(Articulation(prim_path="/World/G29", name="g29_wheel"))
        
        # Set initial poses
        self._piper.set_world_pose(position=np.array([0.0, 0.0, 0.0]))
        self._g29.set_world_pose(position=np.array([0.5, 0.0, 0.5]), orientation=np.array([0.707, 0, 0.707, 0])) # Rotated to face robot
        
        print("Scene Setup: Piper Arm and G29 Wheel loaded successfully.")

    def run(self):
        self._world.reset()
        
        # Initialize Bridge if factory exists
        if bridge_factory:
            self._bridge = bridge_factory(simulation_app, self._piper)
            print("ROS 2 Bridge: MoveIt 2 listener active.")
        
        while simulation_app.is_running():
            self._world.step(render=True)
            
            # Mission 55 Progress Monitoring (Optional)
            if self._world.is_playing():
                # Here we could add logic to check if 55 degrees is reached
                pass
                
        simulation_app.close()

if __name__ == "__main__":
    sim = Mission55Sim()
    sim.run()
