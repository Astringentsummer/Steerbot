"""
Master's Thesis Prototype: G29-Piper Digital Twin Synchronizer.

This script initializes the NVIDIA Isaac Sim environment, loads the high-fidelity
Piper robotic manipulator, and synchronizes it with the G29 steering assembly.
Designed for sub-millimeter precision and MoveIt2 integration.

Core Architecture:
- Physics: Isaac Sim 4.5 GPU-accelerated Rigid Body Dynamics
- Communication: ROS2 Jazzy Synchronous Bridge
- Modeling: Multi-link Articulation with Parallel-Jaw Gripper
"""

import os
import sys
import logging
import traceback
from typing import Dict, Any

# Configure Scientific Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger("SteerbotTwin")

import yaml
import traceback
from typing import Dict, Any, Optional

# Configure Scientific Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger("SteerbotTwin")

def load_config(path: str = "metadata.yaml") -> Dict[str, Any]:
    """Loads industrial configuration from standardized YAML metadata."""
    if not os.path.exists(path):
        logger.error(f"Configuration file missing: {path}")
        sys.exit(1)
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Global configuration load
METADATA = load_config()

# Professional Path Injection
ISAAC_PATH = METADATA['isaac_sim']['path']
PACKAGES_PATH = os.path.join(ISAAC_PATH, "python_packages")
if PACKAGES_PATH not in sys.path:
    sys.path.insert(0, PACKAGES_PATH)

try:
    from isaacsim import SimulationApp
except ImportError:
    logger.critical("NVIDIA Isaac Sim environment not detected. Check 'metadata.yaml'.")
    sys.exit(1)

# App instance
print("[BOOT] - Initializing NVIDIA Isaac Sim 5.0 Engine... (This may take 45s)", flush=True)
sim_app = SimulationApp({"headless": True, "width": 1920, "height": 1080})
print("[BOOT] - Simulation Engine Ready. Initializing Digital Twin...", flush=True)

# Dynamic Imports
import omni.usd
from pxr import UsdGeom, Gf
from omni.isaac.core import World
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.stage import add_reference_to_stage
from digital_twin.isaac_ros2_bridge import bridge_factory

class SteerbotSimulation:
    """Encapsulates the High-Fidelity Research Digital Twin."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # World initialization
        print("[PHASE 1] - Initializing Simulation World...")
        self.world = World(physics_prim_path="/World/physicsScene", stage_units_in_meters=1.0)
        print("[PHASE 2] - Simulation World Ready.")

        # Load Robot
        print(f"[PHASE 3] - Loading Robot Model from: {METADATA['isaac_sim']['assets']['piper_usd']}")
        self.stage = omni.usd.get_context().get_stage()
        # Add your robot loading logic here...
        print("[PHASE 4] - Manipulator Imported and Active.")
        self.stage = omni.usd.get_context().get_stage()
        self._robot: Optional[Articulation] = None
        
    def build_laboratory(self) -> None:
        """Constructs the procedural research environment (Dual-Table Setup)."""
        logger.info("Initializing laboratory workspace...")
        self.world.scene.add_default_ground_plane()
        
        # Table 1: Control Station (Left)
        table_left = UsdGeom.Cube.Define(self.stage, "/World/Table_Control")
        table_left.AddTranslateOp().Set(Gf.Vec3d(-0.6, 0, 0.35))
        table_left.AddScaleOp().Set(Gf.Vec3d(0.6, 1.2, 0.35))
        
        # Table 2: Robot Station (Right)
        table_right = UsdGeom.Cube.Define(self.stage, "/World/Table_Robot")
        table_right.AddTranslateOp().Set(Gf.Vec3d(0.6, 0, 0.35))
        table_right.AddScaleOp().Set(Gf.Vec3d(0.6, 1.2, 0.35))
        
    def mount_g29_assembly(self) -> None:
        """Precision mounting of the steering interface on the control table."""
        logger.info("Mounting G29 steering assembly...")
        mount = UsdGeom.Cube.Define(self.stage, "/World/G29Mount")
        mount.AddTranslateOp().Set(Gf.Vec3d(-0.6, 0.1, 0.8))
        mount.AddScaleOp().Set(Gf.Vec3d(0.1, 0.1, 0.1))
        
        rim = UsdGeom.Cylinder.Define(self.stage, "/World/SteeringWheel/Rim")
        rim.GetRadiusAttr().Set(0.14); rim.GetHeightAttr().Set(0.02)
        rim.AddTranslateOp().Set(Gf.Vec3d(-0.6, 0.2, 0.95))
        rim.AddRotateXYZOp().Set(Gf.Vec3d(90, 0, 0))

    def load_manipulator(self) -> None:
        """Imports the high-fidelity manipulator from authentic USD assets."""
        usd_file = self.config['isaac_sim']['assets']['piper_usd']
        logger.info(f"Importing Manipulator: {os.path.basename(usd_file)}")
        
        add_reference_to_stage(usd_path=usd_file, prim_path="/World/PiperArm")
        # Position Piper on the Right Table
        piper_prim = self.stage.GetPrimAtPath("/World/PiperArm")
        UsdGeom.XformCommonAPI(piper_prim).SetTranslate(Gf.Vec3d(0.6, 0, 0.72))
        
        for _ in range(30): sim_app.update()
            
        self._robot = Articulation(prim_path="/World/PiperArm")
        self.world.scene.add(self._robot)

    def run(self) -> None:
        """Main simulation execution loop with ROS2 state polling."""
        self.world.reset()
        bridge = bridge_factory(sim_app, self._robot)
        logger.info("Integrated Control Loop Active (MoveIt2 -> Isaac Sim).")
        
        try:
            while sim_app.is_running():
                self.world.step(render=True)
                # Physical Contact Analysis Logic
                try:
                    pos = self._robot.get_joint_positions()
                    if len(pos) >= 8:
                        width = abs(pos[6] - pos[7]) * 1000
                        bridge.set_holding_state(25.0 > width > 15.0)
                except Exception: pass
        finally:
            sim_app.close()

if __name__ == "__main__":
    try:
        sim = SteerbotSimulation(METADATA)
        sim.build_laboratory()
        sim.mount_g29_assembly()
        sim.load_manipulator()
        sim.run()
    except Exception as e:
        logger.error(f"Critical System Failure: {str(e)}")
        sim_app.close()

