"""
HICTP | HIGH-FIDELITY DIGITAL TWIN (GUI MODE)
Runs Isaac Sim with the visual interface enabled.
"""

import os
import sys
import yaml
import json
from typing import Optional

# --- Environment Setup ---
METADATA_PATH = "metadata.yaml"
if not os.path.exists(METADATA_PATH):
    METADATA_PATH = "/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/metadata.yaml"

with open(METADATA_PATH, 'r') as f:
    METADATA = yaml.safe_load(f)

ISAAC_PATH = METADATA['isaac_sim']['path']
sys.path.insert(0, os.path.join(ISAAC_PATH, "python_packages"))

from isaacsim import SimulationApp

# *** KEY CHANGE: GUI ENABLED ***
print("[LAUNCH] - Starting Isaac Sim with GUI...", flush=True)
sim_app = SimulationApp({
    "headless": False,  # Show the window!
    "width": 1920,
    "height": 1080
})

import omni.usd
from pxr import UsdGeom, Gf
from omni.isaac.core import World
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.stage import add_reference_to_stage

class HighFidelityTwinGUI:
    def __init__(self):
        self.world = World(physics_prim_path="/World/physicsScene", stage_units_in_meters=1.0)
        self.stage = omni.usd.get_context().get_stage()
        self._piper: Optional[Articulation] = None
        self._g29_path = "/World/G29"
        self._piper_path = "/World/Piper"

    def setup_scene(self):
        print("[SCENE] - Building Laboratory Environment...")
        self.world.scene.add_default_ground_plane()
        
        # Table 1: G29 Station (Left)
        table_l = UsdGeom.Cube.Define(self.stage, "/World/Table_Left")
        table_l.AddTranslateOp().Set(Gf.Vec3d(-0.6, 0.0, 0.35))
        table_l.AddScaleOp().Set(Gf.Vec3d(0.4, 0.6, 0.35))
        
        # Table 2: Piper Station (Right)
        table_r = UsdGeom.Cube.Define(self.stage, "/World/Table_Right")
        table_r.AddTranslateOp().Set(Gf.Vec3d(0.4, 0.0, 0.35))
        table_r.AddScaleOp().Set(Gf.Vec3d(0.4, 0.6, 0.35))

        # Load G29
        g29_usd = METADATA['isaac_sim']['assets']['g29_usd']
        add_reference_to_stage(usd_path=g29_usd, prim_path=self._g29_path)
        g29_prim = self.stage.GetPrimAtPath(self._g29_path)
        UsdGeom.XformCommonAPI(g29_prim).SetTranslate(Gf.Vec3d(-0.6, 0.3, 0.72))

        # Load Piper
        piper_usd = METADATA['isaac_sim']['assets']['piper_usd']
        add_reference_to_stage(usd_path=piper_usd, prim_path=self._piper_path)
        piper_prim = self.stage.GetPrimAtPath(self._piper_path)
        UsdGeom.XformCommonAPI(piper_prim).SetTranslate(Gf.Vec3d(0.4, 0.0, 0.72))
        
        # Initialize physics
        for _ in range(30): 
            sim_app.update()
        
        self._piper = Articulation(self._piper_path)
        self.world.scene.add(self._piper)
        
        # Set grasp pose
        if self._piper:
            grasp_joints = [0.8, -1.2, 1.5, 0.0, 1.3, 0.0, 0.02, -0.02]
            dof_count = self._piper.num_dof
            self._piper.set_joint_positions(grasp_joints[:dof_count])
            
        print("[SCENE] - Scene Ready. You should see the Isaac Sim window now!")

    def run_interactive(self):
        """Run with GUI - user can interact with the scene."""
        self.world.reset()
        print("\n" + "="*60)
        print("Isaac Sim GUI is now running!")
        print("You should see a window showing the Piper arm and G29 wheel.")
        print("Press Ctrl+C in this terminal to exit.")
        print("="*60 + "\n")
        
        step = 0
        try:
            while sim_app.is_running():
                self.world.step(render=True)  # Render enabled!
                
                # Update telemetry
                if self._piper and step % 10 == 0:
                    j_pos = self._piper.get_joint_positions()
                    grip_width = abs(j_pos[6] - j_pos[7]) * 1000 if len(j_pos) >= 8 else 0.0
                    
                    state = {
                        "wheel_angle": 0.0,
                        "gripper_pos": grip_width,
                        "phase": "Interactive Mode",
                        "gripper_xyz": [0.0, 0.15, 0.70]
                    }
                    
                    try:
                        with open("/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/digital_twin_state.json", "w") as f:
                            json.dump(state, f)
                    except:
                        pass
                
                step += 1
                if step % 100 == 0:
                    print(f"[RUNNING] Step {step} - Scene active")
                    
        except KeyboardInterrupt:
            print("\n[EXIT] Shutting down Isaac Sim...")
        
        sim_app.close()

if __name__ == "__main__":
    twin = HighFidelityTwinGUI()
    twin.setup_scene()
    twin.run_interactive()
