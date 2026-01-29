@echo off
echo ========================================================
echo   COMPLETE G29 + PIPER ARM INTEGRATION
echo ========================================================
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [1/2] Starting G29 Hardware Bridge (UDP)...
start "G29 Bridge" cmd /k "python g29_bridge.py"

timeout /t 2 /nobreak > nul

echo [2/2] Launching Complete Integration...
echo.
echo This will:
echo  - Load G29 steering wheel scene
echo  - Import Piper arm with IK
echo  - Connect G29 input to arm control
echo.

call "%ISAAC_PYTHON%" FINAL_G29_PIPER_INTEGRATION.py

echo.
echo Integration closed.
pause
