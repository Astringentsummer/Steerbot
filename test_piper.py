#!/usr/bin/env python3
"""
TEST 2: Verify ROS2 Piper connection
Run this to check if Piper arm is responding
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import time

class PiperTest(Node):
    def __init__(self):
        super().__init__('piper_test')
        
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )
        
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/piper_interface/joint_command',
            10
        )
        
        self.received_data = False
        self.data_count = 0
        
        # Timer to send test commands
        self.timer = self.create_timer(1.0, self.send_test_command)
        
        self.get_logger().info('Listening for Piper joint states...')
        self.get_logger().info('Sending test commands...')
    
    def joint_callback(self, msg):
        self.received_data = True
        self.data_count += 1
        
        if len(msg.position) >= 7:
            self.get_logger().info(
                f'Received joint states #{self.data_count}: '
                f'[{", ".join([f"{p:.2f}" for p in msg.position[:7]])}]'
            )
        else:
            self.get_logger().warn(
                f'Received {len(msg.position)} joints (expected 7)'
            )
    
    def send_test_command(self):
        # Send a simple test command (all zeros)
        msg = Float64MultiArray()
        msg.data = [0.0] * 7
        self.joint_pub.publish(msg)
        
        if not self.received_data:
            self.get_logger().warn(
                'No joint states received yet - is Piper running?'
            )

def main():
    print("=" * 60)
    print(" TEST 2: PIPER ARM ROS2 TEST")
    print("=" * 60)
    print("")
    print("This will check if Piper arm is responding via ROS2")
    print("You should see joint state messages if Piper is connected")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    rclpy.init()
    node = PiperTest()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        if node.received_data:
            print(f"TEST PASSED: Received {node.data_count} joint state messages")
            print("   Piper arm is working correctly!")
        else:
            print("TEST FAILED: No joint states received")
            print("   Check:")
            print("   1. Piper arm is powered on")
            print("   2. Piper ROS2 driver is running")
            print("   3. ROS2 topics are correct")
        print("=" * 60)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
