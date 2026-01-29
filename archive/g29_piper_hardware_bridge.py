#!/usr/bin/env python3
"""
REAL HARDWARE BRIDGE - G29 to Piper Arm
Connects physical G29 wheel to real Piper arm via ROS2
"""

import socket
import json
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import numpy as np

class G29PiperBridge(Node):
    """Bridge between G29 wheel and Piper arm"""
    
    def __init__(self):
        super().__init__('g29_piper_bridge')
        
        # Publishers
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/piper/joint_commands',
            10
        )
        
        # Subscribers
        self.joint_sub = self.create_subscription(
            JointState,
            '/piper/joint_states',
            self.joint_callback,
            10
        )
        
        # UDP socket for G29 input
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 5006))
        self.sock.settimeout(0.01)  # Non-blocking
        
        # State
        self.current_joints = [0.0] * 6
        self.steering_angle = 0.0
        
        # Timer for control loop
        self.timer = self.create_timer(0.016, self.control_loop)  # 60 Hz
        
        self.get_logger().info('G29-Piper bridge started')
        self.get_logger().info('Listening for G29 on UDP port 5006')
    
    def joint_callback(self, msg):
        """Update current joint positions"""
        self.current_joints = list(msg.position)
    
    def simple_ik(self, target_x, target_y):
        """Simple 2-DOF IK for testing"""
        L1 = 0.2
        L2 = 0.2
        
        r = np.clip(np.sqrt(target_x**2 + target_y**2), 0.05, L1 + L2 - 0.05)
        theta = np.arctan2(target_y, target_x)
        cos_q2 = np.clip((r**2 - L1**2 - L2**2) / (2 * L1 * L2), -1, 1)
        q2 = np.arccos(cos_q2)
        beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
        q1 = theta - beta
        
        return [q1, q2, 0, 0, 0, 0]
    
    def control_loop(self):
        """Main control loop"""
        try:
            # Receive G29 data
            data, addr = self.sock.recvfrom(1024)
            g29_data = json.loads(data.decode())
            
            # Extract steering angle (-1 to +1)
            self.steering_angle = g29_data.get('steering', 0.0)
            
            # Compute target position
            target_x = 0.3
            target_y = self.steering_angle * 0.2
            
            # Compute IK
            joint_positions = self.simple_ik(target_x, target_y)
            
            # Publish to Piper
            msg = Float64MultiArray()
            msg.data = joint_positions
            self.joint_pub.publish(msg)
            
            # Log
            self.get_logger().info(
                f'Steer: {self.steering_angle:+.2f} | '
                f'Target: ({target_x:.2f}, {target_y:.2f}) | '
                f'Joints: {[f"{np.degrees(j):.1f}°" for j in joint_positions[:2]]}'
            )
            
        except socket.timeout:
            pass  # No data available
        except Exception as e:
            self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    bridge = G29PiperBridge()
    
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    finally:
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
