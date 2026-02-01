import os
import subprocess
import time
import webbrowser

# ==============================================================================
# MASTER 3D DIGITAL TWIN LAUNCHER (Windows Bridge)
# ==============================================================================

def launch_3d_demo():
    print("="*60)
    print(" HICTP | HIGH-FIDELITY 3D DIGITAL TWIN ")
    print("="*60)
    
    # 1. Launch Headless Simulation in WSL
    print("[1/2] - Triggering Isaac Sim 5.0 Engine (WSL2 Headless)...")
    
    # Using a robust PowerShell invocation to handle quoting
    wsl_cmd = 'wsl -u root bash -c \\\"cd /root/projects/Steerbot-Gripper/Steerbot-Gripper && ./launch_digital_twin.sh\\\"'
    full_cmd = f'powershell -NoExit -Command "Start-Process powershell -ArgumentList \'-NoExit\', \'-Command\', \'{wsl_cmd}\'"'
    
    subprocess.Popen(full_cmd, shell=True)
    
    # 2. Open high-fidelity WebGL HUD
    print("[2/2] - Pre-loading WebGL 3D Visualization...")
    time.sleep(2) # Give simulation a moment to start
    
    hud_path = os.path.abspath("visualization_3d.html")
    webbrowser.open(f"file://{hud_path}")
    
    print("\n[SUCCESS] - System Active.")
    print("-> Monitor the 'Isaac Sim' terminal for Physics logs.")
    print("-> Use the 'Chrome/Edge' window for 3D Graphics.")
    print("="*60)

if __name__ == "__main__":
    launch_3d_demo()
