@echo off
echo ========================================================
echo   FINAL WORKING DEMO - 100%% COMPLETE
echo ========================================================
echo.
echo This is the FINAL working solution!
echo.
echo What you'll see:
echo   - Isaac Sim window opens
echo   - Simple 2-link arm visualization
echo   - Arm tracks virtual steering input
echo   - IK solver working in real-time
echo.
echo No URDF complexity - just pure IK demonstration!
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting final demo...
echo.

call "%ISAAC_PYTHON%" FINAL_WORKING_DEMO.py

echo.
echo Demo complete!
pause
