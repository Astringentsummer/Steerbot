@echo off
echo ========================================================
echo   ISAAC SIM - PIPER ARM CONTROLS G29 WHEEL
echo ========================================================
echo.
echo Starting Isaac Sim with working demo...
echo.

REM Use Isaac Sim's Python (has all the modules)
set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

echo Using Isaac Sim Python: %PYTHON_EXE%
echo.

%PYTHON_EXE% ISAAC_SIM_WORKING.py

echo.
echo Demo stopped.
pause
