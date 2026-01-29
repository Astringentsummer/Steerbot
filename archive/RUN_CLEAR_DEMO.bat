@echo off
echo ========================================================
echo   GRIPPER TOUCHING AND TURNING THE WHEEL
echo ========================================================
echo.
echo You will CLEARLY see:
echo   - Orange gripper TOUCHING the wheel rim
echo   - Gripper PUSHING the wheel
echo   - Wheel ROTATING as gripper moves
echo   - Arm reaching from left to wheel
echo.
echo This shows the ACTUAL control!
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% CLEAR_GRIPPER_WHEEL_DEMO.py

pause
