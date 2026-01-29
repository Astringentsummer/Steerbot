@echo off
echo ========================================================
echo   G29 + PIPER - WITH VISIBLE STEERING WHEEL
echo ========================================================
echo.
echo NOW YOU CAN SEE THE VIRTUAL STEERING WHEEL!
echo.
echo What you'll see:
echo   - LEFT: Virtual steering wheel rotating
echo   - RIGHT: Piper arm tracking the wheel
echo   - Real-time connection between them
echo.
echo The steering wheel will turn left and right
echo The arm will follow the wheel movement
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting demo with visible steering wheel...
echo.

call "%ISAAC_PYTHON%" DEMO_WITH_WHEEL.py

echo.
echo Demo complete!
pause
