@echo off
echo ========================================================
echo   G29 + PIPER ARM - SIMPLIFIED VERSION
echo ========================================================
echo.
echo This is a working version that avoids API issues
echo.
echo Features:
echo   - G29 steering wheel input (UDP port 5006)
echo   - Piper arm with IK control
echo   - Real-time tracking
echo.
echo Make sure G29 is plugged in!
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting system...
echo.

call "%ISAAC_PYTHON%" G29_PIPER_SIMPLE.py

echo.
echo System stopped.
pause
