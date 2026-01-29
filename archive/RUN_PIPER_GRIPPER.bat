@echo off
echo ========================================================
echo   REAL PIPER ARM + MOCK GRIPPER
echo ========================================================
echo.
echo Loading:
echo   - Piper arm URDF (real robot model)
echo   - Mock gripper attached to wrist
echo   - G29 steering wheel
echo.
echo The gripper is attached to the Piper wrist!
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% PIPER_WITH_GRIPPER_DEMO.py

pause
