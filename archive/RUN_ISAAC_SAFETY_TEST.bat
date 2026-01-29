@echo off
echo ========================================================
echo   ISAAC SIM - PROFESSIONAL SAFETY SIMULATION
echo ========================================================
echo.
echo This uses REAL PHYSICS SIMULATION to validate safety
echo before deploying to real hardware.
echo.
echo Features:
echo   - Full physics engine (60 Hz)
echo   - Collision detection
echo   - Joint limit checking
echo   - Speed limit validation
echo   - Professional robotics simulation
echo.
echo Starting Isaac Sim...
echo.

REM Use Isaac Sim's Python
set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% ISAAC_SAFE_SIMULATION.py

echo.
echo Simulation complete.
pause
