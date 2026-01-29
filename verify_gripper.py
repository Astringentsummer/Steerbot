
import hydra
from omegaconf import DictConfig
import torch
import numpy as np
from isaac_rl.tasks.G29PiperTask import G29PiperTask
from omni.isaac.gym.vec_env import VecEnvBase

class MockSimConfig:
    def __init__(self):
        self.task_config = {
            "env": {
                "numEnvs": 1,
                "envSpacing": 1.0,
                "episodeLength": 100
            }
        }

def main():
    print("Starting Gripper Verification...")
    
    # 1. Initialize Task (Mocking capabilities if outside Sim, but better to run inside)
    # This script is intended to be run with the Isaac Sim python
    
    # Check if we can import the task
    try:
        from omni.isaac.kit import SimulationApp
        simulation_app = SimulationApp({"headless": True})
    except ImportError:
        print("Error: Could not import Isaac Sim modules. Make sure you are using the correct Python interpreter.")
        return

    # Setup
    sim_config = MockSimConfig()
    env = VecEnvBase(headless=True)
    task = G29PiperTask(name="G29Piper", sim_config=sim_config, env=env)
    
    # Reset
    env.reset()
    
    # Test 1: Open Gripper
    print("\nTest 1: Open Gripper (Action = 1.0)")
    actions = torch.zeros((1, 7), device="cuda:0")
    actions[0, 6] = 1.0 # Open
    
    task.pre_physics_step(actions)
    
    # Check "target" sent to joints (we can't easily check physics result without stepping, 
    # but we can check the internal logic if we inspect the tensor passed to set_joint_positions)
    # Verification in actual sim is visual or via joint state reading.
    
    print("Stepping simulation...")
    for _ in range(10):
        env.step(actions)
    
    obs = task.get_observations()
    gripper_pos = obs["obs_buf"][0, 14:16] # indices 14, 15
    print(f"Gripper Positions: {gripper_pos}")
    
    # Test 2: Close Gripper
    print("\nTest 2: Close Gripper (Action = -1.0)")
    actions[0, 6] = -1.0 # Close
    
    for _ in range(10):
        env.step(actions)
        
    obs = task.get_observations()
    gripper_pos = obs["obs_buf"][0, 14:16]
    print(f"Gripper Positions: {gripper_pos}")
    
    simulation_app.close()
    print("\nTest Complete.")

if __name__ == "__main__":
    main()
