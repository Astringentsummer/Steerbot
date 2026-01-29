@echo off
echo ========================================================
echo   ISAAC SIM - INTERACTIVE GUI DEMO
echo ========================================================
echo.
echo This will open Isaac Sim with a 3D scene
echo The window will stay open for 2 MINUTES
echo.
echo You will see:
echo   - A ground plane
echo   - 5 colorful cubes
echo.
echo Controls:
echo   - Right-click + drag to rotate camera
echo   - Scroll wheel to zoom
echo   - Ctrl+C to close early
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting Isaac Sim...
echo.
echo WATCH FOR THE WINDOW TO OPEN!
echo.

call "%ISAAC_PYTHON%" DEMO_WITH_CUBES.py

echo.
echo Demo complete!
pause
