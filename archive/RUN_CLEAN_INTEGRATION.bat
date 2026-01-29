@echo off
echo ========================================================
echo   CLEAN G29 + PIPER ARM INTEGRATION
echo ========================================================
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [1/2] Starting G29 Hardware Bridge (UDP)...
start "G29 Bridge" cmd /k "python g29_bridge.py"

timeout /t 2 /nobreak > nul

echo [2/2] Launching Clean Integration...
echo.
echo This builds the scene from scratch (no broken USD files)
echo.

call "%ISAAC_PYTHON%" CLEAN_G29_PIPER.py

echo.
echo Integration closed.
pause
