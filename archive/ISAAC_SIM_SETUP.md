# Isaac Sim Setup Guide

## What You Have

Isaac Sim 5.1.0 is already in your Downloads folder.
Location: `C:\Users\rohit\Downloads\isaac-sim-standalone-5.1.0-linux-x86_64\`

## How to Run

### Option 1: Automated Script (Recommended)
```powershell
.\RUN_ISAAC_SIM.ps1
```

This script will:
- Check all requirements
- Launch Isaac Sim via WSL
- Run your gripper and steering wheel simulation
- Show physics and RTX rendering

### Option 2: Manual Launch
If you want to run it manually:
```bash
# In WSL (wsl -d Ubuntu-22.04)
cd /mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64
./python.sh /mnt/c/Users/rohit/Documents/Steerbot/isaac_simple_demo.py
```

## Requirements

### 1. WSL2 (Already Installed)
```powershell
wsl --version
```

### 2. X Server for GUI (Required)
Isaac Sim needs a display. Install VcXsrv or X410:

**VcXsrv (Free):**
- Download: https://sourceforge.net/projects/vcxsrv/
- Install and run XLaunch
- Choose: "Multiple windows", Display 0, Start no client
- Important: Check "Disable access control"

**Start VcXsrv:**
```powershell
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl
```

### 3. Set DISPLAY in WSL
```bash
export DISPLAY=:0
```

## What the Simulation Does

1. **Physics Simulation** (NVIDIA PhysX)
   - Real gravity, collisions, friction
   - Dynamic rigid body physics
   - Joint constraints

2. **Gripper Actions**
   - Opens to 100mm
   - Approaches steering wheel
   - Closes to 50mm (grasps wheel)
   - Steers the wheel ±45 degrees
   - Releases

3. **RTX Rendering**
   - Ray-traced lighting
   - Physically-based materials
   - Real-time shadows

## Files Created

### Main Files:
- RUN_ISAAC_SIM.ps1 - Main launcher script
- isaac_simple_demo.py - Simulation code
- launch_isaac_demo.sh - Bash launcher for WSL

### Alternative Files:
- isaac_gripper_sim.py - More advanced version
- launch_isaac_sim.ps1 - Alternative launcher

## Troubleshooting

### "Cannot connect to display"
Solution: Start VcXsrv first
```powershell
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl
```

Then in WSL:
```bash
export DISPLAY=:0
```

### "Isaac Sim not found"
Check location:
```powershell
Test-Path "C:\Users\rohit\Downloads\isaac-sim-standalone-5.1.0-linux-x86_64\isaac-sim.sh"
```
Should return True. If not, Isaac Sim might be in a different location.

### "Python package not found"
Isaac Sim uses its own Python. Always use:
```bash
./python.sh your_script.py
```
Not regular `python your_script.py`

### GUI is slow or laggy
Your RTX 5080 should handle this easily. Make sure you're using the GPU in NVIDIA Control Panel. Try headless mode if needed (edit `config = {"headless": True}` in the Python script).

## Customize the Simulation

Edit `isaac_simple_demo.py`:

### Change gripper size:
```python
gripper_width = 0.20  # 200mm instead of 160mm
```

### Change colors:
```python
color=np.array([0.8, 0.2, 0.2])  # RGB values (red, green, blue)
```

### Change steering angle:
```python
angle = np.sin(frame * 0.05) * 0.8  # ±80 degrees instead of ±45
```

## Isaac Sim vs 2D Demo

### 2D Demo (run_gripper_steering_demo.py)
- Simple visualization
- Works on Windows natively
- Creates animated GIF
- No real physics
- No 3D view

### Isaac Sim (RUN_ISAAC_SIM.ps1)
- Real physics simulation (PhysX)
- RTX ray-traced rendering
- 3D interactive view
- ROS2 integration possible
- Same code works with real hardware
- Needs WSL + X server
- Larger download (around 8GB)

## Next Steps

### Try it now:
```powershell
.\RUN_ISAAC_SIM.ps1
```

### If it works:
- You have a full physics simulation
- This is a real Digital Twin
- Can integrate with ROS2
- Can test gripper code before hardware arrives

### Add your gripper interface:
```python
from gripper_interface import Gripper
gripper = Gripper()
# Your gripper code here
```

### Connect to ROS2:
Isaac Sim has built-in ROS2 bridge. We can add this later.

## What You'll See

When you run `RUN_ISAAC_SIM.ps1`, Isaac Sim will open with:
- 3D viewport with gripper and steering wheel
- Physics simulation running at 60 FPS
- Gripper fingers moving smoothly
- Steering wheel rotating when grasped
- Real-time ray-traced lighting

## System Requirements

Your system (RTX 5080) is well-suited for Isaac Sim:
- RTX cores handle fast ray tracing
- CUDA cores handle physics computation
- 16GB VRAM means no memory issues

This is exactly what Isaac Sim was designed for.

## Getting Help

1. First time: Run `.\RUN_ISAAC_SIM.ps1` and follow on-screen messages
2. X server issues: Install VcXsrv and allow it through Windows Firewall
3. Want to customize: Edit `isaac_simple_demo.py` (it has comments explaining each part)
4. Questions: Check the console output to see what's happening

## Ready to Start

Install VcXsrv and run:
```powershell
.\RUN_ISAAC_SIM.ps1
```
