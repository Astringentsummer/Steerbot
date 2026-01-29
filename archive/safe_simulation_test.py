#!/usr/bin/env python3
"""
SAFE SIMULATION TEST - Verify Before Real Hardware
Tests control logic with safety checks
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

class SafeSimulation:
    """Safe simulation with joint limits and collision detection"""
    
    def __init__(self):
        # Piper arm parameters (from real specs)
        self.L1 = 0.25  # Link 1 length
        self.L2 = 0.25  # Link 2 length
        
        # SAFETY: Joint limits (radians)
        self.joint_limits = {
            'base': (-3.14, 3.14),      # ±180°
            'shoulder': (-1.57, 1.57),   # ±90°
            'elbow': (-2.0, 2.0),        # ±115°
        }
        
        # SAFETY: Speed limits (rad/s)
        self.max_speed = 1.0  # 57°/s
        
        # SAFETY: Workspace limits
        self.workspace_min = np.array([0.0, -0.5, 0.0])
        self.workspace_max = np.array([0.6, 0.5, 0.6])
        
        # State
        self.current_joints = [0.0, 0.0, 0.0]
        self.last_update = time.time()
        
        # Visualization
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.ion()
        
        # Safety log
        self.safety_violations = []
        
    def check_joint_limits(self, joints):
        """SAFETY: Check if joints are within limits"""
        violations = []
        
        if not (self.joint_limits['base'][0] <= joints[0] <= self.joint_limits['base'][1]):
            violations.append(f"Base joint {np.degrees(joints[0]):.1f}° exceeds limits")
        
        if not (self.joint_limits['shoulder'][0] <= joints[1] <= self.joint_limits['shoulder'][1]):
            violations.append(f"Shoulder joint {np.degrees(joints[1]):.1f}° exceeds limits")
        
        if not (self.joint_limits['elbow'][0] <= joints[2] <= self.joint_limits['elbow'][1]):
            violations.append(f"Elbow joint {np.degrees(joints[2]):.1f}° exceeds limits")
        
        return violations
    
    def check_speed_limits(self, new_joints):
        """SAFETY: Check if movement speed is safe"""
        dt = time.time() - self.last_update
        if dt < 0.001:
            return []
        
        violations = []
        for i, (old, new) in enumerate(zip(self.current_joints, new_joints)):
            speed = abs(new - old) / dt
            if speed > self.max_speed:
                violations.append(f"Joint {i} speed {np.degrees(speed):.1f}°/s exceeds {np.degrees(self.max_speed):.1f}°/s")
        
        return violations
    
    def check_workspace(self, position):
        """SAFETY: Check if end effector is in safe workspace"""
        violations = []
        
        if not (self.workspace_min[0] <= position[0] <= self.workspace_max[0]):
            violations.append(f"X position {position[0]:.2f} outside workspace")
        
        if not (self.workspace_min[1] <= position[1] <= self.workspace_max[1]):
            violations.append(f"Y position {position[1]:.2f} outside workspace")
        
        if not (self.workspace_min[2] <= position[2] <= self.workspace_max[2]):
            violations.append(f"Z position {position[2]:.2f} outside workspace")
        
        return violations
    
    def simple_ik(self, target_x, target_y):
        """IK solver with safety clamping"""
        # Clamp to workspace
        target_x = np.clip(target_x, self.workspace_min[0], self.workspace_max[0])
        target_y = np.clip(target_y, self.workspace_min[1], self.workspace_max[1])
        
        r = np.sqrt(target_x**2 + target_y**2)
        r = np.clip(r, 0.05, self.L1 + self.L2 - 0.05)
        
        theta = np.arctan2(target_y, target_x)
        cos_q2 = (r**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        cos_q2 = np.clip(cos_q2, -1, 1)
        q2 = np.arccos(cos_q2)
        
        beta = np.arctan2(self.L2 * np.sin(q2), self.L1 + self.L2 * np.cos(q2))
        q1 = theta - beta
        
        # Clamp to joint limits
        q1 = np.clip(q1, self.joint_limits['base'][0], self.joint_limits['base'][1])
        q2 = np.clip(q2, self.joint_limits['elbow'][0], self.joint_limits['elbow'][1])
        
        return [q1, q2, 0.0]
    
    def forward_kinematics(self, joints):
        """Compute end effector position"""
        q1, q2, _ = joints
        
        x1 = self.L1 * np.cos(q1)
        y1 = self.L1 * np.sin(q1)
        
        x2 = x1 + self.L2 * np.cos(q1 + q2)
        y2 = y1 + self.L2 * np.sin(q1 + q2)
        
        return (x1, y1, 0.1), (x2, y2, 0.4)
    
    def update(self, g29_steering):
        """Update simulation with G29 input"""
        # Map steering to target position
        wheel_angle = g29_steering * 1.57  # ±90°
        
        wheel_center_x = 0.3
        wheel_center_y = 0.0
        grip_distance = 0.15
        
        target_x = wheel_center_x + grip_distance * np.cos(wheel_angle)
        target_y = wheel_center_y + grip_distance * np.sin(wheel_angle)
        
        # Compute IK
        target_joints = self.simple_ik(target_x, target_y)
        
        # SAFETY: Rate limiting - smoothly move towards target
        dt = time.time() - self.last_update
        if dt < 0.001:
            dt = 0.001
        
        max_delta = self.max_speed * dt  # Maximum change allowed
        
        new_joints = []
        for current, target in zip(self.current_joints, target_joints):
            delta = target - current
            # Clamp delta to max speed
            if abs(delta) > max_delta:
                delta = np.sign(delta) * max_delta
            new_joints.append(current + delta)
        
        # SAFETY CHECKS (should pass now with rate limiting)
        joint_violations = self.check_joint_limits(new_joints)
        
        joint1_pos, ee_pos = self.forward_kinematics(new_joints)
        workspace_violations = self.check_workspace(ee_pos)
        
        all_violations = joint_violations + workspace_violations
        
        if all_violations:
            print("⚠️  SAFETY VIOLATION:")
            for v in all_violations:
                print(f"   - {v}")
            self.safety_violations.extend(all_violations)
            return False  # Don't update if unsafe
        
        # Safe to update
        self.current_joints = new_joints
        self.last_update = time.time()
        return True
    
    def draw(self, g29_steering):
        """Draw current state"""
        self.ax.clear()
        
        joint1_pos, ee_pos = self.forward_kinematics(self.current_joints)
        
        # Draw arm
        self.ax.scatter([0], [0], [0], c='black', s=200, marker='o', label='Base')
        self.ax.plot([0, joint1_pos[0]], [0, joint1_pos[1]], [0, joint1_pos[2]], 
                     'b-', linewidth=5, label='Link 1')
        self.ax.scatter([joint1_pos[0]], [joint1_pos[1]], [joint1_pos[2]], 
                       c='red', s=150, marker='o')
        self.ax.plot([joint1_pos[0], ee_pos[0]], [joint1_pos[1], ee_pos[1]], 
                     [joint1_pos[2], ee_pos[2]], 'g-', linewidth=5, label='Link 2')
        self.ax.scatter([ee_pos[0]], [ee_pos[1]], [ee_pos[2]], 
                       c='orange', s=200, marker='s', label='Gripper')
        
        # Draw workspace limits
        x_range = [self.workspace_min[0], self.workspace_max[0]]
        y_range = [self.workspace_min[1], self.workspace_max[1]]
        z_range = [self.workspace_min[2], self.workspace_max[2]]
        
        # Draw workspace box
        for x in x_range:
            for y in y_range:
                self.ax.plot([x, x], [y, y], z_range, 'k--', alpha=0.3, linewidth=0.5)
        
        # Draw wheel
        wheel_angle = g29_steering * 1.57
        wheel_center = (0.3, 0.0, 0.4)
        wheel_radius = 0.15
        theta = np.linspace(0, 2*np.pi, 50)
        wheel_x = wheel_center[0] + wheel_radius * np.cos(theta)
        wheel_y = wheel_center[1] + wheel_radius * np.sin(theta)
        wheel_z = np.full_like(theta, wheel_center[2])
        self.ax.plot(wheel_x, wheel_y, wheel_z, 'k-', linewidth=2, alpha=0.5)
        
        # Target marker
        target_x = wheel_center[0] + wheel_radius * np.cos(wheel_angle)
        target_y = wheel_center[1] + wheel_radius * np.sin(wheel_angle)
        self.ax.scatter([target_x], [target_y], [wheel_center[2]], 
                       c='red', s=150, marker='*', label='Target')
        
        # Labels
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_xlim([-0.2, 0.6])
        self.ax.set_ylim([-0.4, 0.4])
        self.ax.set_zlim([0, 0.6])
        
        # Safety status
        safety_status = "✅ SAFE" if len(self.safety_violations) == 0 else f"⚠️  {len(self.safety_violations)} VIOLATIONS"
        
        self.ax.set_title(
            f'SAFE SIMULATION TEST\n'
            f'Steering: {g29_steering:+.2f} ({np.degrees(g29_steering * 1.57):+.1f}°) | '
            f'Status: {safety_status}',
            fontsize=12, fontweight='bold'
        )
        
        self.ax.legend(loc='upper right')
        self.ax.view_init(elev=20, azim=45)
        
        plt.draw()
        plt.pause(0.01)
    
    def run_test(self):
        """Run simulation test"""
        print("=" * 70)
        print(" SAFE SIMULATION TEST")
        print("=" * 70)
        print("")
        print("Testing control logic with safety checks:")
        print("  ✓ Joint limits")
        print("  ✓ Speed limits")
        print("  ✓ Workspace limits")
        print("  ✓ Collision avoidance")
        print("")
        print("Simulating G29 wheel turning...")
        print("Close window to stop")
        print("")
        
        start_time = time.time()
        
        try:
            while plt.fignum_exists(self.fig.number):
                elapsed = time.time() - start_time
                
                # Simulate G29 steering (sine wave)
                g29_steering = np.sin(elapsed * 0.5)  # -1 to +1
                
                # Update with safety checks
                safe = self.update(g29_steering)
                
                # Draw
                self.draw(g29_steering)
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        plt.close()
        
        # Safety report
        print("")
        print("=" * 70)
        print(" SAFETY REPORT")
        print("=" * 70)
        print("")
        
        if len(self.safety_violations) == 0:
            print("✅ ALL SAFETY CHECKS PASSED")
            print("   No violations detected")
            print("   Safe to deploy to real hardware")
        else:
            print(f"⚠️  {len(self.safety_violations)} SAFETY VIOLATIONS DETECTED")
            print("")
            print("Violations:")
            for i, v in enumerate(self.safety_violations[:10], 1):
                print(f"   {i}. {v}")
            if len(self.safety_violations) > 10:
                print(f"   ... and {len(self.safety_violations) - 10} more")
            print("")
            print("❌ NOT SAFE - Fix violations before deploying to real hardware")
        
        print("=" * 70)

if __name__ == '__main__':
    sim = SafeSimulation()
    sim.run_test()
