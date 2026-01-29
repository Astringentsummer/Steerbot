@echo off
echo ========================================================
echo   LARGE VISIBLE DEMO - Everything 3-5x BIGGER!
echo ========================================================
echo.
echo You will clearly see:
echo   - LARGE brown table
echo   - LARGE black steering wheel
echo   - BIG RED target ball
echo   - BLUE arm link (thick)
echo   - GREEN arm link (thick)
echo   - ORANGE gripper cube (big)
echo.
echo Everything scaled up for visibility!
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% LARGE_ISAAC_DEMO.py

pause
