import pygame
import json
import time
import os

# ==============================================================================
# G29 DIRECT TO 3D BRIDGE (Windows Native)
# ==============================================================================

STATE_FILE = "digital_twin_state.json"

def run_bridge():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("[ERROR] - Logitech G29 not detected for 3D Control.")
        return

    g29 = pygame.joystick.Joystick(0)
    g29.init()
    print(f"[ACTIVE] - Controlling {STATE_FILE} via {g29.get_name()}")

    gripper_pos = 58.6
    
    try:
        while True:
            pygame.event.pump()
            
            # 1. Read Wheel (Axis 0) -> Angle (-450 to 450 degrees)
            # G29 has 900 degrees lock-to-lock
            wheel_angle = g29.get_axis(0) * 450.0
            
            # 2. Read Buttons for Gripper
            if g29.get_button(0): # X Button -> Close
                gripper_pos = max(0.0, gripper_pos - 2.0)
            if g29.get_button(1): # Circle Button -> Open
                gripper_pos = min(80.0, gripper_pos + 2.0)
            
            # 3. Save State for Visualizer to Pick Up
            state = {
                "wheel_angle": -wheel_angle, # Inverse for visual alignment
                "gripper_pos": gripper_pos,
                "phase": "Manual Control",
                "is_gripping": gripper_pos < 10.0,
                "active": True,
                "latency": 5
            }
            
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
            
            print(f"\r[G29 -> 3D] Angle: {wheel_angle:+.1f} | Gripper: {gripper_pos:.1f}mm    ", end="")
            time.sleep(0.02) # 50Hz

    except KeyboardInterrupt:
        print("\n[INFO] - Bridge Stopped.")
        pygame.quit()

if __name__ == "__main__":
    run_bridge()
