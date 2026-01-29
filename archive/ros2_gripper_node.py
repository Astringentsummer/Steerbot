#!/usr/bin/env python3
"""
ROS2 Gripper Control Node - Steerbot Digital Twin

This node controls the gripper (real or simulated) via ROS2 topics.
Works with both Isaac Sim and real Piper hardware.

ROS2 Topics:
  Subscribe:
    /gripper/command (std_msgs/Float32) - Target gripper position (0-100mm)
    /gripper/speed (std_msgs/Int32) - Gripper speed (1-1000)
  
  Publish:
    /gripper/state (std_msgs/Float32) - Current gripper position
    /gripper/status (std_msgs/String) - Gripper status messages
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32, String
import sys
import os

# Add current directory to path to import gripper_interface
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from gripper_interface import Gripper
except ImportError as e:
    print(f"ERROR: Could not import Gripper: {e}")
    print(f"Make sure gripper_interface.py is in: {current_dir}")
    sys.exit(1)


class GripperROS2Node(Node):
    """ROS2 node for controlling the gripper via topics"""
    
    def __init__(self):
        super().__init__('gripper_controller')
        
        # Initialize gripper (will use MockPiper if hardware not available)
        self.get_logger().info('Initializing gripper controller...')
        self.gripper = Gripper()
        self.get_logger().info(f'Gripper initialized: {type(self.gripper._piper).__name__}')
        
        # Gripper state
        self.current_position = 0.0  # mm
        self.target_speed = 1000  # default speed
        
        # Create subscribers
        self.command_sub = self.create_subscription(
            Float32,
            '/gripper/command',
            self.command_callback,
            10
        )
        
        self.speed_sub = self.create_subscription(
            Int32,
            '/gripper/speed',
            self.speed_callback,
            10
        )
        
        # Create publishers
        self.state_pub = self.create_publisher(Float32, '/gripper/state', 10)
        self.status_pub = self.create_publisher(String, '/gripper/status', 10)
        
        # Timer for publishing state (10 Hz)
        self.timer = self.create_timer(0.1, self.publish_state)
        
        self.get_logger().info('========================================')
        self.get_logger().info('ROS2 GRIPPER CONTROLLER NODE READY')
        self.get_logger().info('========================================')
        self.get_logger().info('Subscribed to:')
        self.get_logger().info('  /gripper/command (Float32) - Position 0-100mm')
        self.get_logger().info('  /gripper/speed (Int32) - Speed 1-1000')
        self.get_logger().info('Publishing:')
        self.get_logger().info('  /gripper/state (Float32) - Current position')
        self.get_logger().info('  /gripper/status (String) - Status messages')
        self.get_logger().info('========================================')
    
    def command_callback(self, msg):
        """Handle gripper position command"""
        target_pos = msg.data
        
        # Clamp to valid range
        target_pos = max(0.0, min(100.0, target_pos))
        
        self.get_logger().info(f'Command received: Move to {target_pos}mm at speed {self.target_speed}')
        
        try:
            # Send command to gripper
            self.gripper.close_to(target_pos, speed=self.target_speed)
            self.current_position = target_pos
            
            # Publish status
            status_msg = String()
            status_msg.data = f'Moved to {target_pos}mm'
            self.status_pub.publish(status_msg)
            
            self.get_logger().info(f'✓ Successfully moved to {target_pos}mm')
            
        except Exception as e:
            self.get_logger().error(f'Failed to move gripper: {str(e)}')
            status_msg = String()
            status_msg.data = f'ERROR: {str(e)}'
            self.status_pub.publish(status_msg)
    
    def speed_callback(self, msg):
        """Handle gripper speed setting"""
        speed = msg.data
        
        # Clamp to valid range
        speed = max(1, min(1000, speed))
        
        self.target_speed = speed
        self.get_logger().info(f'Speed updated to {speed}')
        
        status_msg = String()
        status_msg.data = f'Speed set to {speed}'
        self.status_pub.publish(status_msg)
    
    def publish_state(self):
        """Periodically publish gripper state"""
        state_msg = Float32()
        state_msg.data = self.current_position
        self.state_pub.publish(state_msg)


def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)
    
    try:
        node = GripperROS2Node()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\nShutting down gripper controller...')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
