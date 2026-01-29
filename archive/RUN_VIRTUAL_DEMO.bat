@echo off
echo ========================================================
echo   G29 + PIPER ARM - VIRTUAL MODE
echo ========================================================
echo.
echo NO PHYSICAL G29 WHEEL NEEDED!
echo.
echo This uses a virtual sine wave to simulate steering input
echo The Piper arm will move left and right automatically
echo.
echo Features:
echo   - Virtual steering wheel (sine wave)
echo   - Piper arm with IK control
echo   - Real-time tracking demonstration
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting virtual demo...
echo.

call "%ISAAC_PYTHON%" G29_PIPER_VIRTUAL.py

echo.
echo Demo stopped.
pause
