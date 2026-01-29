"""
Kalman Filter for Robot State Estimation
Fuses noisy sensor data for smooth, accurate state tracking
"""

import numpy as np
from filterpy.kalman import KalmanFilter


class RobotStateEstimator:
    """
    Extended Kalman Filter for robot state estimation
    
    State vector: [positions, velocities, accelerations]
    Measurement: [positions] (from encoders)
    
    Features:
    - Filters sensor noise
    - Predicts future states
    - Handles missing measurements
    - Adaptive noise estimation
    """
    
    def __init__(self, num_joints=6, dt=0.016):
        """
        Args:
            num_joints: Number of robot joints
            dt: Time step (seconds), default 60 Hz
        """
        self.num_joints = num_joints
        self.dt = dt
        
        # State: [positions, velocities, accelerations]
        dim_x = num_joints * 3
        dim_z = num_joints  # Measurements: positions only
        
        self.kf = KalmanFilter(dim_x=dim_x, dim_z=dim_z)
        
        # State transition matrix (constant acceleration model)
        self.kf.F = np.eye(dim_x)
        for i in range(num_joints):
            # position += velocity * dt + 0.5 * acceleration * dt^2
            self.kf.F[i, num_joints + i] = dt
            self.kf.F[i, 2*num_joints + i] = 0.5 * dt**2
            
            # velocity += acceleration * dt
            self.kf.F[num_joints + i, 2*num_joints + i] = dt
            
        # Measurement matrix (observe positions only)
        self.kf.H = np.zeros((dim_z, dim_x))
        self.kf.H[:num_joints, :num_joints] = np.eye(num_joints)
        
        # Process noise covariance (how much we trust the model)
        # Higher values = trust model less, adapt faster to changes
        q = 0.01
        self.kf.Q = np.eye(dim_x) * q
        
        # Measurement noise covariance (how much we trust sensors)
        # Higher values = trust sensors less, smoother output
        r = 0.1
        self.kf.R = np.eye(dim_z) * r
        
        # Initial state covariance
        self.kf.P = np.eye(dim_x) * 100
        
        # Initial state
        self.kf.x = np.zeros(dim_x)
        
        # Statistics for adaptive noise estimation
        self.innovation_history = []
        self.max_history = 100
        
    def predict(self):
        """
        Predict next state based on motion model
        
        Returns:
            predicted_positions: (num_joints,) array
        """
        self.kf.predict()
        return self.kf.x[:self.num_joints]
        
    def update(self, measured_positions):
        """
        Update state estimate with sensor measurement
        
        Args:
            measured_positions: (num_joints,) array from encoders
            
        Returns:
            estimated_positions: (num_joints,) filtered positions
        """
        self.kf.update(measured_positions)
        
        # Store innovation for adaptive noise estimation
        innovation = measured_positions - self.kf.H @ self.kf.x
        self.innovation_history.append(innovation)
        if len(self.innovation_history) > self.max_history:
            self.innovation_history.pop(0)
            
        # Adapt measurement noise if needed
        self._adapt_noise()
        
        return self.kf.x[:self.num_joints]
        
    def get_velocity_estimate(self):
        """
        Get estimated joint velocities
        
        Returns:
            velocities: (num_joints,) array
        """
        return self.kf.x[self.num_joints:2*self.num_joints]
        
    def get_acceleration_estimate(self):
        """
        Get estimated joint accelerations
        
        Returns:
            accelerations: (num_joints,) array
        """
        return self.kf.x[2*self.num_joints:]
        
    def get_full_state(self):
        """
        Get complete state estimate
        
        Returns:
            dict with positions, velocities, accelerations
        """
        return {
            'positions': self.kf.x[:self.num_joints],
            'velocities': self.kf.x[self.num_joints:2*self.num_joints],
            'accelerations': self.kf.x[2*self.num_joints:],
            'covariance': self.kf.P
        }
        
    def _adapt_noise(self):
        """
        Adaptive noise estimation based on innovation sequence
        Adjusts R (measurement noise) based on recent innovations
        """
        if len(self.innovation_history) < 10:
            return
            
        # Calculate innovation covariance
        innovations = np.array(self.innovation_history[-10:])
        innovation_cov = np.cov(innovations.T)
        
        # Expected innovation covariance: H*P*H' + R
        expected_cov = self.kf.H @ self.kf.P @ self.kf.H.T + self.kf.R
        
        # If actual innovation is much larger, increase R (trust sensors less)
        ratio = np.trace(innovation_cov) / np.trace(expected_cov)
        
        if ratio > 1.5:  # Innovation too large
            self.kf.R *= 1.1  # Increase measurement noise
        elif ratio < 0.5:  # Innovation too small
            self.kf.R *= 0.9  # Decrease measurement noise
            
        # Clamp R to reasonable bounds
        self.kf.R = np.clip(self.kf.R, 0.01, 10.0)
        
    def reset(self, initial_positions=None):
        """
        Reset filter to initial state
        
        Args:
            initial_positions: Optional initial joint positions
        """
        if initial_positions is not None:
            self.kf.x[:self.num_joints] = initial_positions
        else:
            self.kf.x = np.zeros(self.num_joints * 3)
            
        self.kf.P = np.eye(self.num_joints * 3) * 100
        self.innovation_history = []


# Example usage
if __name__ == "__main__":
    """Test the state estimator with simulated noisy data"""
    import matplotlib.pyplot as plt
    
    # Create estimator
    estimator = RobotStateEstimator(num_joints=6, dt=0.016)
    
    # Simulate noisy sensor data
    true_positions = []
    measured_positions = []
    estimated_positions = []
    estimated_velocities = []
    
    t = 0
    for i in range(500):
        # True position (sine wave)
        true_pos = np.sin(2 * np.pi * 0.5 * t) * np.ones(6)
        
        # Noisy measurement
        noise = np.random.normal(0, 0.1, 6)
        measured_pos = true_pos + noise
        
        # Predict and update
        estimator.predict()
        estimated_pos = estimator.update(measured_pos)
        estimated_vel = estimator.get_velocity_estimate()
        
        # Store for plotting
        true_positions.append(true_pos[0])
        measured_positions.append(measured_pos[0])
        estimated_positions.append(estimated_pos[0])
        estimated_velocities.append(estimated_vel[0])
        
        t += 0.016
        
    # Plot results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(true_positions, 'g-', label='True', linewidth=2)
    plt.plot(measured_positions, 'r.', label='Measured (noisy)', alpha=0.5)
    plt.plot(estimated_positions, 'b-', label='Estimated (filtered)', linewidth=2)
    plt.legend()
    plt.ylabel('Position (rad)')
    plt.title('Kalman Filter State Estimation')
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    true_velocities = np.gradient(true_positions, 0.016)
    plt.plot(true_velocities, 'g-', label='True velocity', linewidth=2)
    plt.plot(estimated_velocities, 'b-', label='Estimated velocity', linewidth=2)
    plt.legend()
    plt.ylabel('Velocity (rad/s)')
    plt.xlabel('Time step')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('kalman_filter_test.png')
    print("Test plot saved to kalman_filter_test.png")
    
    # Print statistics
    position_error = np.array(estimated_positions) - np.array(true_positions)
    print(f"\nPosition estimation error:")
    print(f"  Mean: {np.mean(np.abs(position_error)):.4f} rad")
    print(f"  Std:  {np.std(position_error):.4f} rad")
    print(f"  Max:  {np.max(np.abs(position_error)):.4f} rad")
