#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32
import math
import numpy as np

class SteeringSignalBridge(Node):
    def __init__(self):
        super().__init__('steering_signal_bridge')
        
        # Subscribes to the G29 steering input stream
        self.subscription = self.create_subscription(
            Float32,
            '/wheel/steering_angle',
            self.input_mapping_callback,
            10)
            
        # Publishes kinematic commands to the simulation backend
        self.publisher = self.create_publisher(
            JointState,
            '/arm/joint_commands',
            10)
            
        self.get_logger().info('Initialized Steering Signal Bridge: Monitoring input stream...')

    def input_mapping_callback(self, msg):
        steering_rad = msg.data
        
        # Mapping the steering wheel rotation to the Piper Arm's Base Joint
        # G29 usually gives ±450°, we map this to a reasonable arm range
        # base_rotation = steering_rad / 5.0 (scale down for precision)
        
        base_cmd = steering_rad * 0.2 # Tune this factor for sensitivity
        
        joint_state = JointState()
        joint_state.name = [
            "joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "gripper"
        ]
        
        # Example: Base follows wheel, arm stays in a neutral "driving" pose
        joint_state.position = [
            float(base_cmd),  # Joint 1: Base rotation
            0.5,              # Joint 2: Shoulder tilted forward
            -1.0,             # Joint 3: Elbow
            0.0,              # Joint 4: Wrist roll
            0.5,              # Joint 5: Wrist pitch
            0.0,              # Joint 6: Wrist yaw
            0.058             # Gripper: Firmly closed on the rim
        ]
        
        self.publisher.publish(joint_state)

def main(args=None):
    rclpy.init(args=args)
    node = SteeringSignalBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
