@echo off
echo ================================================================================
echo   Isaac Sim Demonstration
echo   Piper Arm with G29 Steering Wheel Control
echo ================================================================================
echo.
echo Features:
echo   - Steering wheel in vertical orientation
echo   - Wheel mounted on stand
echo   - Complete Piper arm structure with all joints
echo   - Realistic workspace table
echo   - Angled camera view
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% isaac_sim_demo.py

pause
