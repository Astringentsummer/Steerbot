@echo off
echo ========================================================
echo   PERFECT DEMO - Everything ON the Table!
echo ========================================================
echo.
echo Fixed positioning:
echo   - Table at bottom (Z = 0 to 1.0)
echo   - All objects ABOVE table (Z = 1.8)
echo   - Piper arm ON table surface
echo   - G29 wheel ON table surface
echo   - Everything clearly visible!
echo.

set ISAAC_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set PYTHON_EXE=%ISAAC_PATH%\python.bat

%PYTHON_EXE% PERFECT_ISAAC_DEMO.py

pause
