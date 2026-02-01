Done:
Physical setup of G29 in Isaac sim: isaac/scenes/g29_rotate_right_tilted27degrees.usd 

To do:
Physical setup of Piper
Integration: a stage with G29 and Arm robot.

notice: 
Combine all developed modules (engine visualization, ROS2 communication, G29 input) into a single integrated simulation setup inside Isaac Sim
The G29 must be physically stable on the table, with correct colliders, inertia, and a properly aligned steering-wheel joint that can rotate smoothly.
The Piper arm must stand stably (fixed or supported), with all joints moving correctly and controllable from Isaac or MoveIt.
Both models must show no penetration, no jitter, and no articulation warnings when the simulation runs

------

Offene Punkte
```
⬜ Piper als USD importieren
⬜ Collisions, Inertias, Articulation Setup
⬜ Gemeinsame Szene: G29 + Piper auf Tisch
⬜ ROS2 Movement → Isaac Sim Synchronisation
⬜ Keine Jitter oder Articulation Errors
```

------

# Steerbot – ROS2 & Isaac Sim Workspace
Der Steerbot-Workspace enthält alle Module für das Digital-Twin-Projekt bestehend aus:
 - Logitech G29 (Input Device)
 - Piper Roboterarm (MoveIt2 + ros2_control)
 - ROS2 Humble Kommunikation
 - Isaac Sim Integration
 - Startsystem für Simulation & Realbetrieb

Ziel ist ein vollständiger Digital Twin, in dem G29, MoveIt2, der echte Roboter und Isaac Sim konsistent zusammenarbeiten.

## Workspace Struktur
```
Steerbot/
│
├── ros2_ws/                     # ROS2 Workspace
│   ├── src/
│   │   ├── piper_ros/           # Piper Robot (Control, URDF, MoveIt, Simulation)
│   │   ├── g29_isaac_bridge/    # G29 → ROS2 Bridge
│   │   ├── <weitere Pakete>     
│   │
│   └── install/ build/ log/     # Standard ROS2 Ordner
│
├── isaac/
│   └── scenes/
│       └── 1stage.usd           # Hauptszene: Tisch + G29 + Piper
│       # weitere .usd / .py Dateien = Tests/Prototypen
│
├── dev/                         # Entwicklungsdateien
│
├── start_dtp.sh                 # Unified Launcher (Real / Simulation)
└── README.md                    
```

##  Installationsanleitung
Workspace bauen
```
cd ~/Steerbot/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Starten des Gesamtsystems
Alle wichtigen ROS2-Knoten, Controller und MoveIt-Instanzen werden über eine gemeinsame Shell gestartet:

### Simulation Mode
```
./start_dtp.sh -s
```
Startet:
- Fake Hardware Mode
- MoveIt2 (move_group, RViz2, planning pipeline)
- ros2_control (fake hardware)
- Controller bringup
- Alle ROS2 Nodes in eigenen Terminals

### Real Hardware Mode
```
./start_dtp.sh -r
```
Startet:
- CAN-Bus Pipelines (piper control)
- Real Hardware Controller
- MoveIt2 (mit realen Joint States)
- RViz2
- ros2_control (real hardware)
⚠️ Aktuell noch nicht möglich

## Piper Roboter – wichtige Launchfiles
### MoveIt2 mit Fake-Hardware
```
ros2 launch piper_no_gripper_moveit controller_bringup.launch.py fake_hardware:=true
ros2 launch piper_no_gripper_moveit moveit_dt.launch.py
```

### Echtes Hardware-Bringup
```
ros2 launch piper start_single_piper.launch.py
```
### Gazebo Simulation
```
ros2 launch piper_gazebo piper_no_gripper_gazebo.launch.py
```

### Mujoco Simulation
```
ros2 run piper_mujoco piper_no_gripper_mujoco_ctrl.py
```

## Logitech G29 Integration
Das G29 wird über das Paket g29_isaac_bridge eingebunden.
Start:
```
ros2 run g29_isaac_bridge g29_bridge_node
```
Verfügbare Topics:
```
/wheel/steering_angle
/joy (je nach Konfiguration)
```
## Isaac Sim IntegrationFertig
Physikalisch korrektes G29
→ isaac/scenes/g29_rotate_right_tilted27degrees.usd
Mit:
- Korrektes Steering Joint
- 27° Tilt Alignment
- Richtige Masse/Collider
- Stabile physikalische Basis

## Branch Recovery
If you lost files on the gripper branch, you can restore them from history:

```bash
# Show recent commits on the gripper branch
git log --oneline gripper

# Show recent branch movements to find the last good commit
git reflog show gripper

# Restore a specific file from a prior commit
git checkout <commit-hash> -- path/to/file

# Restore the full branch to a known good commit
# Warning: git reset --hard discards uncommitted changes. Consider creating a backup branch first.
git checkout gripper
git reset --hard <commit-hash>
```

...
