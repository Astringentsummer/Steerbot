@echo off
REM WSL Environment Setup Launcher
echo ==========================================
echo Running WSL Environment Setup
echo ==========================================
echo.

wsl -d Ubuntu bash /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/setup_wsl_environment.sh

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
pause
