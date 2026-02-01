@echo off
setlocal

title STEERBOT | KINEMATIC INTEGRATION PLATFORM
echo ============================================================
echo   STEERBOT: INTEGRATED KINEMATIC CORE (WSL)
echo ============================================================
echo.

:: 1. Initialize Physics Backend
echo [1/2] Launching Isaac Sim Physics Backend...
start "PHYSICS BACKEND" wsl -d Ubuntu bash -c "cd /mnt/c/Users/rohit/Downloads && ./python.sh /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/physics_backend.py"

:: 2. Wait for Initialization
echo      Synchronizing Middleware Environment...
timeout /t 45

:: 3. Initialize Kinematic Processor
echo [2/2] Launching Kinematic Processing Engine...
start "KINEMATIC PROCESSOR" wsl -d Ubuntu bash -c "cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper && source environment_setup.sh && python3 kinematic_processor.py"

echo.
echo ============================================================
echo   SYSTEM DEPLOYMENT SUCCESSFUL
echo ============================================================
pause
