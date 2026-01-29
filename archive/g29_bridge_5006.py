#!/usr/bin/env python3
"""
G29 UDP Bridge - Sends data to port 5006
"""
import socket
import json
import time
import numpy as np

try:
    import pygame
    HAS_PYGAME = True
except:
    HAS_PYGAME = False
    print("[INFO] pygame not found, using virtual mode")

UDP_IP = "127.0.0.1"
UDP_PORT = 5006  # Changed to match new integration

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Try to initialize G29
    g29_available = False
    if HAS_PYGAME:
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"[INFO] G29 detected: {joystick.get_name()}")
            g29_available = True
        else:
            print("[INFO] No G29 detected. Using VIRTUAL TEST MODE.")
    
    if not g29_available:
        print("[INFO] Generating virtual steering signal (sine wave)")
    
    print(f"[INFO] Broadcasting to {UDP_IP}:{UDP_PORT}")
    print("[INFO] Press Ctrl+C to stop")
    
    virtual_time = 0.0
    
    try:
        while True:
            if g29_available:
                pygame.event.pump()
                steer = joystick.get_axis(0)  # Steering axis
                buttons = [i for i in range(joystick.get_numbuttons()) if joystick.get_button(i)]
            else:
                # Virtual mode: sine wave
                steer = 0.8 * np.sin(virtual_time * 0.5)
                buttons = []
                virtual_time += 0.05
            
            data = {
                "steer": float(steer),
                "buttons": buttons
            }
            
            sock.sendto(json.dumps(data).encode(), (UDP_IP, UDP_PORT))
            
            if g29_available:
                print(f"\r[G29] Steer: {steer:+.2f} | Buttons: {buttons}", end="", flush=True)
            else:
                print(f"\r[VIRTUAL] Steer: {steer:+.2f}", end="", flush=True)
            
            time.sleep(0.05)  # 20 Hz
            
    except KeyboardInterrupt:
        print("\n[INFO] Stopped")
    finally:
        if HAS_PYGAME and g29_available:
            pygame.quit()
        sock.close()

if __name__ == "__main__":
    main()
