#!/usr/bin/env python3
"""
ROS2 Gripper Visualizer
Publishes gripper state to ROS2 and displays in RViz
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math
import time

class GripperVisualizer(Node):
    def __init__(self):
        super().__init__('gripper_visualizer')
        
        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # Timer for publishing (20 Hz)
        self.timer = self.create_timer(0.05, self.publish_joint_states)
        
        # Gripper state
        self.gripper_width = 0.12  # 120mm in meters
        self.steering_angle = 0.0
        self.frame_count = 0
        
        # Animation parameters
        self.phase_duration = 180  # frames
        self.phases = ["OPEN", "APPROACH", "GRASP", "STEER", "RELEASE"]
        
        self.get_logger().info('Gripper Visualizer Node Started')
        self.get_logger().info('Publishing joint states to /joint_states')
        self.get_logger().info('Open RViz2 and add RobotModel display')
        
    def publish_joint_states(self):
        # Update animation
        self.frame_count += 1
        phase_index = (self.frame_count // self.phase_duration) % len(self.phases)
        phase = self.phases[phase_index]
        
        # Update gripper state based on phase
        if phase == "OPEN":
            self.gripper_width = 0.12
            self.steering_angle = 0.0
        elif phase == "APPROACH":
            self.gripper_width = 0.12
        elif phase == "GRASP":
            target_width = 0.05
            self.gripper_width = max(target_width, self.gripper_width - 0.0015)
        elif phase == "STEER":
            self.gripper_width = 0.05
            self.steering_angle = 0.785 * math.sin(self.frame_count * 0.05)  # ±45 degrees
        elif phase == "RELEASE":
            self.gripper_width = min(0.12, self.gripper_width + 0.002)
            self.steering_angle = self.steering_angle * 0.9
        
        # Create joint state message
        joint_state = JointState()
        joint_state.header = Header()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        
        # Joint names must match URDF
        joint_state.name = [
            'left_finger_joint',
            'right_finger_joint',
            'wheel_joint'
        ]
        
        # Joint positions (in meters/radians)
        # Fingers move symmetrically from center
        finger_offset = -self.gripper_width / 2
        joint_state.position = [
            finger_offset,      # left finger
            finger_offset,      # right finger (mirrored)
            self.steering_angle # steering wheel rotation
        ]
        
        # Publish
        self.joint_pub.publish(joint_state)
        
        # Log status every 60 frames
        if self.frame_count % 60 == 0:
            self.get_logger().info(
                f'Phase: {phase:8s} | Gripper: {self.gripper_width*1000:5.1f}mm | '
                f'Steering: {math.degrees(self.steering_angle):+5.1f}°'
            )

def main(args=None):
    rclpy.init(args=args)
    
    node = GripperVisualizer()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
