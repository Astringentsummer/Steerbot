import json
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

# ==============================================================================
# 2D ANALYTICAL TELEMETRY VISUALIZER (Python Native)
# ==============================================================================

STATE_FILE = "digital_twin_state.json"

class Visualizer2D:
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.canvas.manager.set_window_title('HICTP | Analytical 2D Dashboard')
        
        # Data buffers
        self.time_data = []
        self.joint_data = [[] for _ in range(6)]
        self.force_data = []
        self.start_time = time.time()

        # Setup Plot 1: Joint Positions
        self.ax1.set_title("Robot Joint States (MoveIt2 -> Isaac)")
        self.ax1.set_ylabel("Angle (rad)")
        self.lines = [self.ax1.plot([], [], label=f"J{i+1}")[0] for i in range(6)]
        self.ax1.legend(loc='upper right', fontsize='x-small', ncol=3)
        self.ax1.grid(True, alpha=0.3)

        # Setup Plot 2: External Force / Haptic Feedback
        self.ax2.set_title("External Force Feedback (HICTP)")
        self.ax2.set_ylabel("Force (N)")
        self.ax2.set_xlabel("Time (s)")
        self.force_line, = self.ax2.plot([], [], color='red', label="$\tau_{ext}$")
        self.ax2.legend(loc='upper right')
        self.ax2.grid(True, alpha=0.3)

        plt.tight_layout()

    def update(self, frame):
        try:
            if not os.path.exists(STATE_FILE):
                # Show empty plot with waiting message
                self.ax1.set_title("Robot Joint States (Waiting for data...)")
                return self.lines + [self.force_line]

            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                
            curr_t = time.time() - self.start_time
            self.time_data.append(curr_t)
            
            # Update Joint Buffers - handle different data formats
            # Try to extract joint data from various possible formats
            joints = None
            if "joints" in data:
                joints = data["joints"]
            elif "gripper_xyz" in data:
                # Estimate joint angles from gripper position (simplified)
                xyz = data["gripper_xyz"]
                wheel_angle = data.get("wheel_angle", 0.0)
                # Create synthetic joint data for visualization
                joints = [
                    wheel_angle * 0.1,  # J1 (base rotation)
                    xyz[2] * 0.5,       # J2 (shoulder)
                    xyz[1] * 0.5,       # J3 (elbow)
                    0.0,                # J4 (wrist1)
                    wheel_angle * 0.05, # J5 (wrist2)
                    0.0                 # J6 (wrist3)
                ]
            else:
                joints = [0.0] * 6
            
            for i in range(6):
                self.joint_data[i].append(joints[i] if i < len(joints) else 0.0)
            
            # Update Force Buffer - estimate from gripper position
            gripper_pos = data.get("gripper_pos", 80.0)
            # Estimate force: closed gripper = higher force
            estimated_force = max(0, (80.0 - gripper_pos) * 0.5)
            self.force_data.append(estimated_force)

            # Keep only last 100 points (windowing)
            if len(self.time_data) > 100:
                self.time_data.pop(0)
                for i in range(6): self.joint_data[i].pop(0)
                self.force_data.pop(0)

            # Update Lines
            for i in range(6):
                self.lines[i].set_data(self.time_data, self.joint_data[i])
            
            self.force_line.set_data(self.time_data, self.force_data)

            # Auto-scale
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            
            # Update title with current phase
            phase = data.get("phase", "Running")
            self.ax1.set_title(f"Robot Joint States - {phase}")

        except Exception as e:
            print(f"Visualizer error: {e}")
            # Continue showing plot even with errors

        return self.lines + [self.force_line]

if __name__ == "__main__":
    viz = Visualizer2D()
    ani = FuncAnimation(viz.fig, viz.update, interval=50, blit=True)
    plt.show()
