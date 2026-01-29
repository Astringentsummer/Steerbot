#!/usr/bin/env python3
"""
TEST 1: Verify G29 is sending data
Run this to check if G29 wheel is connected and working
"""

import socket
import json
import time

print("=" * 60)
print(" TEST 1: G29 WHEEL INPUT TEST")
print("=" * 60)
print("")
print("This will listen for G29 data on UDP port 5006")
print("Turn your G29 wheel to see if data is received")
print("")
print("Press Ctrl+C to stop")
print("")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5006))
sock.settimeout(1.0)

last_data_time = time.time()
data_count = 0

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            g29_data = json.loads(data.decode())
            data_count += 1
            last_data_time = time.time()
            
            steering = g29_data.get('steering', 0.0)
            throttle = g29_data.get('throttle', 0.0)
            brake = g29_data.get('brake', 0.0)
            
            print(f"Data #{data_count}: Steering={steering:+.2f} | "
                  f"Throttle={throttle:.2f} | Brake={brake:.2f}")
            
        except socket.timeout:
            if time.time() - last_data_time > 3:
                print("No data received in 3 seconds - is G29 connected?")
                last_data_time = time.time()
        except Exception as e:
            print(f"Error: {e}")
            
except KeyboardInterrupt:
    print("\n")
    print("=" * 60)
    if data_count > 0:
        print(f"TEST PASSED: Received {data_count} data packets")
        print("   G29 wheel is working correctly!")
    else:
        print("TEST FAILED: No data received")
        print("   Check:")
        print("   1. G29 is connected via USB")
        print("   2. G29 driver is running")
        print("   3. Firewall allows UDP port 5006")
    print("=" * 60)

sock.close()
