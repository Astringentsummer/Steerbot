#!/usr/bin/env python3
"""
ROS2 Action Graph Setup Script for Isaac Sim.
Configures bidirectional communication between Isaac Sim and MoveIt2.
"""

import omni.graph.core as og
from omni.isaac.core_nodes.scripts.utils import set_target_prims

def create_ros2_action_graph():
    """
    Create ROS2 Action Graph for Piper-MoveIt2 integration.
    
    This graph enables:
    - Publishing joint states from Isaac Sim to MoveIt2
    - Subscribing to joint commands from MoveIt2
    - Publishing TF transforms for RViz visualization
    """
    
    # Create action graph
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
                # Joint State Publisher
                ("PublishJointState.inputs:topicName", "/joint_states"),
                ("PublishJointState.inputs:qosProfile", "SENSOR_DATA"),
                
                # Transform Tree Publisher
                ("PublishTF.inputs:topicName", "/tf"),
                
                # Joint State Subscriber
                ("SubscribeJointState.inputs:topicName", "/joint_commands"),
                ("SubscribeJointState.inputs:qosProfile", "DEFAULT"),
            ],
        },
    )
    
    # Set target prims for publishers
    set_target_prims(
        primPath="/ActionGraph/PublishJointState",
        targetPrimPaths=["/World/Piper"],
    )
    
    set_target_prims(
        primPath="/ActionGraph/PublishTF",
        targetPrimPaths=["/World/Piper", "/World/G29"],
    )
    
    # Set target prim for articulation controller
    set_target_prims(
        primPath="/ActionGraph/ArticulationController",
        targetPrimPaths=["/World/Piper"],
    )
    
    print("[ROS2 Action Graph] Configuration complete!")
    print("Topics:")
    print("  - Publishing: /joint_states (Sim -> MoveIt2)")
    print("  - Publishing: /tf (Transforms)")
    print("  - Subscribing: /joint_commands (MoveIt2 -> Sim)")
    
    return graph


def configure_joint_drives():
    """
    Configure joint drive parameters for the Piper arm.
    Sets stiffness, damping, and max force for position control.
    """
    from pxr import UsdPhysics, Usd
    
    stage = omni.usd.get_context().get_stage()
    piper_prim = stage.GetPrimAtPath("/World/Piper")
    
    if not piper_prim.IsValid():
        print("[ERROR] Piper prim not found at /World/Piper")
        return
    
    # Joint drive parameters
    drive_params = {
        "stiffness": 400.0,
        "damping": 80.0,
        "maxForce": 100.0,
    }
    
    # Apply to all arm joints
    for i in range(1, 7):  # joint1 to joint6
        joint_path = f"/World/Piper/joint{i}"
        joint_prim = stage.GetPrimAtPath(joint_path)
        
        if joint_prim.IsValid():
            drive = UsdPhysics.DriveAPI.Apply(joint_prim, "angular")
            drive.GetStiffnessAttr().Set(drive_params["stiffness"])
            drive.GetDampingAttr().Set(drive_params["damping"])
            drive.GetMaxForceAttr().Set(drive_params["maxForce"])
            print(f"[Joint Drive] Configured {joint_path}")
    
    # Gripper joints (lower stiffness)
    gripper_params = {
        "stiffness": 200.0,
        "damping": 40.0,
        "maxForce": 10.0,
    }
    
    for i in range(7, 9):  # joint7, joint8
        joint_path = f"/World/Piper/joint{i}"
        joint_prim = stage.GetPrimAtPath(joint_path)
        
        if joint_prim.IsValid():
            drive = UsdPhysics.DriveAPI.Apply(joint_prim, "linear")
            drive.GetStiffnessAttr().Set(gripper_params["stiffness"])
            drive.GetDampingAttr().Set(gripper_params["damping"])
            drive.GetMaxForceAttr().Set(gripper_params["maxForce"])
            print(f"[Joint Drive] Configured {joint_path}")
    
    print("[Joint Drives] Configuration complete!")


if __name__ == "__main__":
    print("="*80)
    print("ROS2 Action Graph Setup for Piper-MoveIt2 Integration")
    print("="*80)
    
    # Create action graph
    create_ros2_action_graph()
    
    # Configure joint drives
    configure_joint_drives()
    
    print("\n[SETUP COMPLETE]")
    print("Next steps:")
    print("1. Start ROS2: ros2 launch piper_moveit isaac_sim.launch.py")
    print("2. Run this script in Isaac Sim Script Editor")
    print("3. Press Play in Isaac Sim")
    print("4. Send commands via MoveIt2")
