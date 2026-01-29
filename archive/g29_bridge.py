import pygame
import socket
import time
import json

# Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
FPS = 60

def run_bridge():
    pygame.init()
    pygame.joystick.init()
    
    import math

    # Check for devices
    if pygame.joystick.get_count() == 0:
        print("WARNING: No G29 Steering Wheel detected!")
        print(">>> STARTING VIRTUAL TEST MODE (Auto-generating sine wave) <<<")
        virtual_mode = True
        g29 = None
    else:
        virtual_mode = False
        # Initialize G29
        g29 = pygame.joystick.Joystick(0)
        g29.init()
        print(f"Connected to: {g29.get_name()}")

    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Broadcasting inputs to {UDP_IP}:{UDP_PORT}...")
    
    clock = pygame.time.Clock()
    running = True
    start_time = time.time()
    
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if virtual_mode:
                # Generate Sine Wave (-1.0 to 1.0)
                elapsed = time.time() - start_time
                steer = math.sin(elapsed * 0.5) # Slow sine wave
                buttons = []
            else:
                # G29 Axis Mapping (Standard Pygame indices for G29)
                # Axis 0: Steering (-1.0 to 1.0)
                steer = g29.get_axis(0)
                buttons = [g29.get_button(i) for i in range(g29.get_numbuttons())]
            
            # Extract basic inputs
            data = {
                "steer": float(steer), # normalize if needed
                "buttons": buttons
            }
            
            # Send via UDP
            msg = json.dumps(data).encode('utf-8')
            sock.sendto(msg, (UDP_IP, UDP_PORT))
            
            # Print status less frequently
            if virtual_mode and int(time.time() * 10) % 20 == 0:
                 print(f"Virtual Auto-Steer: {steer:.3f} | Sending...")
            elif not virtual_mode and pygame.time.get_ticks() % 1000 < 20: 
                 print(f"G29 Steer: {steer:.3f} | Sending...")
            
            clock.tick(FPS)
            
    except KeyboardInterrupt:
        print("\nStopping Bridge...")
    finally:
        pygame.quit()

if __name__ == "__main__":
    frame_count = 0
    run_bridge()
