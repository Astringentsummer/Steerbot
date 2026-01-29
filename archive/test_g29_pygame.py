import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joysticks found!")
    exit()

joy = pygame.joystick.Joystick(0)
joy.init()

print(f"Name: {joy.get_name()}")
print(f"Axes: {joy.get_numaxes()}")
print(f"Buttons: {joy.get_numbuttons()}")

try:
    while True:
        pygame.event.pump()
        # Axis 0 is usually steering
        angle = joy.get_axis(0)
        # Axis 1/2 are often pedals
        # Buttons for gripper open/close
        btn_open = joy.get_button(0) # Cross?
        btn_close = joy.get_button(1) # Circle?
        
        print(f"\rSteering: {angle:6.3f} | Open: {btn_open} | Close: {btn_close}", end="")
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\nDone")
pygame.quit()
