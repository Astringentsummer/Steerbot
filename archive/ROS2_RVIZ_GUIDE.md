# ROS2 + RViz Quick Reference

## What You're Getting

**ROS2 Humble** - Industry standard robotics framework
- LTS support until 2027
- Most stable and widely used
- Best documentation and community support

**RViz2** - 3D Visualization Tool
- Visualize robot models (URDF)
- Display sensor data (cameras, lidar, etc.)
- Show trajectories and motion planning
- Interactive markers for control

## Installation

Run the installation script:
```bash
wsl -d Ubuntu bash /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/install_ros2_humble.sh
```

This will take about 10-15 minutes and install:
- ROS2 Humble Desktop Full
- RViz2 visualization tool
- All development tools
- Python ROS2 packages

## Using RViz2

### Launch RViz2

Make sure VcXsrv is running on Windows, then:

```bash
# In WSL
export DISPLAY=:0
rviz2
```

You should see the RViz2 window open with a 3D viewport.

### What You'll See

RViz2 opens with:
- **3D Viewport**: Main visualization area
- **Displays Panel**: Add/remove visualization elements
- **Tool Properties**: Configure selected tools
- **Views Panel**: Camera controls

### Visualizing Your Gripper

To see your gripper in RViz2, you need a URDF model (robot description). I can create one for you that shows:
- Gripper base
- Two fingers
- Steering wheel
- Joint movements

## ROS2 Gripper Node

Your project already has ROS2 integration:

**File**: `ros2_gripper_node.py`

**Topics**:
- `/gripper/command` - Send position commands (0-100mm)
- `/gripper/speed` - Set gripper speed (1-1000)
- `/gripper/state` - Current gripper position
- `/gripper/status` - Status messages

### Running the Gripper Node

```bash
cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper
python3 ros2_gripper_node.py
```

### Controlling the Gripper via ROS2

```bash
# Send position command (50mm)
ros2 topic pub /gripper/command std_msgs/Float32 "data: 50.0"

# Set speed
ros2 topic pub /gripper/speed std_msgs/Int32 "data: 800"

# Monitor gripper state
ros2 topic echo /gripper/state
```

## Comparison: RViz vs Isaac Sim vs Matplotlib

| Feature | RViz2 | Isaac Sim | Matplotlib 3D |
|---------|-------|-----------|---------------|
| **Purpose** | Robot visualization | Physics simulation | Quick demos |
| **Physics** | No | Yes (PhysX) | No |
| **Real-time** | Yes | Yes | Yes |
| **ROS Integration** | Native | Via bridge | Manual |
| **Sensor Data** | Yes | Yes | No |
| **Ease of Use** | Medium | Complex | Easy |
| **Best For** | Robot state & sensors | Testing physics | Quick visualization |

## When to Use Each

**Use RViz2 when:**
- Visualizing robot state in real-time
- Displaying sensor data (cameras, lidar)
- Debugging ROS2 topics and transforms
- Monitoring robot during operation

**Use Isaac Sim when:**
- Testing gripper physics and forces
- Simulating collisions and contacts
- Training ML models
- Validating control algorithms

**Use Matplotlib 3D when:**
- Quick demos and presentations
- No ROS2 needed
- Simple motion visualization
- Works on Windows directly

## Next Steps

1. **Install ROS2 Humble** (run the script)
2. **Test RViz2** (make sure it opens)
3. **Create gripper URDF** (I can do this for you)
4. **Visualize in RViz2** (see your gripper in 3D)
5. **Connect to real hardware** (when it arrives)


