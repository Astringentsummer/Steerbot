@echo off
echo ========================================================
echo   PIPER GRIPPER CONTROLS G29 WHEEL - SIMPLE DEMO
echo ========================================================
echo.
echo You will see:
echo   - Brown table
echo   - Black steering wheel
echo   - Blue arm link
echo   - Green arm link  
echo   - Orange gripper cube
echo   - Red target marker
echo.
echo The orange gripper will turn the steering wheel!
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% SIMPLE_ISAAC_DEMO.py

pause
