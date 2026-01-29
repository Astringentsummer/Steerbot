@echo off
set "IsaacPath=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
set "ScriptPath=%~dp0isaac_piper_steering.py"

echo Starting Refined Virtual Steering Simulation (Lula IK)...
echo RTX Graphics and Physics Enabling...

set ROS_PACKAGE_PATH=c:\Users\rohit\Downloads\Steerbot-Gripper\piper_ros\src

"%IsaacPath%\python.bat" "%ScriptPath%"
pause
