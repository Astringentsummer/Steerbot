import json
import os
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, ServerGoalHandle
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from typing import Any
import threading
import numpy as np
import time

class IsaacMoveItBridge(Node):
    """
    High-fidelity Bridge linking MoveIt2 trajectory planners to Isaac Sim physics.
    
    Implements a robust FollowJointTrajectory Action Server, a 
    high-frequency JointState publisher, and a Dashboard State Serializer.
    """
    
    def __init__(self, simulation_app: Any, piper_arm: Any):
        super().__init__('steerbot_moveit_bridge')
        
        self._sim_app = simulation_app
        self._arm = piper_arm
        self._lock = threading.Lock()
        self._is_holding = False
        self._phase = "STANDBY"
        
        # 1. Trajectory Action Server
        self._action_server = ActionServer(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory',
            self._on_trajectory_received
        )
        
        # 2. State & Dashboard Handlers
        self._state_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.create_timer(0.02, self._fast_update) # 50Hz precision
        
        self.get_logger().info('Academic Bridge: Operational with Dashboard Sync (50Hz)')

    def set_holding_state(self, is_holding: bool) -> None:
        """Updates the holding state detected by the physics engine."""
        self._is_holding = is_holding
        if is_holding:
            self._phase = "STEERING (CONTACT)"

    def _fast_update(self) -> None:
        """Combined callback for ROS2 publishing and JSON serialization."""
        self._publish_state()
        self._write_dashboard_json()

    def _publish_state(self) -> None:
        """Publishes the current articulation state to the ROS2 network."""
        if self._arm is None: return
        with self._lock:
            try:
                positions = self._arm.get_joint_positions()
                msg = JointState()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.name = [f"joint{i+1}" for i in range(len(positions))]
                msg.position = positions.tolist()
                self._state_pub.publish(msg)
            except Exception as e:
                self.get_logger().error(f"State Pub Error: {str(e)}")

    def _write_dashboard_json(self) -> None:
        """Serializes simulation state for the Three.js dashboard hub."""
        if self._arm is None: return
        try:
            positions = self._arm.get_joint_positions()
            # Calculate gripper width (joints 7 and 8 usually represent the parallel jaws)
            gripper_width = 0.0
            if len(positions) >= 8:
                # Assuming symmetric prismatic joints in millimeters
                gripper_width = abs(positions[6] - positions[7]) * 1000

            state = {
                "phase": self._phase,
                "gripper_width": gripper_width,
                "wheel_angle": positions[0] if len(positions) > 0 else 0.0,
                "is_holding": self._is_holding,
                "ros_mode": "MoveIt2 (Active)" if self._phase != "STANDBY" else "MoveIt2 (Ready)",
                "joints": {
                    "base": float(positions[0]),
                    "shoulder": float(positions[1]),
                    "elbow": float(positions[2])
                }
            }
            
            with open('digital_twin_state.json', 'w') as f:
                json.dump(state, f)
        except Exception:
            pass

    async def _on_trajectory_received(self, goal_handle: ServerGoalHandle) -> FollowJointTrajectory.Result:
        self.get_logger().info('MoveIt2: Executing new trajectory set...')
        self._phase = "EXECUTING"
        trajectory = goal_handle.request.trajectory
        
        if not trajectory.points:
            goal_handle.abort()
            return FollowJointTrajectory.Result()

        try:
            for point in trajectory.points:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    return FollowJointTrajectory.Result()

                with self._lock:
                    self._arm.set_joint_positions(np.array(point.positions))
                
                time.sleep(0.01) 
                
            goal_handle.succeed()
            result = FollowJointTrajectory.Result()
            result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
            self.get_logger().info('MoveIt2: Trajectory Complete.')
            return result
        except Exception as e:
            goal_handle.abort()
            return FollowJointTrajectory.Result()

def bridge_factory(sim_app: Any, arm: Any) -> IsaacMoveItBridge:
    if not rclpy.ok():
        rclpy.init()
    node = IsaacMoveItBridge(sim_app, arm)
    t = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    t.start()
    return node

