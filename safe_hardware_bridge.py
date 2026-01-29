#!/usr/bin/env python3
"""
SAFE HARDWARE BRIDGE - Production Ready with Safety Checks
Only deploy after simulation test passes!
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import socket
import json
import numpy as np
import time

class SafeHardwareBridge(Node):
    """Safe bridge with rate limiting and safety checks"""
    
    def __init__(self):
        super().__init__('safe_hardware_bridge')
        
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
        self.target_joints = [0.0] * 7
        self.g29_steering = 0.0
        self.last_update = time.time()
        
        # SAFETY: Joint limits (radians)
        self.joint_limits = [
            (-3.14, 3.14),   # Base
            (-1.57, 1.57),   # Shoulder
            (-2.0, 2.0),     # Elbow
            (-1.57, 1.57),   # Wrist 1
            (-1.57, 1.57),   # Wrist 2
            (-1.57, 1.57),   # Wrist 3
            (0.0, 0.08)      # Gripper
        ]
        
        # SAFETY: Maximum speed (rad/s)
        self.max_speed = 1.0  # 57°/s - SAFE SPEED
        
        # Control timer (20 Hz)
        self.timer = self.create_timer(0.05, self.control_loop)
        
        self.get_logger().info('=' * 60)
        self.get_logger().info(' SAFE HARDWARE BRIDGE - READY')
        self.get_logger().info('=' * 60)
        self.get_logger().info('Safety features enabled:')
        self.get_logger().info('  - Joint limits enforced')
        self.get_logger().info('  - Speed limiting (57 degrees/s max)')
        self.get_logger().info('  - Smooth rate limiting')
        self.get_logger().info('Listening for G29 on UDP port 5006')
        self.get_logger().info('=' * 60)
    
    def joint_callback(self, msg):
        """Receive current joint positions from Piper"""
        if len(msg.position) >= 7:
            self.current_joints = list(msg.position[:7])
    
    def clamp_to_limits(self, joints):
        """SAFETY: Clamp joints to safe limits"""
        clamped = []
        for i, (joint, (min_val, max_val)) in enumerate(zip(joints, self.joint_limits)):
            clamped_val = np.clip(joint, min_val, max_val)
            if clamped_val != joint:
                self.get_logger().warn(
                    f'Joint {i} clamped from {np.degrees(joint):.1f}° '
                    f'to {np.degrees(clamped_val):.1f}°'
                )
            clamped.append(clamped_val)
        return clamped
    
    def rate_limit(self, target_joints):
        """SAFETY: Limit rate of change"""
        dt = time.time() - self.last_update
        if dt < 0.001:
            dt = 0.001
        
        max_delta = self.max_speed * dt
        
        safe_joints = []
        for current, target in zip(self.current_joints, target_joints):
            delta = target - current
            # Clamp to max speed
            if abs(delta) > max_delta:
                delta = np.sign(delta) * max_delta
            safe_joints.append(current + delta)
        
        self.last_update = time.time()
        return safe_joints
    
    def simple_ik(self, target_x, target_y):
        """Simple 2D IK for base control"""
        L1 = 0.25
        L2 = 0.25
        
        r = np.sqrt(target_x**2 + target_y**2)
        r = np.clip(r, 0.05, L1 + L2 - 0.05)
        
        theta = np.arctan2(target_y, target_x)
        cos_q2 = (r**2 - L1**2 - L2**2) / (2 * L1 * L2)
        cos_q2 = np.clip(cos_q2, -1, 1)
        q2 = np.arccos(cos_q2)
        
        beta = np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
        q1 = theta - beta
        
        return [q1, q2]
    
    def control_loop(self):
        """Main control loop with safety"""
        
        # Read G29 input
        try:
            data, addr = self.sock.recvfrom(1024)
            g29_data = json.loads(data.decode())
            self.g29_steering = g29_data.get('steering', 0.0)
        except socket.timeout:
            pass  # No new data - keep last value
        except Exception as e:
            self.get_logger().warn(f'G29 read error: {e}')
        
        # Map steering to target position
        wheel_angle = self.g29_steering * 1.57  # ±90°
        
        wheel_center_x = 0.3
        wheel_center_y = 0.0
        grip_distance = 0.15
        
        target_x = wheel_center_x + grip_distance * np.cos(wheel_angle)
        target_y = wheel_center_y + grip_distance * np.sin(wheel_angle)
        
        # Compute IK
        ik_result = self.simple_ik(target_x, target_y)
        
        # Build target joints
        self.target_joints = [
            ik_result[0],    # Base
            ik_result[1],    # Shoulder
            -ik_result[1],   # Elbow (opposite)
            0.0,             # Wrist 1
            0.0,             # Wrist 2
            0.0,             # Wrist 3
            0.04             # Gripper (closed)
        ]
        
        # SAFETY: Clamp to limits
        self.target_joints = self.clamp_to_limits(self.target_joints)
        
        # SAFETY: Rate limit
        safe_joints = self.rate_limit(self.target_joints)
        
        # Publish command
        msg = Float64MultiArray()
        msg.data = safe_joints
        self.joint_pub.publish(msg)
        
        # Log status
        self.get_logger().info(
            f'G29: {self.g29_steering:+.2f} ({np.degrees(wheel_angle):+.1f}°) | '
            f'Base: {np.degrees(safe_joints[0]):+.1f}° | '
            f'Shoulder: {np.degrees(safe_joints[1]):+.1f}°',
            throttle_duration_sec=1.0  # Log once per second
        )

def main(args=None):
    print("\nSAFETY REMINDER:")
    print("   1. Run simulation validation first")
    print("   2. Verify zero safety violations")
    print("   3. Keep emergency stop ready")
    print("   4. Start with small movements\n")
    
    input("Press ENTER to start (Ctrl+C to cancel)...")
    
    rclpy.init(args=args)
    bridge = SafeHardwareBridge()
    
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        print("\n\nEmergency stop activated!")
    finally:
        bridge.destroy_node()
        rclpy.shutdown()
        print("Bridge stopped safely.")

if __name__ == '__main__':
    main()
