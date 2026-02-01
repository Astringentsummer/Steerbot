#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math
import time

class KinematicInputSimulator(Node):
    def __init__(self):
        super().__init__('kinematic_input_simulator')
        self.publisher = self.create_publisher(Float32, '/wheel/steering_angle', 10)
        self.timer = self.create_timer(0.05, self.generate_periodic_signal)
        self.start_time = time.time()
        
        # Operational limits (±450 degrees in radians)
        self.limit_rad = 450 * math.pi / 180.0
        
        self.get_logger().info('Initialized Kinematic Input Simulator: Generating periodic steering signal...')

    def generate_periodic_signal(self):
        elapsed = time.time() - self.start_time
        
        # Periodic waveform to simulate continuous steering interaction
        angle = self.limit_rad * math.sin(0.4 * elapsed)
        
        msg = Float32()
        msg.data = angle
        self.publisher.publish(msg)
        
        # Log to terminal for proof
        deg = angle * 180 / math.pi
        if int(elapsed * 2) % 10 == 0:
            self.get_logger().info(f'Virtual Steering: {deg:.1f}°')

def main(args=None):
    rclpy.init(args=args)
    node = KinematicInputSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
