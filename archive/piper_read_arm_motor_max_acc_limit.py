#!/usr/bin/env python3
# -*-coding:utf8-*-
# Note: This demo cannot run directly, you need to pip install the SDK first
# Read the maximum acceleration limit of all motors of the robotic arm
import time
from piper_sdk import C_PiperInterface_V2

# Test code
if __name__ == "__main__":
    piper = C_PiperInterface_V2()
    piper.ConnectPort()
    while True:
        piper.SearchAllMotorMaxAccLimit()
        print(piper.GetAllMotorMaxAccLimit())
        time.sleep(0.01)
    