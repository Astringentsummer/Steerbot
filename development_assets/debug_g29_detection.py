import pygame
import sys

# ==============================================================================
# G29 HARDWARE DIAGNOSTIC TOOL
# ==============================================================================

def scan_hardware():
    pygame.init()
    pygame.joystick.init()
    
    count = pygame.joystick.get_count()
    print("="*50)
    print(f" DEVICE SCAN: {count} Controllers Found ")
    print("="*50)

    if count == 0:
        print("[CRITICAL] - No Joystick/Wheel detected by Windows.")
        print("\nTroubleshooting Checklist:")
        print("1. Is the G29 USB plugged directly into the PC (not a hub)?")
        print("2. Is the switch on top of the wheel set to 'PS4' mode?")
        print("3. Is the power cable plugged in? (The wheel should spin on plug-in)")
        print("4. Is 'Logitech G HUB' installed and running?")
        return

    for i in range(count):
        j = pygame.joystick.Joystick(i)
        j.init()
        print(f"ID [{i}]: {j.get_name()}")
        print(f"  - Axes: {j.get_numaxes()}")
        print(f"  - Buttons: {j.get_numbuttons()}")
        print(f"  - HATS: {j.get_numhats()}")
        print("-" * 30)

    print("\n[PRO TIP] If your G29 is listed as ID [1] or higher,")
    print("you must update g29_to_3d_bridge.py to use that ID number.")
    print("="*50)
    pygame.quit()

if __name__ == "__main__":
    scan_hardware()
