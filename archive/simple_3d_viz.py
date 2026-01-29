#!/usr/bin/env python3
"""
Simple 3D Visualization - Works without RViz
Uses matplotlib for 3D plotting
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

class SimplePiperVisualizer:
    """Simple 3D visualizer for Piper arm"""
    
    def __init__(self):
        # Create figure
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Arm parameters
        self.L1 = 0.25  # Link 1 length
        self.L2 = 0.25  # Link 2 length
        
        # Demo parameters
        self.start_time = time.time()
        
        plt.ion()  # Interactive mode
        
    def compute_forward_kinematics(self, q1, q2):
        """Compute end effector position from joint angles"""
        # Joint 1 position
        x1 = self.L1 * np.cos(q1)
        y1 = self.L1 * np.sin(q1)
        z1 = 0.1
        
        # End effector position
        x2 = x1 + self.L2 * np.cos(q1 + q2)
        y2 = y1 + self.L2 * np.sin(q1 + q2)
        z2 = z1
        
        return (x1, y1, z1), (x2, y2, z2)
    
    def draw_arm(self, q1, q2, wheel_angle):
        """Draw the arm and wheel"""
        self.ax.clear()
        
        # Compute positions
        joint1_pos, ee_pos = self.compute_forward_kinematics(q1, q2)
        
        # Draw base
        self.ax.scatter([0], [0], [0], c='black', s=200, marker='o', label='Base')
        
        # Draw link 1
        self.ax.plot([0, joint1_pos[0]], 
                     [0, joint1_pos[1]], 
                     [0, joint1_pos[2]], 
                     'b-', linewidth=5, label='Link 1')
        
        # Draw joint 1
        self.ax.scatter([joint1_pos[0]], [joint1_pos[1]], [joint1_pos[2]], 
                       c='red', s=150, marker='o')
        
        # Draw link 2
        self.ax.plot([joint1_pos[0], ee_pos[0]], 
                     [joint1_pos[1], ee_pos[1]], 
                     [joint1_pos[2], ee_pos[2]], 
                     'g-', linewidth=5, label='Link 2')
        
        # Draw end effector (gripper)
        self.ax.scatter([ee_pos[0]], [ee_pos[1]], [ee_pos[2]], 
                       c='orange', s=200, marker='s', label='Gripper')
        
        # Draw virtual steering wheel
        wheel_center = (0.3, 0.0, 0.4)
        wheel_radius = 0.15
        theta = np.linspace(0, 2*np.pi, 50)
        wheel_x = wheel_center[0] + wheel_radius * np.cos(theta)
        wheel_y = wheel_center[1] + wheel_radius * np.sin(theta)
        wheel_z = np.full_like(theta, wheel_center[2])
        
        self.ax.plot(wheel_x, wheel_y, wheel_z, 'k-', linewidth=3, alpha=0.5, label='Wheel')
        
        # Draw grip point on wheel
        grip_x = wheel_center[0] + wheel_radius * np.cos(wheel_angle)
        grip_y = wheel_center[1] + wheel_radius * np.sin(wheel_angle)
        grip_z = wheel_center[2]
        self.ax.scatter([grip_x], [grip_y], [grip_z], 
                       c='red', s=150, marker='*', label='Target')
        
        # Set labels and limits
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_xlim([-0.2, 0.6])
        self.ax.set_ylim([-0.4, 0.4])
        self.ax.set_zlim([0, 0.6])
        
        # Add title with current angle
        self.ax.set_title(f'Piper Arm Controlling Wheel\nWheel Angle: {np.degrees(wheel_angle):+.1f}°', 
                         fontsize=14, fontweight='bold')
        
        self.ax.legend(loc='upper right')
        self.ax.view_init(elev=20, azim=45)
        
        plt.draw()
        plt.pause(0.01)
    
    def simple_ik(self, target_x, target_y):
        """Simple 2D IK"""
        r = np.sqrt(target_x**2 + target_y**2)
        r = np.clip(r, 0.05, self.L1 + self.L2 - 0.05)
        
        theta = np.arctan2(target_y, target_x)
        cos_q2 = (r**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        cos_q2 = np.clip(cos_q2, -1, 1)
        q2 = np.arccos(cos_q2)
        
        beta = np.arctan2(self.L2 * np.sin(q2), self.L1 + self.L2 * np.cos(q2))
        q1 = theta - beta
        
        return q1, q2
    
    def run_demo(self):
        """Run the demo"""
        print("=" * 50)
        print(" PIPER ARM 3D VISUALIZATION")
        print("=" * 50)
        print("")
        print("Watch the arm turn the virtual steering wheel!")
        print("Close the window to stop.")
        print("")
        
        try:
            while plt.fignum_exists(self.fig.number):
                # Demo: sine wave wheel turning
                elapsed = time.time() - self.start_time
                wheel_angle = np.sin(elapsed * 0.5) * 1.57  # ±90°
                
                # Compute target grip position
                wheel_center_x = 0.3
                wheel_center_y = 0.0
                grip_distance = 0.15
                
                target_x = wheel_center_x + grip_distance * np.cos(wheel_angle)
                target_y = wheel_center_y + grip_distance * np.sin(wheel_angle)
                
                # Compute IK
                q1, q2 = self.simple_ik(target_x, target_y)
                
                # Draw
                self.draw_arm(q1, q2, wheel_angle)
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        plt.close()
        print("Demo complete!")

if __name__ == '__main__':
    viz = SimplePiperVisualizer()
    viz.run_demo()
