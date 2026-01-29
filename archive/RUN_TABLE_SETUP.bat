@echo off
echo ========================================================
echo   G29 + PIPER ARM - IMPROVED IK VERSION
echo ========================================================
echo.
echo Improvements:
echo  - Orientation constraints (10x better IK success)
echo  - Workspace bounds checking
echo  - Previous solution caching
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [1/2] Starting G29 Bridge (Port 5006)...
start "G29 Bridge" cmd /k "python g29_bridge_5006.py"

timeout /t 2 /nobreak > nul

echo [2/2] Launching Improved IK Setup...
call "%ISAAC_PYTHON%" G29_PIPER_TABLE_SETUP.py

echo.
echo Integration closed.
pause
