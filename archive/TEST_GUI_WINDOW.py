"""
Minimal Isaac Sim GUI Test
This will open the Isaac Sim window and keep it running
"""

from isaacsim import SimulationApp

# Configure for GUI mode (NOT headless)
config = {
    "headless": False,  # MUST be False to show window
    "width": 1280,
    "height": 720,
}

print("Creating Isaac Sim window...")
print("This should open a GUI window!")

# Create the app - this opens the window
simulation_app = SimulationApp(config)

print("\n" + "="*60)
print("SUCCESS! Isaac Sim window should be open now!")
print("="*60)
print("\nThe window will stay open for 30 seconds...")
print("You should see the Isaac Sim interface.")
print("\nPress Ctrl+C to close early, or wait 30 seconds.")
print("="*60 + "\n")

# Keep window open
import time
try:
    for i in range(30, 0, -1):
        print(f"Closing in {i} seconds...", end='\r')
        time.sleep(1)
except KeyboardInterrupt:
    print("\nUser interrupted - closing...")

print("\nClosing Isaac Sim...")
simulation_app.close()
print("Done!")
