import sys
import rclpy
from rclpy.node import Node

def verify_humble_stack():
    print("--- Environment Verification ---")
    print(f"Python Version: {sys.version.split()[0]}")
    
    try:
        import rclpy
        from rclpy.action import ActionServer
        print("[✓] ROS 2 Humble Core: OK")
    except ImportError:
        print("[✗] ROS 2 Humble Core: NOT FOUND")
        return

    try:
        import moveit_msgs
        import moveit_msgs.msg
        print("[✓] MoveIt 2 Messages: OK")
    except ImportError:
        print("[✗] MoveIt 2 Messages: NOT FOUND")
        return

    try:
        import numpy as np
        print(f"[✓] NumPy Version: {np.__version__}")
    except ImportError:
        print("[✗] NumPy: NOT FOUND")
        return

    print("\nCONCLUSION: Environment ready for Mission 55.")

if __name__ == "__main__":
    verify_humble_stack()
