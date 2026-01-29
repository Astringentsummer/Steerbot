@echo off
echo ========================================================
echo   PIPER GRIPPER HOLDING STEERING WHEEL
echo ========================================================
echo.
echo NOW THE GRIPPER ACTUALLY HOLDS THE WHEEL!
echo.
echo What you'll see:
echo   - Table with steering wheel setup
echo   - Piper arm positioned to reach wheel
echo   - Gripper fingers GRIPPING the wheel
echo   - Arm follows as wheel rotates
echo.
echo This shows realistic gripper control!
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting gripper holding wheel demo...
echo.

call "%ISAAC_PYTHON%" GRIPPER_HOLDING_WHEEL.py

echo.
echo Demo complete!
pause
