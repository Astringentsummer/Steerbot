import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32
import math

class G29SteeringPublisher(Node):
    def __init__(self):
        super().__init__('g29_steering_publisher')
        # Subscribe to joystick topic
        self.subscription = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        # Publisher for steering angle
        self.publisher = self.create_publisher(Float32, '/wheel/steering_angle', 10)

        self.max_angle_deg = 450.0  # maximum wheel rotation
        self.get_logger().info('✅ G29 steering node started (±450°)')

    def joy_callback(self, msg):
        # Make sure axes exist
        if len(msg.axes) > 0:
            axes_value = msg.axes[0]  # left/right steering axis
            # Convert normalized (-1..1) to radians
            steering_angle_rad = -axes_value * self.max_angle_deg * math.pi / 180.0
            # Publish to topic
            self.publisher.publish(Float32(data=steering_angle_rad))

def main(args=None):
    rclpy.init(args=args)
    node = G29SteeringPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
