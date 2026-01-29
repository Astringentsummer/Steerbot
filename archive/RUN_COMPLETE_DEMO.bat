@echo off
echo ========================================================
echo   COMPLETE ISAAC SIM DEMO
echo   Piper Arm + G29 Wheel + Animated Controller
echo ========================================================
echo.
echo This demo includes:
echo   - Table and steering wheel
echo   - Simplified Piper arm (3 links)
echo   - Animated IK controller
echo   - Real-time wheel turning
echo.
echo Starting Isaac Sim...
echo.

REM Use Isaac Sim's Python
set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% ISAAC_COMPLETE_DEMO.py

echo.
echo Demo stopped.
pause
