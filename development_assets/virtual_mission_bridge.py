import json
import time
import os
import math

# ==============================================================================
# PIPER-G29 VIRTUAL MISSION SIMULATOR: "THE 55 DEGREE CHALLENGE"
# ==============================================================================

STATE_FILE = "digital_twin_state.json"

def run_virtual_mission():
    print("="*60)
    print(" HICTP | VIRTUAL MISSION START: 55° STEERING ACTUATION")
    print("="*60)
    print("Target: 0.9468 rad (Approx. 54.26°)")
    print("Strategy: MoveIt2 Planned Trajectory -> Isaac Sim Sync")
    print("-" * 60)

    # Simulation constants
    TARGET_ANGLE = 54.26
    STEPS = 100
    DT = 0.05

    try:
        # Phase 1: Approach Wheel (Move gripper to rim position)
        print("[PHASE 1] - Approaching Wheel Rim...")
        for i in range(STEPS // 2):
            # Move from starting position to wheel rim
            progress = i / (STEPS // 2)
            x_curr = 0.0 * (1 - progress) + 0.0 * progress  # Start at X=0, stay at X=0
            y_curr = 0.0 * (1 - progress) + 0.15 * progress  # Move from Y=0 to Y=0.15 (rim)
            z_curr = 0.95 * (1 - progress) + 0.70 * progress  # Move down from Z=0.95 to Z=0.70
            
            state = {
                "wheel_angle": 0.0,
                "gripper_pos": 80.0,  # Open
                "gripper_xyz": [x_curr, y_curr, z_curr],
                "phase": "Approaching Rim",
                "is_gripping": False,
                "active": True,
                "latency": 5
            }
            with open(STATE_FILE, "w") as f: json.dump(state, f)
            time.sleep(DT)

        # Phase 2: Grasp Rim (Close gripper on wheel rim)
        print("[PHASE 2] - Grasping Wheel Rim...")
        for i in range(1, 41):
            curr_grip = 80.0 - (i * (80.0 - 58.6) / 40.0)
            state["gripper_pos"] = curr_grip
            state["gripper_xyz"] = [0.0, 0.15, 0.70]  # Stay at rim position
            state["phase"] = "Grasping Rim"
            state["is_gripping"] = curr_grip < 60.0
            with open(STATE_FILE, "w") as f: json.dump(state, f)
            time.sleep(DT)

        # Phase 3: Rotate Wheel (Gripper follows rim while holding)
        print("[PHASE 3] - Rotating Wheel 55 Degrees...")
        for i in range(1, STEPS + 1):
            curr_angle = (i / STEPS) * TARGET_ANGLE
            rad = math.radians(curr_angle)
            
            # Gripper orbits with the wheel rim (stays gripped)
            # Starting at Y=0.15 (top), rotating clockwise
            g_x = 0.15 * math.sin(rad)
            g_y = 0.15 * math.cos(rad)
            
            state["wheel_angle"] = -curr_angle
            state["gripper_xyz"] = [g_x, g_y, 0.70]
            state["gripper_pos"] = 58.6  # Keep gripped
            state["is_gripping"] = True  # Still gripping
            state["phase"] = f"Rotating: {curr_angle:.2f}°"
            
            with open(STATE_FILE, "w") as f: json.dump(state, f)
            
            print(f"\rAngle: {curr_angle:6.2f}° | Gripper at ({g_x:.3f}, {g_y:.3f}, 0.70) | GRIPPING", end="")
            time.sleep(DT)

        # Phase 4: Release Gripper
        print("\n[PHASE 4] - Releasing Gripper...")
        for i in range(1, 21):
            curr_grip = 58.6 + (i * (80.0 - 58.6) / 20.0)
            state["gripper_pos"] = curr_grip
            state["is_gripping"] = curr_grip < 60.0
            state["phase"] = "Releasing"
            with open(STATE_FILE, "w") as f: json.dump(state, f)
            time.sleep(DT)

        # Phase 5: Rotate Back to Center (Return Motion)
        print("[PHASE 5] - Rotating Back to Center...")
        for i in range(STEPS, 0, -1):
            curr_angle = (i / STEPS) * TARGET_ANGLE
            rad = math.radians(curr_angle)
            
            # Gripper orbits back with the wheel rim
            g_x = 0.15 * math.sin(rad)
            g_y = 0.15 * math.cos(rad)
            
            state["wheel_angle"] = -curr_angle
            state["gripper_xyz"] = [g_x, g_y, 0.70]
            state["gripper_pos"] = 58.6  # Keep gripped during return
            state["is_gripping"] = True
            state["phase"] = f"Returning: {curr_angle:.2f}°"
            
            with open(STATE_FILE, "w") as f: json.dump(state, f)
            
            print(f"\rAngle: {curr_angle:6.2f}° | Gripper at ({g_x:.3f}, {g_y:.3f}, 0.70) | RETURNING", end="")
            time.sleep(DT)

        # Phase 6: Final Release
        print("\n[PHASE 6] - Final Release...")
        for i in range(1, 21):
            curr_grip = 58.6 + (i * (80.0 - 58.6) / 20.0)
            state["gripper_pos"] = curr_grip
            state["is_gripping"] = curr_grip < 60.0
            state["gripper_xyz"] = [0.0, 0.15, 0.70]  # Back at top
            state["wheel_angle"] = 0.0  # Back at center
            state["phase"] = "Final Release"
            with open(STATE_FILE, "w") as f: json.dump(state, f)
            time.sleep(DT)

        print("\n[SUCCESS] - Complete cycle: 0° -> 55° -> 0°")
        print("Repeating in 3 seconds...")
        time.sleep(3)
        run_virtual_mission()  # Loop for presentation

    except KeyboardInterrupt:
        print("\n[INFO] - Virtual Mission Terminated.")

if __name__ == "__main__":
    run_virtual_mission()
