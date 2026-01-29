#!/usr/bin/env python3
"""
SIMPLIFIED VERSION: Piper Gripper Controls G29 Wheel
No UDP socket - just demo movement
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import numpy as np
import time

class PiperControlsG29Simple(Node):
    """Simplified Piper arm controller - no network dependencies"""
    
    def __init__(self):
        super().__init__('piper_controls_g29')
        
        # Publishers - send commands to Piper arm
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )
        
        # State
        self.target_wheel_angle = 0.0
        
        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        
        # Demo mode
        self.demo_start_time = time.time()
        
        self.get_logger().info('Piper-Controls-G29 (Simple) started')
        self.get_logger().info('Running in DEMO mode - automatic turning')
    
    def compute_grip_position(self, wheel_angle):
        """Compute gripper position to hold wheel at given angle"""
        wheel_center_x = 0.3
        wheel_center_y = 0.0
        wheel_center_z = 0.4
        grip_distance = 0.15
        
        grip_x = wheel_center_x + grip_distance * np.cos(wheel_angle)
        grip_y = wheel_center_y + grip_distance * np.sin(wheel_angle)
        grip_z = wheel_center_z
        
        return grip_x, grip_y, grip_z
    
    def simple_ik(self, target_x, target_y, target_z):
        """Simple IK for 7-DOF arm"""
        # Base rotation
        q1 = np.arctan2(target_y, target_x)
        
        # Distance
        r = np.sqrt(target_x**2 + target_y**2)
        
        # Arm lengths
        L1 = 0.25
        L2 = 0.25
        
        # 2D IK
        d = np.sqrt(r**2 + target_z**2)
        d = np.clip(d, 0.05, L1 + L2 - 0.05)
        
        cos_q3 = (d**2 - L1**2 - L2**2) / (2 * L1 * L2)
        cos_q3 = np.clip(cos_q3, -1, 1)
        q3 = np.arccos(cos_q3)
        
        alpha = np.arctan2(target_z, r)
        beta = np.arctan2(L2 * np.sin(q3), L1 + L2 * np.cos(q3))
        q2 = alpha - beta
        
        # Wrist
        q4 = 0
        q5 = -(q2 + q3)
        q6 = 0
        
        # Gripper closed
        gripper = 0.04
        
        return [q1, q2, q3, q4, q5, q6, gripper]
    
    def control_loop(self):
        """Main control loop"""
        # Demo: sine wave ±90 degrees
        elapsed = time.time() - self.demo_start_time
        self.target_wheel_angle = np.sin(elapsed * 0.5) * 1.57
        
        # Compute gripper position
        grip_x, grip_y, grip_z = self.compute_grip_position(self.target_wheel_angle)
        
        # Compute IK
        joint_positions = self.simple_ik(grip_x, grip_y, grip_z)
        
        # Publish
        msg = Float64MultiArray()
        msg.data = joint_positions
        self.joint_pub.publish(msg)
        
        # Log
        self.get_logger().info(
            f'Wheel: {np.degrees(self.target_wheel_angle):+6.1f}° | '
            f'Pos: ({grip_x:.2f}, {grip_y:.2f}, {grip_z:.2f})'
        )

def main(args=None):
    rclpy.init(args=args)
    controller = PiperControlsG29Simple()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
