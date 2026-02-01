import os
import sys
import numpy as np

# 1. Setup Isaac Sim Path
# Updated to match actual file locations in Downloads
ISAAC_SIM_PATH = "/mnt/c/Users/rohit/Downloads"
sys.path.append(os.path.join(ISAAC_SIM_PATH, "exts/omni.isaac.examples/python_samples"))

from omni.isaac.kit import SimulationApp

# Initialize Simulation App
is_headless = "--headless" in sys.argv
simulation_app = SimulationApp({"headless": is_headless})

# 2. Import Isaac core modules
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.extensions import enable_extension
import omni.graph.core as og
from omni.isaac.core_nodes.scripts.utils import set_target_prims
from pxr import UsdPhysics, Usd

# 3. Enable ROS 2 Bridge
enable_extension("omni.isaac.ros2_bridge")

class SteeringSimulationBackend:
    def __init__(self):
        self._world = World(stage_units_in_meters=1.0)
        self._setup_scene()
        self._setup_action_graph()
        self._configure_physics()
        
    def _setup_scene(self):
        PROJECT_ROOT = "/mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper"
        PIPER_USD = os.path.join(PROJECT_ROOT, "prototype_assets/piper_isaac_sim/usd/piper_description.usd")
        G29_USD = os.path.join(PROJECT_ROOT, "simulation_assets/scenes/g29.usd")
        
        self._world.scene.add_default_ground_plane()
        
        # Load Piper
        add_reference_to_stage(usd_path=PIPER_USD, prim_path="/World/Piper")
        self._piper = self._world.scene.add(Articulation(prim_path="/World/Piper", name="piper_arm"))
        
        # Load G29
        add_reference_to_stage(usd_path=G29_USD, prim_path="/World/G29")
        self._g29 = self._world.scene.add(Articulation(prim_path="/World/G29", name="g29_wheel"))
        
        # Set Poses (Optimized for reach)
        self._piper.set_world_pose(position=np.array([0.0, 0.0, 0.0]))
        self._g29.set_world_pose(position=np.array([0.35, 0.0, 0.45]), orientation=np.array([0.707, 0, 0.707, 0]))

    def _setup_action_graph(self):
        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("ReadSimTime", "omni.isaac.core_nodes.IsaacReadSimulationTime"),
                    ("PublishJointState", "omni.isaac.ros2_bridge.ROS2PublishJointState"),
                    ("PublishTF", "omni.isaac.ros2_bridge.ROS2PublishTransformTree"),
                    ("SubscribeJointState", "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
                    ("ArticulationController", "omni.isaac.core_nodes.IsaacArticulationController"),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ReadSimTime.inputs:execIn"),
                    ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
                    ("OnPlaybackTick.outputs:tick", "PublishTF.inputs:execIn"),
                    ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),
                    ("SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
                    ("SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
                ],
                keys.SET_VALUES: [
                    ("PublishJointState.inputs:topicName", "/joint_states"),
                    ("PublishTF.inputs:topicName", "/tf"),
                    ("SubscribeJointState.inputs:topicName", "/joint_commands"),
                ],
            },
        )
        set_target_prims(primPath="/ActionGraph/PublishJointState", targetPrimPaths=["/World/Piper"])
        set_target_prims(primPath="/ActionGraph/PublishTF", targetPrimPaths=["/World/Piper", "/World/G29"])
        set_target_prims(primPath="/ActionGraph/ArticulationController", targetPrimPaths=["/World/Piper"])

    def _configure_physics(self):
        stage = omni.usd.get_context().get_stage()
        for i in range(1, 7):
            joint_prim = stage.GetPrimAtPath(f"/World/Piper/joint{i}")
            if joint_prim.IsValid():
                drive = UsdPhysics.DriveAPI.Apply(joint_prim, "angular")
                drive.GetStiffnessAttr().Set(400.0)
                drive.GetDampingAttr().Set(80.0)
                drive.GetMaxForceAttr().Set(100.0)

    def run(self):
        self._world.reset()
        self._world.play() # Start physics automatically
        print("Simulation Started: ROS 2 Humble Linked & Playing.")
        while simulation_app.is_running():
            self._world.step(render=True)
            # Export state for visualizer
            if self._world.is_playing():
                import json
                pos = self._piper.get_joint_positions()
                world_pos, _ = self._piper.get_world_pose()
                # Simple approximation of end-effector for visualization
                gripper_xyz = [float(world_pos[0]), float(world_pos[1] + 0.15), float(world_pos[2] + 0.7)]
                
                state = {
                    "phase": "ROS 2 Humble Active",
                    "gripper_pos": float(abs(pos[6]-pos[7])*1000) if len(pos)>7 else 0.0,
                    "gripper_xyz": gripper_xyz,
                    "wheel_angle": float(np.degrees(self._g29.get_joint_positions()[0])) if self._g29 else 0.0,
                    "is_gripping": abs(pos[6]-pos[7]) < 0.03,
                    "ros_mode": "Humble (Active)"
                }
                with open('system_state_telemetry.json', 'w') as f:
                    json.dump(state, f)
        simulation_app.close()

if __name__ == "__main__":
    sim = SteeringSimulationBackend()
    sim.run()
