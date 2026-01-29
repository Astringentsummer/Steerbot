# Quick Start: RViz Gripper Visualization

## What You Have Now

**URDF Model Created** ✓
- File: `urdf/gripper.urdf`
- Includes: Gripper base, 2 movable fingers, steering wheel
- Joints: Prismatic (fingers), Revolute (wheel)

**ROS2 Visualizer Node** ✓
- File: `gripper_visualizer.py`
- Publishes joint states for animation
- Shows all 5 phases automatically

**Launch Script** ✓
- File: `launch_rviz_gripper.sh`
- Starts RViz with gripper model
- Includes joint controller GUI

## How to Use (After ROS2 Installation Completes)

### Step 1: Launch RViz with Gripper

```bash
wsl -d Ubuntu bash /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/launch_rviz_gripper.sh
```

This will:
1. Start robot_state_publisher (loads URDF)
2. Start joint_state_publisher_gui (manual control)
3. Launch RViz2

### Step 2: Configure RViz

When RViz opens:
1. Click **"Add"** button (bottom left)
2. Select **"RobotModel"**
3. In left panel, set **Fixed Frame** to `base_link`
4. You should see your gripper!

### Step 3: Control the Gripper

**Option A: Manual Control (GUI)**
- Use the joint_state_publisher window that appears
- Slide the bars to move fingers and wheel

**Option B: Automated Animation**
```bash
# In a new WSL terminal
cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper
python3 gripper_visualizer.py
```

This runs the 5-phase animation automatically.

## URDF Model Details

**Links (Parts):**
- `base_link` - Reference frame
- `gripper_base` - Main gripper body (150x100x50mm, gray)
- `left_finger` - Left gripper finger (20x30x150mm, black)
- `right_finger` - Right gripper finger (20x30x150mm, black)
- `steering_wheel` - G29-style wheel (350mm diameter, black)
- `wheel_hub` - Center hub (80x80x20mm, very dark)

**Joints (Movements):**
- `left_finger_joint` - Prismatic, range: 0 to -60mm
- `right_finger_joint` - Prismatic, range: 0 to -60mm (mirrored)
- `wheel_joint` - Revolute, range: ±45° (±0.785 rad)

## Troubleshooting

**RViz doesn't show the robot:**
- Check Fixed Frame is set to `base_link`
- Make sure RobotModel display is added
- Verify robot_state_publisher is running

**No joint_state_publisher GUI:**
- Install with: `sudo apt install ros-humble-joint-state-publisher-gui`

**RViz window doesn't appear:**
- Make sure VcXsrv is running on Windows
- Check DISPLAY variable: `echo $DISPLAY` (should be `:0`)

## Next Steps

1. **Wait for ROS2 installation** to complete (~10-15 min)
2. **Launch RViz** with the script
3. **See your gripper** in 3D
4. **Control it** manually or with animation
5. **Integrate with real hardware** when it arrives
