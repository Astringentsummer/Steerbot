@echo off
title Steerbot-Gripper: Full System Launcher
echo ========================================================
echo   STEERBOT-GRIPPER: G29 HARDWARE + ISAAC SIM INTEGRATION
echo ========================================================
echo.
echo [1/3] Checking environment...
set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat
if not exist "%ISAAC_PYTHON%" (
    echo ERROR: Isaac Sim python.bat not found at:
    echo %ISAAC_PYTHON%
    pause
    exit /b
)

echo [2/3] Starting G29 Hardware Bridge (UDP)...
start "G29 Bridge" cmd /k "python g29_bridge.py"

echo [3/3] Launching Isaac Sim Simulation...
echo This uses the VERIFIED WORKING version.
call "%ISAAC_PYTHON%" isaac_piper_steering_WORKING.py

echo.
echo Simulation exited. Closing Bridge...
taskkill /FI "WINDOWTITLE eq G29 Bridge" /F
echo Done.
pause
