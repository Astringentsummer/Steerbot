@echo off
echo ========================================================
echo   G29 + PIPER ARM - FULL INTEGRATION
echo ========================================================
echo.
echo This will start:
echo   1. G29 steering wheel bridge (UDP port 5006)
echo   2. Isaac Sim with Piper arm
echo   3. Real-time IK control
echo.
echo Make sure your G29 wheel is plugged in!
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting G29 + Piper Arm Integration...
echo.

call "%ISAAC_PYTHON%" G29_PIPER_TABLE_SETUP.py

echo.
echo Integration stopped.
pause
