#!/usr/bin/env python3
"""
ROS2-Compatible Gripper Node for Windows (Without ROS2)

This version runs on Windows WITHOUT needing ROS2 installed.
It simulates the ROS2 interface for testing.

For REAL ROS2 integration, use ros2_gripper_node.py in WSL.

Usage:
  python ros2_gripper_node_windows.py
"""

import sys
import os
import time
import threading

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from gripper_interface import Gripper
except ImportError as e:
    print(f"ERROR: Could not import Gripper: {e}")
    print(f"Make sure gripper_interface.py is in: {current_dir}")
    sys.exit(1)


class MockROS2GripperNode:
    """Mock ROS2 node for Windows testing (no ROS2 required)"""
    
    def __init__(self):
        print("=" * 80)
        print("MOCK ROS2 GRIPPER NODE (Windows)")
        print("=" * 80)
        print("\nNOTE: This is a simulation - no real ROS2 topics.")
        print("For REAL ROS2, install it in WSL and use ros2_gripper_node.py")
        print("=" * 80)
        
        # Initialize gripper
        print("\nInitializing gripper controller...")
        self.gripper = Gripper()
        print(f"Gripper initialized: {type(self.gripper._piper).__name__}")
        
        # Gripper state
        self.current_position = 0.0  # mm
        self.target_speed = 1000
        self.running = True
        
        # Start state publisher thread
        self.publisher_thread = threading.Thread(target=self._publish_loop, daemon=True)
        self.publisher_thread.start()
        
        print("\n" + "=" * 80)
        print("MOCK ROS2 NODE READY")
        print("=" * 80)
        print("\nSimulated Topics:")
        print("  /gripper/command - Send position commands")
        print("  /gripper/speed - Set speed")
        print("  /gripper/state - Current position (auto-published)")
        print("  /gripper/status - Status messages")
        print("\n" + "=" * 80)
        print("\nCommands:")
        print("  Type position (0-100) and press Enter")
        print("  Type 'speed <value>' to change speed")
        print("  Type 'quit' to exit")
        print("=" * 80 + "\n")
    
    def send_command(self, position: float):
        """Send position command to gripper"""
        position = max(0.0, min(100.0, position))
        
        print(f"\n[COMMAND] Moving to {position}mm at speed {self.target_speed}")
        
        try:
            self.gripper.close_to(position, speed=self.target_speed)
            self.current_position = position
            print(f"[STATUS] ✓ Moved to {position}mm")
        except Exception as e:
            print(f"[ERROR] Failed to move gripper: {e}")
    
    def set_speed(self, speed: int):
        """Set gripper speed"""
        speed = max(1, min(1000, speed))
        self.target_speed = speed
        print(f"[STATUS] Speed set to {speed}")
    
    def _publish_loop(self):
        """Periodically 'publish' gripper state"""
        while self.running:
            # In real ROS2, this would publish to /gripper/state topic
            time.sleep(1.0)
    
    def run_interactive(self):
        """Run interactive command loop"""
        try:
            while self.running:
                try:
                    user_input = input("gripper> ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() == 'quit':
                        print("\nShutting down...")
                        break
                    
                    if user_input.lower().startswith('speed '):
                        try:
                            speed = int(user_input.split()[1])
                            self.set_speed(speed)
                        except (ValueError, IndexError):
                            print("[ERROR] Invalid speed. Usage: speed <1-1000>")
                        continue
                    
                    # Try to parse as position
                    try:
                        position = float(user_input)
                        self.send_command(position)
                    except ValueError:
                        print("[ERROR] Invalid command. Type a number (0-100) or 'speed <value>'")
                
                except KeyboardInterrupt:
                    print("\n\nShutting down...")
                    break
        
        finally:
            self.running = False
            print("\nGripper node stopped")


def main():
    """Main entry point"""
    print("Starting Windows-compatible gripper node...\n")
    
    try:
        node = MockROS2GripperNode()
        node.run_interactive()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
