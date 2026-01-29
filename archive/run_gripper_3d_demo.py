#!/usr/bin/env python3
"""
3D Interactive Gripper Visualization using Matplotlib
Shows gripper grasping and steering a wheel in 3D with interactive rotation
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from gripper_interface import Gripper

print("="*70)
print("  3D INTERACTIVE GRIPPER VISUALIZATION")
print("="*70)
print("\nFeatures:")
print("  • Interactive 3D rotation (drag with mouse)")
print("  • Real-time gripper animation")
print("  • 5-phase operation cycle")
print("  • Force visualization")
print("\nControls:")
print("  • Left mouse: Rotate view")
print("  • Right mouse: Zoom")
print("  • Middle mouse: Pan")
print("  • Close window to exit")
print("="*70 + "\n")

# Initialize gripper
gripper = Gripper('can0')
gripper.configure_for_first_use()

# Animation parameters
PHASE_DURATION = 60  # frames per phase
phases = ["OPEN", "APPROACH", "GRASP", "STEER", "RELEASE"]

# Gripper state
gripper_width = 120.0  # mm
steering_angle = 0.0  # degrees
current_force = 0.0

def create_box(center, size, color='blue', alpha=0.7):
    """Create a 3D box (cuboid) for visualization"""
    x, y, z = center
    dx, dy, dz = size
    
    # Define the 8 vertices of the box
    vertices = np.array([
        [x-dx/2, y-dy/2, z-dz/2],
        [x+dx/2, y-dy/2, z-dz/2],
        [x+dx/2, y+dy/2, z-dz/2],
        [x-dx/2, y+dy/2, z-dz/2],
        [x-dx/2, y-dy/2, z+dz/2],
        [x+dx/2, y-dy/2, z+dz/2],
        [x+dx/2, y+dy/2, z+dz/2],
        [x-dx/2, y+dy/2, z+dz/2]
    ])
    
    # Define the 6 faces
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[0], vertices[3], vertices[7], vertices[4]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]]
    ]
    
    return Poly3DCollection(faces, alpha=alpha, facecolor=color, edgecolor='black', linewidths=0.5)

def create_wheel(center, radius, thickness, angle=0, color='black', alpha=0.8):
    """Create a steering wheel (torus-like shape)"""
    x, y, z = center
    
    # Create wheel as a thick circle
    theta = np.linspace(0, 2*np.pi, 50)
    
    # Rotate wheel based on steering angle
    angle_rad = np.radians(angle)
    
    # Outer rim
    rim_x = x + radius * np.cos(theta)
    rim_y = y + radius * np.sin(theta) * np.cos(angle_rad)
    rim_z = z + radius * np.sin(theta) * np.sin(angle_rad)
    
    # Create wheel as collection of segments
    vertices = []
    for i in range(len(theta)-1):
        # Create rectangular segments
        v1 = [rim_x[i], rim_y[i], rim_z[i] - thickness/2]
        v2 = [rim_x[i+1], rim_y[i+1], rim_z[i+1] - thickness/2]
        v3 = [rim_x[i+1], rim_y[i+1], rim_z[i+1] + thickness/2]
        v4 = [rim_x[i], rim_y[i], rim_z[i] + thickness/2]
        vertices.append([v1, v2, v3, v4])
    
    return Poly3DCollection(vertices, alpha=alpha, facecolor=color, edgecolor='darkgray', linewidths=0.3)

def create_force_indicator(force_percent, position, color_low='green', color_high='red'):
    """Create a sphere to indicate force level"""
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    
    radius = 10 + force_percent * 5  # Size increases with force
    x = position[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = position[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = position[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Color interpolation
    r = force_percent
    g = 1 - force_percent
    color = (r, g, 0)
    
    return x, y, z, color

# Set up the figure and 3D axis
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Set up the plot limits
ax.set_xlim([-200, 200])
ax.set_ylim([-200, 200])
ax.set_zlim([0, 400])
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.set_title('3D Gripper Simulation - Interactive View', fontsize=14, fontweight='bold')

# Add grid
ax.grid(True, alpha=0.3)

# Text annotations
phase_text = ax.text2D(0.05, 0.95, '', transform=ax.transAxes, fontsize=12, 
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
status_text = ax.text2D(0.05, 0.85, '', transform=ax.transAxes, fontsize=10,
                        verticalalignment='top', family='monospace')

frame_count = 0

def update(frame):
    global gripper_width, steering_angle, current_force, frame_count
    
    frame_count += 1
    ax.clear()
    
    # Determine current phase
    phase_index = (frame // PHASE_DURATION) % len(phases)
    phase = phases[phase_index]
    
    # Update gripper state based on phase
    if phase == "OPEN":
        gripper_width = 120.0
        current_force = 0.0
        steering_angle = 0.0
        
    elif phase == "APPROACH":
        gripper_width = 120.0
        current_force = 0.0
        
    elif phase == "GRASP":
        target_width = 50.0
        gripper_width = max(target_width, gripper_width - 1.5)
        current_force = min(100, (120 - gripper_width) / (120 - target_width) * 100)
        
    elif phase == "STEER":
        gripper_width = 50.0
        current_force = 85.0
        steering_angle = 45 * np.sin(frame * 0.1)
        
    elif phase == "RELEASE":
        gripper_width = min(120.0, gripper_width + 2.0)
        current_force = max(0, current_force - 3.0)
        steering_angle = steering_angle * 0.9
    
    # Send command to gripper interface
    gripper.close_to(gripper_width, speed=1000, timeout=0.01)
    
    # Draw gripper base (gray metallic)
    base = create_box([0, 0, 250], [80, 50, 30], color='gray', alpha=0.8)
    ax.add_collection3d(base)
    
    # Draw left finger (black)
    left_finger = create_box([-gripper_width/2, 0, 180], [15, 20, 100], color='black', alpha=0.9)
    ax.add_collection3d(left_finger)
    
    # Draw right finger (black)
    right_finger = create_box([gripper_width/2, 0, 180], [15, 20, 100], color='black', alpha=0.9)
    ax.add_collection3d(right_finger)
    
    # Draw steering wheel (dark gray/black)
    wheel = create_wheel([0, 0, 150], 100, 20, angle=steering_angle, color='#1a1a1a', alpha=0.9)
    ax.add_collection3d(wheel)
    
    # Draw wheel center hub
    hub = create_box([0, 0, 150], [40, 40, 15], color='#0a0a0a', alpha=1.0)
    ax.add_collection3d(hub)
    
    # Draw force indicators
    left_force_x, left_force_y, left_force_z, left_color = create_force_indicator(
        current_force/100, [-150, 0, 150]
    )
    ax.plot_surface(left_force_x, left_force_y, left_force_z, color=left_color, alpha=0.6)
    
    right_force_x, right_force_y, right_force_z, right_color = create_force_indicator(
        current_force/100, [150, 0, 150]
    )
    ax.plot_surface(right_force_x, right_force_y, right_force_z, color=right_color, alpha=0.6)
    
    # Draw ground plane
    xx, yy = np.meshgrid(range(-200, 201, 100), range(-200, 201, 100))
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=0.1, color='lightblue')
    
    # Update plot settings
    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])
    ax.set_zlim([0, 400])
    ax.set_xlabel('X (mm)', fontsize=10)
    ax.set_ylabel('Y (mm)', fontsize=10)
    ax.set_zlabel('Z (mm)', fontsize=10)
    ax.set_title('3D Gripper Simulation - Interactive View', fontsize=14, fontweight='bold')
    
    # Update text
    phase_text = ax.text2D(0.05, 0.95, f'Phase: {phase}', transform=ax.transAxes, 
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    status_info = f'Gripper: {gripper_width:5.1f}mm\nForce:   {current_force:5.1f}%\nSteering: {steering_angle:+5.1f}°\nFrame:   {frame_count}'
    status_text = ax.text2D(0.05, 0.85, status_info, transform=ax.transAxes, 
                           fontsize=10, verticalalignment='top', family='monospace',
                           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # Set viewing angle for better perspective
    ax.view_init(elev=20, azim=frame * 0.5)  # Slow rotation
    
    return [phase_text, status_text]

# Create animation
print("Creating 3D animation...")
print("This will open an interactive window where you can rotate the view.\n")

anim = FuncAnimation(fig, update, frames=PHASE_DURATION * len(phases), 
                     interval=50, blit=False, repeat=True)

print("Animation ready! Displaying interactive 3D view...")
print("Use your mouse to rotate, zoom, and pan the view.\n")

plt.tight_layout()
plt.show()

print("\n" + "="*70)
print("  3D Visualization Complete")
print("="*70)
print(f"Total frames displayed: {frame_count}")
print("="*70 + "\n")
