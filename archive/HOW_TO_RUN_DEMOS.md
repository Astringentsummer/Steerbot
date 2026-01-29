# How to Run the Demos

Three ways to see the gripper in action, from simplest to most advanced.

## 1. Terminal Demo (Recommended First)

**What it does:** Shows ASCII art animation right in your terminal  
**Time:** 15 seconds  
**Requirements:** Just Python (no extra packages)

```bash
python run_gripper_terminal_demo.py
```

You'll see the gripper and steering wheel drawn with text characters, animating through 5 phases:
1. OPEN - Fingers spread apart
2. APPROACH - Moving toward wheel
3. GRASP - Gripping the wheel
4. STEER - Rotating the wheel left and right
5. RELEASE - Opening back up

Perfect for quick testing or when you don't want to install graphics libraries.

---

## 2. 2D Animation Demo

**What it does:** Creates a smooth animated GIF showing the gripper operation  
**Time:** 1 minute to generate  
**Requirements:** matplotlib (`pip install matplotlib`)

```bash
# Install if needed
pip install matplotlib

# Run the demo
python run_gripper_steering_demo.py
```

This creates `gripper_steering_demo.gif` that you can:
- Share with others to show what you're building
- Use in presentations or documentation
- Watch to understand the motion before building hardware

The animation shows:
- Gripper fingers with realistic motion
- G29 steering wheel (350mm diameter)
- Force indicators
- Separation distance measurements
- Phase labels

---

## 3. Isaac Sim 3D Physics (Advanced)

**What it does:** Professional robotics simulation with real physics  
**Time:** 30 seconds to run (after 1-time 2-minute setup)  
**Requirements:** Isaac Sim installed in WSL (~9GB)

### If Isaac Sim is Already Set Up

```powershell
# From PowerShell in this directory
.\launch_isaac_3d.ps1
```

### What You Get

This uses NVIDIA's PhysX physics engine (the same one used in professional robotics research) to simulate:
- 3D gripper with realistic geometry
- Collision detection and contact forces
- Gravity and dynamics
- Steering wheel with proper mass/inertia
- Force calculations based on actual physics

The output shows frame-by-frame data about positions, forces, and states.

### Troubleshooting Isaac Sim

If you get errors:

**Error: "ISAAC_PATH not found"**
- The environment variables are not set correctly
- Solution: The launcher script should handle this automatically
- If it persists, check that Isaac Sim is at `~/isaac_sim_extract` in WSL

**Error: "wsl command not found"**
- WSL is not installed or not in PATH
- Solution: Run `wsl --install` in PowerShell (admin) and restart

**Simulation hangs or times out**
- First run can take 60-90 seconds as Isaac loads
- Subsequent runs are faster (~30 seconds)
- Be patient on the first execution

---

## Comparison

| Feature | Terminal | 2D Animation | 3D Physics |
|---------|----------|--------------|------------|
| Setup time | 0 seconds | 30 seconds | 2 minutes |
| Run time | 15 seconds | 1 minute | 30 seconds |
| Visual quality | ASCII art | Smooth GIF | Physics sim |
| File output | None | GIF file | Text data |
| Dependencies | None | matplotlib | Isaac Sim |
| Platform | Any | Any | WSL/Linux |

## Which Should I Use?

- **Just want to see if code works?** → Terminal demo
- **Want to show someone what you're building?** → 2D animation
- **Need to test physics and dynamics?** → Isaac Sim 3D
- **Preparing for hardware testing?** → All three to compare

## Next Steps

After running demos, you can:
1. Modify timing in the code to match your needs
2. Adjust gripper speeds and forces
3. Test different steering angles
4. Connect real hardware using vehicle_gripper_integration.py

Each demo uses the same `Gripper` class interface, so changes you make to the demo code will translate directly to real hardware control.
