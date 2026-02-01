import pygame
import time

# ==============================================================================
# G29 HARDWARE-IN-THE-LOOP (HIL) TEST SCRIPT
# ==============================================================================

def test_steering_wheel():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("[ERROR] - Logitech G29 not detected. Please check USB connection.")
        return

    g29 = pygame.joystick.Joystick(0)
    g29.init()
    
    print(f"[SUCCESS] - Device Detected: {g29.get_name()}")
    print("Reading G29 Raw Inputs (HID Service)...")
    print("Rotate the wheel and press the Gripper buttons (X/O).")
    print("Press CTRL+C to stop.")

    try:
        while True:
            pygame.event.pump()
            
            # 1. Steering Axis (Normalized -1.0 to 1.0)
            steering = g29.get_axis(0)
            
            # 2. Buttons (Piper Gripper Control mapping)
            btn_x = g29.get_button(0)
            btn_o = g29.get_button(1)
            
            status = "OPEN" if btn_x else "CLOSE" if btn_o else "IDLE"
            
            print(f"\r[G29] Steering: {steering:+.2f} | Action: {status}    ", end="")
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n[INFO] - Hardware test stopped.")
        pygame.quit()

if __name__ == "__main__":
    test_steering_wheel()
