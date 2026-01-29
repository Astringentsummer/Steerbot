#!/usr/bin/env python3
"""
PRODUCTION HARDWARE BRIDGE - G29 Wheel → Piper Arm
Simple, reliable, ready for company testing
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import socket
import json
import numpy as np

class HardwareBridge(Node):
    """Bridge between G29 wheel and Piper arm"""
    
    def __init__(self):
        super().__init__('hardware_bridge')
        
        # ROS2 Publishers
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/piper_interface/joint_command',
            10
        )
        
        # ROS2 Subscribers
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )
        
        # UDP for G29 input
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 5006))
        self.sock.settimeout(0.01)
        
        # State
        self.current_joints = [0.0] * 7
        self.g29_steering = 0.0
        self.g29_throttle = 0.0
        self.g29_brake = 0.0
        
        # Control timer
        self.timer = self.create_timer(0.05, self.control_loop)  # 20 Hz
        
        self.get_logger().info('=== HARDWARE BRIDGE READY ===')
        self.get_logger().info('Listening for G29 on UDP port 5006')
        self.get_logger().info('Publishing to /piper_interface/joint_command')
        self.get_logger().info('Turn the G29 wheel to control Piper arm')
    
    def joint_callback(self, msg):
        """Receive current joint positions from Piper"""
        if len(msg.position) >= 7:
            self.current_joints = list(msg.position[:7])
    
    def control_loop(self):
        """Main control loop - read G29, command Piper"""
        
        # Read G29 input
        try:
            data, addr = self.sock.recvfrom(1024)
            g29_data = json.loads(data.decode())
            self.g29_steering = g29_data.get('steering', 0.0)
            self.g29_throttle = g29_data.get('throttle', 0.0)
            self.g29_brake = g29_data.get('brake', 0.0)
        except socket.timeout:
            pass  # No new data
        except Exception as e:
            self.get_logger().warn(f'G29 read error: {e}')
        
        # Map steering to arm position
        # Steering: -1 (left) to +1 (right)
        # Map to joint angles
        
        # Simple mapping: steering controls base rotation
        base_angle = self.g29_steering * 1.57  # ±90 degrees
        
        # Throttle/brake control arm extension
        extension = (self.g29_throttle - self.g29_brake) * 0.5
        
        # Compute target joints
        target_joints = [
            base_angle,           # Joint 0: Base rotation
            0.5 + extension,      # Joint 1: Shoulder
            -0.5 - extension,     # Joint 2: Elbow
            0.0,                  # Joint 3: Wrist 1
            0.0,                  # Joint 4: Wrist 2
            0.0,                  # Joint 5: Wrist 3
            0.04                  # Joint 6: Gripper (closed)
        ]
        
        # Publish command
        msg = Float64MultiArray()
        msg.data = target_joints
        self.joint_pub.publish(msg)
        
        # Log status
        self.get_logger().info(
            f'G29: Steering={self.g29_steering:+.2f} | '
            f'Throttle={self.g29_throttle:.2f} | '
            f'Brake={self.g29_brake:.2f} | '
            f'Base={np.degrees(base_angle):+.1f}°'
        )

def main(args=None):
    rclpy.init(args=args)
    bridge = HardwareBridge()
    
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    finally:
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
