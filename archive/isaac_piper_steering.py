import os
import sys
import numpy as np
import time

# Set Isaac Sim standalone path
# Adjust this to the user's correct path
isaac_path = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.append(os.path.join(isaac_path, "exts", "isaacsim.simulation_app"))

from isaacsim.simulation_app import SimulationApp

def run_simulation():
    # 1. Startup
    simulation_app = SimulationApp({"headless": False})
    
    try:
        import carb
        from isaacsim.core.api import World
        from isaacsim.core.api.objects import DynamicCuboid, FixedCuboid, DynamicCylinder
        from isaacsim.core.utils.extensions import enable_extension
        from isaacsim.core.utils.prims import create_prim
        from isaacsim.core.utils.viewports import set_camera_view
        from isaacsim.core.utils.stage import get_current_stage
        from isaacsim.core.utils.xforms import get_world_pose
        from isaacsim.core.api.prims import XFormPrim
        import omni.physx.scripts.utils as physx_utils
        from scipy.spatial.transform import Rotation as R
        import socket
        import json
        import threading

        # Enable extensions
        enable_extension("isaac_sim.asset.importer.urdf")
        enable_extension("isaac_sim.robot_motion.motion_generation")
        enable_extension("omni.isaac.ros2_bridge")
        
        from isaac_sim.asset.importer.urdf import _urdf
        from isaac_sim.robot_motion.motion_generation.lula.kinematics import LulaKinematicsSolver
        from isaac_sim.robot_motion.motion_generation.articulation_kinematics_solver import ArticulationKinematicsSolver

        # --- UDP BRIDGE (LISTEN) ---
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005
        shared_data = {"steer": 0.0}

        def udp_listener():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, UDP_PORT))
            sock.setblocking(False)
            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    shared_data["steer"] = json.loads(data.decode('utf-8'))["steer"]
                except:
                    pass
        
        t = threading.Thread(target=udp_listener, daemon=True)
        t.start()

        # --- SCENE SETUP ---
        world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
        world.scene.add_default_ground_plane()

        # Lighting
        create_prim("/World/Light", "DistantLight", attributes={"inputs:intensity": 5000.0})

        # --- IMPORT PIPER ---
        package_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/urdf"
        urdf_file = os.path.join(package_path, "piper_arm.urdf")
        
        import_config = _urdf.ImportConfig()
        import_config.merge_fixed_joints = False
        import_config.fix_base = True
        
        status, prim_path = omni.kit.commands.execute("URDFParseAndImportFile", urdf_path=urdf_file, import_config=import_config)
        
        from isaacsim.core.api.articulations import Articulation
        piper_arm = Articulation(prim_path=prim_path)
        world.scene.add(piper_arm)
        
        # --- ATTACH GRIPPER ---
        # Fixed box for now to represent the gripper
        gripper_base = world.scene.add(DynamicCuboid("/World/Gripper", name="gripper", scale=np.array([0.15, 0.1, 0.05]), mass=0.1))
        wrist_path = f"{prim_path}/link6"
        
        # --- STEERING WHEEL ---
        wheel_pos = np.array([0.4, 0.0, 0.2])
        # 45 deg tilt
        q_tilt = R.from_euler('y', 45, degrees=True).as_quat()
        q_isaac = np.array([q_tilt[3], q_tilt[0], q_tilt[1], q_tilt[2]])
        
        wheel_hub = world.scene.add(FixedCuboid("/World/Wheel/Hub", position=wheel_pos, orientation=q_isaac, scale=np.array([0.05, 0.05, 0.05])))
        wheel_rim = world.scene.add(DynamicCylinder("/World/Wheel/Rim", position=wheel_pos, orientation=q_isaac, radius=0.16, height=0.04, mass=0.5))
        
        stage = get_current_stage()
        physx_utils.createJoint(stage, "Revolute", stage.GetPrimAtPath("/World/Wheel/Hub"), stage.GetPrimAtPath("/World/Wheel/Rim"))
        wheel_joint = stage.GetPrimAtPath("/World/Wheel/Hub/RevoluteJoint")
        
        from pxr import UsdPhysics
        drive = UsdPhysics.DriveAPI.Apply(wheel_joint, "angular")
        drive.CreateTypeAttr("position")
        drive.CreateStiffnessAttr(1000.0)
        
        # --- IK ---
        descriptor_path = os.path.join(os.getcwd(), "piper_descriptor.yaml")
        lula_solver = LulaKinematicsSolver(descriptor_path, urdf_file)
        ik_solver = ArticulationKinematicsSolver(piper_arm, lula_solver, "link6")

        # --- ROS2 BRIDGE (JOINT STATES) ---
        import omni.graph.core as og
        try:
            keys = og.Controller.Keys
            og.Controller.edit(
                {"graph_path": "/ROS_Bridge", "evaluator_name": "execution"},
                {
                    keys.CREATE_NODES: [
                        ("OnTick", "omni.graph.action.OnPlaybackTick"),
                        ("Publish", "omni.isaac.ros2_bridge.ROS2PublishJointState"),
                    ],
                    keys.CONNECT: [("OnTick.outputs:tick", "Publish.inputs:execIn")],
                    keys.SET_VALUES: [("Publish.inputs:targetPrim", prim_path)],
                }
            )
        except Exception as e:
            print(f"Warning: ROS2 Bridge failed: {e}")

        # --- RUN ---
        set_camera_view(eye=[1.0, 1.0, 1.2], target=wheel_pos)
        world.reset()
        
        # Initial pose
        init_pos = np.zeros(piper_arm.num_dof)
        if piper_arm.num_dof >= 3:
            init_pos[1] = 0.5
            init_pos[2] = -0.5
        piper_arm.set_joint_positions(init_pos)

        frame = 0
        while simulation_app.is_running():
            world.step(render=True)
            
            # 1. Drive Wheel
            target_deg = shared_data["steer"] * -90
            wheel_joint.GetAttribute("physics:angular:targetPosition").Set(target_deg)
            
            # 2. Get Rim Pose for IK
            rim_pos, rim_ori = get_world_pose("/World/Wheel/Rim")
            rim_rot = R.from_quat([rim_ori[1], rim_ori[2], rim_ori[3], rim_ori[0]])
            
            # Target is Top of Rim (local [0.16, 0, 0])
            offset = np.array([0, 0, -0.05]) # Safety offset
            target_pos = rim_pos + rim_rot.apply(np.array([0, 0.16, 0]) + offset)
            
            # 3. Solve IK
            action, success = ik_solver.compute_inverse_kinematics(target_position=target_pos)
            if action:
                piper_arm.get_articulation_controller().apply_action(action)
                # Attach visual gripper box to wrist
                w_pos, w_ori = get_world_pose(wrist_path)
                gripper_base.set_world_pose(w_pos, w_ori)
                
            if frame % 60 == 0:
                print(f"Frame {frame} | Steer: {target_deg:.1f} | IK: {'OK' if success else 'SEARCH'}")
            frame += 1

    except Exception as e:
        import traceback
        error_msg = f"CRITICAL SIMULATION ERROR:\n{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("sim_crash_log.txt", "w") as f:
            f.write(error_msg)
    finally:
        simulation_app.close()

if __name__ == "__main__":
    run_simulation()
