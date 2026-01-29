@echo off
echo ========================================================
echo   RL TRAINING - SAC Algorithm
echo ========================================================
echo.
echo Training SAC on Piper G29 Environment
echo Expected time: ~2 hours on GPU
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Installing dependencies with Isaac Sim Python...
call "%ISAAC_PYTHON%" -m pip install stable-baselines3[extra] gymnasium torch tensorboard

echo.
echo Starting SAC training...
cd rl_training
call "%ISAAC_PYTHON%" train_sac.py --timesteps 500000

echo.
echo Training complete!
pause
