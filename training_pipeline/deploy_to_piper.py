#!/usr/bin/env python3
"""
Deploy Trained Policy to Real Piper Hardware
Transfer learned policy from Isaac Sim to real robot
"""
import sys
import os
import numpy as np
import torch
import time

# Import your existing Piper control code
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# from piper_control import PiperController  # Your existing Piper interface

# Import SAC agent
sys.path.append(os.path.join(os.path.dirname(__file__)))
from sac_algorithm import SAC


class RealPiperDeployment:
    """Deploy trained SAC policy to real Piper hardware"""
    
    def __init__(self, model_path):
        self.model_path = model_path
        
        # Load trained agent
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.agent = SAC(
            state_dim=15,  # Match training
            action_dim=8,   # Match training
            device=self.device
        )
        self.agent.load(model_path)
        print(f" Loaded trained model: {model_path}")
        
        # Initialize real Piper (placeholder - use your actual interface)
        # self.piper = PiperController()
        # self.piper.connect()
        print(" Real Piper interface not connected (placeholder)")
    
    def get_state(self):
        """Get current state from real Piper hardware"""
        # Read joint positions and velocities from real hardware
        # joint_positions = self.piper.get_joint_positions()  # 8 values
        # joint_velocities = self.piper.get_joint_velocities()  # 8 values
        # wheel_angle = self.read_g29_angle()  # 1 value
        
        # Placeholder: return dummy state
        joint_positions = np.zeros(8)
        joint_velocities = np.zeros(8)
        wheel_angle = 0.0
        
        state = np.concatenate([
            joint_positions[:8],
            joint_velocities[:6],
            [wheel_angle]
        ])
        return state
    
    def send_action(self, action):
        """Send action to real Piper hardware"""
        # Convert normalized action [-1, 1] to joint commands
        # self.piper.set_joint_velocities(action)
        
        # Placeholder
        print(f"  Action: {action[:3]}... (not sent to hardware)")
    
    def read_g29_angle(self):
        """Read current G29 wheel angle"""
        # Read from your G29 interface
        # return g29.get_angle()
        return 0.0  # Placeholder
    
    def run_closed_loop(self, duration_sec=60, control_freq=30):
        """Run closed-loop control with trained policy"""
        
        print("\n" + "=" * 80)
        print("DEPLOYING TO REAL PIPER HARDWARE")
        print("=" * 80)
        print(f"Duration: {duration_sec}s")
        print(f"Control Frequency: {control_freq} Hz")
        print("=" * 80 + "\n")
        
        dt = 1.0 / control_freq
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration_sec:
                loop_start = time.time()
                
                # Get current state
                state = self.get_state()
                
                # Get action from trained policy
                action = self.agent.select_action(state, evaluate=True)
                
                # Send to hardware
                self.send_action(action)
                
                # Maintain control frequency
                elapsed = time.time() - loop_start
                if elapsed < dt:
                    time.sleep(dt - elapsed)
                
                # Print status every second
                if int(time.time() - start_time) % 1 == 0:
                    print(f"  t={time.time()-start_time:.1f}s, "
                          f"State: {state[:3]}..., Action: {action[:3]}...")
        
        except KeyboardInterrupt:
            print("\n\nStopping deployment...")
        
        finally:
            # Stop robot
            # self.piper.stop()
            print(" Deployment stopped")


def deploy_to_hardware():
    """Main deployment function"""
    
    # Path to trained model
    model_path = "logs/extended_sac/sac_final_10k.pt"
    
    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found: {model_path}")
        print("Train the model first using train_extended_sac.py")
        return
    
    # Create deployment
    deployment = RealPiperDeployment(model_path)
    
    # Run closed-loop control
    deployment.run_closed_loop(duration_sec=60, control_freq=30)


if __name__ == "__main__":
    print("""
     WARNING: This will control REAL HARDWARE!
    
    Before running:
    1. Ensure Piper arm is in safe position
    2. Emergency stop is accessible
    3. Workspace is clear
    4. G29 wheel is connected
    
    Press Ctrl+C to stop at any time.
    """)
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    deploy_to_hardware()
