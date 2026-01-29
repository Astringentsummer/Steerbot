"""
Isaac Sim GUI Demo with Visible Content
This creates a simple scene so you can SEE the window working
"""

from isaacsim import SimulationApp

# GUI configuration
config = {
    "headless": False,
    "width": 1920,
    "height": 1080,
}

print("="*70)
print("ISAAC SIM GUI DEMO")
print("="*70)
print("\nStarting Isaac Sim...")
print("A window should open in a few seconds...")
print("\nPlease wait for the window to appear!")
print("="*70 + "\n")

# Create app and open window
simulation_app = SimulationApp(config)

print("\n" + "="*70)
print("WINDOW OPENED!")
print("="*70)
print("\nYou should now see the Isaac Sim window.")
print("Let me add some 3D content so you can see it's working...")
print("="*70 + "\n")

# Now import Isaac Sim modules (AFTER SimulationApp is created)
from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid
import numpy as np

# Create world
print("Creating 3D world...")
world = World()

# Add a ground plane
print("Adding ground plane...")
world.scene.add_default_ground_plane()

# Add some colorful cubes
print("Adding colorful cubes...")
for i in range(5):
    x = (i - 2) * 0.3
    cube = DynamicCuboid(
        prim_path=f"/World/Cube_{i}",
        name=f"cube_{i}",
        position=np.array([x, 0, 0.5]),
        size=0.2,
        color=np.array([i/5, 1-i/5, 0.5])
    )
    world.scene.add(cube)

print("Resetting world...")
world.reset()

print("\n" + "="*70)
print("SCENE READY!")
print("="*70)
print("\nYou should now see:")
print("  - A ground plane")
print("  - 5 colorful cubes floating in the air")
print("\nThe window will stay open for 2 MINUTES.")
print("You can rotate the camera with right-click + drag")
print("You can zoom with scroll wheel")
print("\nPress Ctrl+C to close early")
print("="*70 + "\n")

# Run simulation and keep window open
import time
try:
    for i in range(120, 0, -1):
        world.step(render=True)  # Update physics and render
        if i % 10 == 0:  # Print every 10 seconds
            print(f"Window will close in {i} seconds...")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nUser interrupted - closing...")

print("\n" + "="*70)
print("Closing Isaac Sim...")
print("="*70)
simulation_app.close()
print("\nDone! The window should have closed.")
