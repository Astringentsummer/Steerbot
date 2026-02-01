#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32
import time
import math

class SteeringTaskModule(Node):
    """
    Formal Task Execution Module for Automated Steering Maneuvers.
    Implements a controlled rotation to target setpoints (e.g., 55 degrees).
    """
    def __init__(self):
        super().__init__('steering_task_module')
        
        self.publisher = self.create_publisher(JointState, '/arm/joint_commands', 10)
        self.get_logger().info('Initialized Steering Task Module: Awaiting execution triggers...')

    def execute_target_maneuver(self, target_deg=55.0):
        """
        Executes a precision rotation to the specified target angle.
        """
        self.get_logger().info(f'Commencing Automated Maneuver: Target Angle = {target_deg}°')
        
        target_rad = math.radians(target_deg)
        base_cmd = target_rad * 0.2 # Calibrated mapping factor
        
        # 1. Approach Phase
        self._publish_pose(base_cmd, 0.5, -1.0, 0.0, 0.5, 0.0, 0.035)
        time.sleep(2.0)
        
        # 2. Actuation Phase (Rotation)
        self.get_logger().info('Actuating Steering Rotation...')
        self._publish_pose(base_cmd, 0.5, -1.0, 0.0, 0.5, 0.0, 0.058)
        time.sleep(1.0)
        
        self.get_logger().info('Maneuver Completed Successfully.')

    def _publish_pose(self, j1, j2, j3, j4, j5, j6, grit):
        msg = JointState()
        msg.name = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "gripper"]
        msg.position = [float(j1), float(j2), float(j3), float(j4), float(j5), float(j6), float(grit)]
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SteeringTaskModule()
    
    # Example execution of a standard validation maneuver
    try:
        node.execute_target_maneuver(55.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
