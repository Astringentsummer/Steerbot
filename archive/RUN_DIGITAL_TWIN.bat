@echo off
echo ========================================================
echo   DIGITAL TWIN - ROS2 BRIDGE TEST
echo ========================================================
echo.
echo Testing bidirectional ROS2 communication
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [1/3] Checking ROS2 installation...
call "%ISAAC_PYTHON%" -c "import rclpy; print('ROS2 found!')"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: ROS2 not found!
    echo Installing ROS2 for Isaac Sim...
    call "%ISAAC_PYTHON%" -m pip install rclpy sensor_msgs geometry_msgs std_msgs
)

echo.
echo [2/3] Checking filterpy for Kalman filter...
call "%ISAAC_PYTHON%" -c "import filterpy; print('filterpy found!')"

if %ERRORLEVEL% NEQ 0 (
    echo Installing filterpy...
    call "%ISAAC_PYTHON%" -m pip install filterpy
)

echo.
echo [3/3] Starting Digital Twin ROS2 Bridge...
echo.
echo ROS2 Topics:
echo   Publishing to:
echo     - /piper/joint_commands
echo     - /g29/force_feedback
echo     - /digital_twin/state
echo.
echo   Subscribing to:
echo     - /piper/joint_states
echo     - /g29/state
echo.

cd digital_twin
call "%ISAAC_PYTHON%" isaac_ros2_bridge.py

pause
