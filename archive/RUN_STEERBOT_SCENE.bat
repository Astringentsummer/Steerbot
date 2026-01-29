@echo off
echo ========================================================
echo   STEERBOT USD SCENE + PIPER ARM INTEGRATION
echo ========================================================
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [1/1] Launching Steerbot Isaac Sim Scene...
echo This will load the complete USD scene with G29 and Piper arm.
echo.

call "%ISAAC_PYTHON%" isaac_steerbot_integration.py

echo.
echo Scene closed.
pause
