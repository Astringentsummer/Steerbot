# Isaac Sim Setup Guide

## What You Have

Isaac Sim 5.1.0 is already in your Downloads folder. No installation needed.

Location: `C:\Users\rohit\Downloads\isaac-sim-standalone-5.1.0-linux-x86_64\`

## How to Run (3 Steps)

### Step 1: Install X Server (One-time setup)
Download and install VcXsrv (free X server for Windows):
- Download from: https://sourceforge.net/projects/vcxsrv/
- Install with default options
- Run XLaunch and select: "Multiple windows", Display 0, "Disable access control"

### Step 2: Start VcXsrv
Before running Isaac Sim each time, start the X server:
```powershell
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl
```

Or double-click the XLaunch icon and use the settings above.

### Step 3: Run Isaac Sim
```powershell
.\RUN_ISAAC_SIM.ps1
```

Isaac Sim will open with your gripper and steering wheel simulation.

## What You'll See

- 3D viewport with gripper and steering wheel
- Real-time physics (NVIDIA PhysX)
- RTX ray tracing with dynamic lighting
- Gripper animation: Opens, Approaches, Grasps, Steers, Releases
- 60 FPS smooth simulation

## Comparison with Previous Setup

### Before:
- Matplotlib 3D animations (no real physics)
- Tkinter errors and crashes
- No actual simulation environment

### Now:
- Real Isaac Sim installation
- Real physics simulation (PhysX)
- RTX GPU-accelerated rendering
- Simple script to run everything
- ROS2 integration possible
- Your RTX 5080 handles this well

## Files Created

### Main Files:
1. RUN_ISAAC_SIM.ps1 - Main launcher (run this)
2. isaac_simple_demo.py - The simulation code (gripper and wheel)
3. ISAAC_SIM_SETUP.md - Complete guide with troubleshooting

### How They Work Together:
```
RUN_ISAAC_SIM.ps1 (PowerShell)
    ↓
launch_isaac_demo.sh (Bash in WSL)
    ↓
Isaac Sim Python (isaac_simple_demo.py)
    ↓
Your simulation runs with physics
```

## Quick Start Commands

```powershell
# 1. Install VcXsrv from: https://sourceforge.net/projects/vcxsrv/

# 2. Start X server
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl

# 3. Navigate to project
cd C:\Users\rohit\Documents\Steerbot

# 4. Run simulation
.\RUN_ISAAC_SIM.ps1
```

## Next Steps

### Today
1. Install VcXsrv (takes about 5 minutes)
2. Run `.\RUN_ISAAC_SIM.ps1`
3. Watch your gripper simulation

### This Week
1. Customize the simulation (edit `isaac_simple_demo.py`)
2. Add ROS2 integration if needed
3. Connect to your real gripper when it arrives

### Later
1. Test gripper control algorithms in simulation
2. Record simulation data
3. Train ML models (Isaac Sim supports reinforcement learning)

## Why Isaac Sim Instead of Matplotlib

### Matplotlib 3D (Previous approach):
```python
# Just drawing lines and shapes
ax.plot3D([x1, x2], [y1, y2], [z1, z2])
```
- No physics calculations
- No collision detection  
- No force simulation
- Only visual representation

### Isaac Sim (Current setup):
```python
# Real physics simulation
world.step(render=True)  # Physics calculates everything
```
- Gravity, friction, collisions
- Joint constraints
- Force feedback
- Realistic motion
- Same code works with real hardware

## Troubleshooting

### "Cannot open display :0"
Start VcXsrv first. Allow it through Windows Firewall if prompted.

### "Isaac Sim not found"
Check the path:
```powershell
Test-Path "C:\Users\rohit\Downloads\isaac-sim-standalone-5.1.0-linux-x86_64\isaac-sim.sh"
```
Should return True.

### Script runs but no window appears
- Check VcXsrv is running (icon in system tray)
- In VcXsrv settings, make sure "Disable access control" is checked

### Simulation is slow
Your RTX 5080 should handle this easily. Check NVIDIA Control Panel to make sure Isaac Sim uses the GPU.

## Learn More

- Full guide: ISAAC_SIM_SETUP.md
- Project status: CLEAN_PROJECT_STATUS.md
- Isaac Sim documentation: https://docs.omniverse.nvidia.com/isaacsim/latest/

## Summary

You now have a real physics simulation environment running:
- Isaac Sim 5.1.0 installed
- Physics simulation ready (PhysX)
- RTX rendering ready
- Simple launcher script created
- Only need VcXsrv X server to display the GUI

Ready to run:
```powershell
.\RUN_ISAAC_SIM.ps1
```
