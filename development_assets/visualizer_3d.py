import json
import time
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# ==============================================================================
# 3D GRAPHICAL TELEMETRY VISUALIZER (Matplotlib Edition)
# ==============================================================================

STATE_FILE = "digital_twin_state.json"

class Visualizer3D:
    def __init__(self):
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.canvas.manager.set_window_title('HICTP | 3D Digital Twin Visualizer')

        self.ax.set_xlim([-0.3, 0.3])
        self.ax.set_ylim([-0.3, 0.3])
        self.ax.set_zlim([0.5, 1.2])
        self.ax.set_xlabel("X (meters)")
        self.ax.set_ylabel("Y (meters)")
        self.ax.set_zlabel("Z (meters)")
        self.ax.set_title("3D Gripper + G29 Steering Wheel Simulation", fontweight='bold')

        # 1. Pre-allocate Steering Wheel (Rim + Hub)
        theta = np.linspace(0, 2*np.pi, 50)
        # Rim
        self.wheel_line, = self.ax.plot(0.15*np.cos(theta), 0.15*np.sin(theta), np.full(50, 0.7), color='blue', lw=5, alpha=0.3)
        # Center Hub (Middle Circle)
        self.hub_line, = self.ax.plot(0.04*np.cos(theta), 0.04*np.sin(theta), np.full(50, 0.71), color='blue', lw=3, alpha=0.3)
        # Spokes
        self.spokes = [self.ax.plot([0.04*np.cos(a), 0.15*np.cos(a)], [0.04*np.sin(a), 0.15*np.sin(a)], [0.705, 0.705], color='blue', lw=3, alpha=0.3)[0] for a in [0, 2*np.pi/3, -2*np.pi/3]]
        
        # 2. Pre-allocate Gripper Jaws
        self.jaw_lines_links = []
        for _ in range(24):
            line, = self.ax.plot([0,0], [0,0], [0.95,0.95], color='green', lw=2, alpha=0.3)
            self.jaw_lines_links.append(line)
        
        # 3. Telemetry Overlay (TOP-LEFT CORNER)
        self.text_box = self.ax.text2D(0.02, 0.98, "STATUS: WAITING FOR BRIDGE...", transform=self.ax.transAxes, 
                                     fontsize=10, verticalalignment='top',
                                     bbox=dict(facecolor='wheat', alpha=0.8, boxstyle='round,pad=0.5'))

    def update_prism(self, lines_slice, center, size, active=True):
        w, h, d = size
        x, y, z = center
        v = np.array([
            [x-w/2, y-h/2, z-d/2], [x+w/2, y-h/2, z-d/2], [x+w/2, y+h/2, z-d/2], [x-w/2, y+h/2, z-d/2],
            [x-w/2, y-h/2, z+d/2], [x+w/2, y-h/2, z+d/2], [x+w/2, y+h/2, z+d/2], [x-w/2, y+h/2, z+d/2]
        ])
        edges = [[0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4], [0,4], [1,5], [2,6], [3,7]]
        for i, edge in enumerate(edges):
            pts = v[edge]
            lines_slice[i].set_data(pts[:,0], pts[:,1])
            lines_slice[i].set_3d_properties(pts[:,2])
            lines_slice[i].set_alpha(1.0 if active else 0.3)

    def update(self, frame):
        # Always return all artists to keep them visible
        all_artists = [self.wheel_line, self.hub_line, self.text_box] + self.spokes + self.jaw_lines_links
        
        try:
            if not os.path.exists(STATE_FILE):
                self.text_box.set_text("Phase: Waiting\nConnecting to G29...\n\nStatus: OFFLINE")
                return all_artists

            with open(STATE_FILE, 'r') as f:
                data = json.load(f)

            wheel_angle = data.get("wheel_angle", 0.0)
            gripper_pos = data.get("gripper_pos", 58.6)
            gripper_xyz = data.get("gripper_xyz", [0.0, 0.15, 0.70])
            phase = data.get("phase", "Grasping")
            is_gripping = "YES" if data.get("is_gripping", False) else "NO"

            # 1. Update Wheel Visuals (Rim + Hub)
            theta = np.linspace(0, 2*np.pi, 50)
            phi = np.deg2rad(wheel_angle)
            
            self.wheel_line.set_data(0.15 * np.cos(theta), 0.15 * np.sin(theta))
            self.wheel_line.set_3d_properties(np.full(50, 0.7))
            self.wheel_line.set_alpha(1.0)
            
            self.hub_line.set_data(0.04 * np.cos(theta), 0.04 * np.sin(theta))
            self.hub_line.set_3d_properties(np.full(50, 0.71))
            self.hub_line.set_alpha(1.0)

            # 2. Update Spokes (Rotating)
            for i, sa in enumerate([phi, phi + 2*np.pi/3, phi - 2*np.pi/3]):
                self.spokes[i].set_data([0.04*np.cos(sa), 0.15*np.cos(sa)], [0.04*np.sin(sa), 0.15*np.sin(sa)])
                self.spokes[i].set_3d_properties([0.705, 0.705])
                self.spokes[i].set_alpha(1.0)

            # 3. Update Gripper Visuals (ALWAYS VISIBLE with state-based coloring)
            gap = (gripper_pos / 1000.0) / 2.0
            size = [0.02, 0.08, 0.15]
            is_gripping_bool = data.get("is_gripping", False)
            
            # Change color based on gripping state
            gripper_color = 'green' if is_gripping_bool else 'red'
            gripper_alpha = 1.0  # Always fully visible
            
            # Update jaw colors - FORCE visibility
            for line in self.jaw_lines_links:
                line.set_color(gripper_color)
                line.set_alpha(gripper_alpha)
                line.set_linewidth(3)  # Make thicker
            
            # Always show gripper (active=True)
            self.update_prism(self.jaw_lines_links[0:12], [gripper_xyz[0]-gap, gripper_xyz[1], gripper_xyz[2]], size, active=True)
            self.update_prism(self.jaw_lines_links[12:24], [gripper_xyz[0]+gap, gripper_xyz[1], gripper_xyz[2]], size, active=True)

            # 4. Update Overlay
            info_text = (f"Phase: {phase}\n"
                        f"Gripper: {gripper_pos:.1f}mm\n"
                        f"Wheel Angle: {wheel_angle:.1f}\xb0\n"
                        f"Gripping: {is_gripping}\n\n"
                        f"ROS2: Demo Mode")
            self.text_box.set_text(info_text)

        except Exception as e:
            self.text_box.set_text(f"Sync Error: {str(e)[:20]}")
            
        return all_artists

if __name__ == "__main__":
    viz = Visualizer3D()
    # Using blit=False for better stability on Windows 3D plots
    ani = FuncAnimation(viz.fig, viz.update, interval=30, blit=False, cache_frame_data=False)
    plt.show()
