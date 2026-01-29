from isaacsim import SimulationApp

print("Launching Minimal Isaac Sim Test...")
config = {"headless": False, "width": 800, "height": 600}
simulation_app = SimulationApp(config)

print("Simulation App Created. Creating World...")
from omni.isaac.core import World
world = World()
world.scene.add_default_ground_plane()

print("\nSUCCESS! Isaac Sim is working.")
print("Press ENTER to close...")
input()
simulation_app.close()
