@echo off
echo ========================================================
echo   ADVANCED G29 + PIPER ARM DEMO
echo ========================================================
echo.
echo ADVANCED FEATURES:
echo   - Real Piper URDF (6-DOF)
echo   - Advanced IK solver
echo   - Gripper control (open/close)
echo   - Physics simulation
echo   - Collision detection
echo.
echo This is the production-ready version!
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting advanced demo...
echo.

call "%ISAAC_PYTHON%" ADVANCED_PIPER_DEMO.py

echo.
echo Advanced demo complete!
pause
