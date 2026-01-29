@echo off
echo ========================================================
echo   ULTRA SIMPLE - EVERYTHING VISIBLE
echo ========================================================
echo.
echo You will CLEARLY see:
echo.
echo LEFT SIDE - Piper Arm:
echo   - Gray BASE cylinder
echo   - Red SHOULDER sphere
echo   - Blue LINK 1 cylinder
echo   - Yellow ELBOW sphere
echo   - Green LINK 2 cylinder
echo   - Cyan WRIST sphere
echo.
echo RIGHT SIDE:
echo   - Black STEERING WHEEL
echo   - Orange GRIPPER (outside wheel)
echo   - Two orange FINGERS
echo.
echo Static view - no animation, just structure!
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% ULTRA_SIMPLE_DEMO.py

pause
