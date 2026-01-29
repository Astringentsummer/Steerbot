#!/usr/bin/env python3
"""
Gymnasium Environment for Piper Arm + G29 Steering Control
Supports training with PPO, SAC, and TD3 algorithms
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any

# Basic imports only - Isaac Sim imports happen AFTER SimulationApp is created
import sys
import os
ISAAC_SIM_PATH = r"C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64"
sys.path.insert(0, os.path.join(ISAAC_SIM_PATH, "python_packages"))


class PiperG29Environment(gym.Env):
    """
    Custom Gymnasium environment for training RL policies on Piper arm
    to track G29 steering wheel movements.
    
    Observation Space (18D):
        - Steering angle (1D): [-90, 90] degrees
        - Steering velocity (1D): angular velocity
        - Joint positions (6D): current arm configuration
        - Joint velocities (6D): current joint speeds
        - Target position (3D): where end-effector should be
        - Distance to target (1D): tracking error
    
    Action Space (6D):
        - Joint position deltas: [-1, 1] normalized
        - Mapped to actual joint limits
    
    Reward Function:
        - Distance penalty: -10 * ||pos - target||²
        - Smoothness: -0.5 * ||velocity||²
        - Energy: -0.1 * ||torque||²
        - Success bonus: +10 if within 2cm
        - Collision penalty: -100
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(
        self,
        render_mode: Optional[str] = None,
        headless: bool = False,
        max_episode_steps: int = 500
    ):
        super().__init__()
        
        self.render_mode = render_mode
        self.max_episode_steps = max_episode_steps
        self.current_step = 0
        
        # Initialize Isaac Sim FIRST
        config = {"headless": headless, "width": 1920, "height": 1080}
        from isaacsim import SimulationApp
        self.simulation_app = SimulationApp(config)
        
        # NOW import Isaac Sim modules (after SimulationApp is created)
        from omni.isaac.core import World
        from omni.isaac.core.articulations import Articulation
        from omni.isaac.core.objects import FixedCuboid
        from pxr import UsdPhysics, UsdGeom, Gf, Sdf
        import omni.usd
        
        # Store imports as instance variables
        self.World = World
        self.Articulation = Articulation
        self.FixedCuboid = FixedCuboid
        self.UsdPhysics = UsdPhysics
        self.UsdGeom = UsdGeom
        self.Gf = Gf
        self.Sdf = Sdf
        self.omni_usd = omni.usd
        
        # Create world
        self.world = World(physics_dt=1.0/60.0, rendering_dt=1.0/60.0)
        self._setup_scene()
        
        # Define observation space (18D)
        self.observation_space = spaces.Box(
            low=np.array([
                -90.0,      # steering angle
                -180.0,     # steering velocity
                -np.pi, -np.pi, -np.pi, -np.pi, -np.pi, -np.pi,  # joint positions
                -10.0, -10.0, -10.0, -10.0, -10.0, -10.0,        # joint velocities
                -2.0, -2.0, 0.0,    # target position
                0.0             # distance to target
            ], dtype=np.float32),
            high=np.array([
                90.0,       # steering angle
                180.0,      # steering velocity
                np.pi, np.pi, np.pi, np.pi, np.pi, np.pi,  # joint positions
                10.0, 10.0, 10.0, 10.0, 10.0, 10.0,        # joint velocities
                2.0, 2.0, 2.0,      # target position
                2.0             # distance to target
            ], dtype=np.float32),
            dtype=np.float32
        )
        
        # Define action space (6D joint deltas)
        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(6,),
            dtype=np.float32
        )
        
        # State variables
        self.steering_angle = 0.0
        self.steering_velocity = 0.0
        self.target_position = np.zeros(3)
        
    def _setup_scene(self):
        """Create the simulation scene"""
        # Add ground plane
        self.world.scene.add_default_ground_plane()
        
        # Create table
        table = self.FixedCuboid(
            prim_path="/World/Table",
            name="table",
            size=np.array([1.2, 0.8, 0.05]),
            position=np.array([0.0, 0.0, 0.4]),
            color=np.array([0.6, 0.4, 0.2])
        )
        self.world.scene.add(table)
        
        # Create steering wheel base
        wheel_base = self.FixedCuboid(
            prim_path="/World/WheelBase",
            name="wheel_base",
            size=np.array([0.15, 0.15, 0.2]),
            position=np.array([0.3, 0.0, 0.525]),
            color=np.array([0.1, 0.1, 0.1])
        )
        self.world.scene.add(wheel_base)
        
        # Create steering wheel with revolute joint
        stage = self.omni_usd.get_context().get_stage()
        wheel_path = "/World/SteeringWheel"
        wheel_prim = stage.DefinePrim(wheel_path, "Xform")
        
        cylinder_path = wheel_path + "/WheelMesh"
        cylinder = self.UsdGeom.Cylinder.Define(stage, cylinder_path)
        cylinder.GetRadiusAttr().Set(0.15)
        cylinder.GetHeightAttr().Set(0.04)
        cylinder.GetAxisAttr().Set("Z")
        
        xform = self.UsdGeom.Xformable(wheel_prim)
        xform.AddTranslateOp().Set(self.Gf.Vec3d(0.3, 0.0, 0.625))
        
        self.UsdPhysics.RigidBodyAPI.Apply(wheel_prim)
        mass_api = self.UsdPhysics.MassAPI.Apply(wheel_prim)
        mass_api.GetMassAttr().Set(0.5)
        
        self.UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(cylinder_path))
        
        # Create revolute joint
        joint_path = "/World/WheelJoint"
        joint = self.UsdPhysics.RevoluteJoint.Define(stage, joint_path)
        joint.CreateBody0Rel().SetTargets([self.Sdf.Path("/World/WheelBase")])
        joint.CreateBody1Rel().SetTargets([self.Sdf.Path(wheel_path)])
        joint.CreateAxisAttr("Z")
        joint.CreateLowerLimitAttr(-90)
        joint.CreateUpperLimitAttr(90)
        joint.CreateLocalPos0Attr().Set(self.Gf.Vec3f(0, 0, 0.1))
        joint.CreateLocalRot0Attr().Set(self.Gf.Quatf(1, 0, 0, 0))
        joint.CreateLocalPos1Attr().Set(self.Gf.Vec3f(0, 0, 0))
        joint.CreateLocalRot1Attr().Set(self.Gf.Quatf(1, 0, 0, 0))
        
        # Add drive
        self.drive_api = self.UsdPhysics.DriveAPI.Apply(stage.GetPrimAtPath(joint_path), "angular")
        self.drive_api.CreateTypeAttr("force")
        self.drive_api.CreateDampingAttr(100.0)
        self.drive_api.CreateStiffnessAttr(10000.0)
        self.drive_api.CreateMaxForceAttr(1000.0)
        
        # Import Piper arm
        from isaacsim.asset.importer.urdf import _urdf
        import omni.kit.commands
        
        urdf_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description/urdf/piper_description.urdf"
        import_config = _urdf.ImportConfig()
        import_config.merge_fixed_joints = False
        import_config.fix_base = True
        
        status, piper_path = omni.kit.commands.execute(
            "URDFParseAndImportFile",
            urdf_path=urdf_path,
            import_config=import_config,
        )
        
        # Position arm
        piper_prim = stage.GetPrimAtPath(piper_path)
        xformable = self.UsdGeom.Xformable(piper_prim)
        xformable.ClearXformOpOrder()
        xformable.AddTranslateOp().Set(self.Gf.Vec3d(-0.3, 0.0, 0.425))
        
        self.piper_arm = self.Articulation(prim_path=piper_path)
        self.world.scene.add(self.piper_arm)
        
        # Reset world
        self.world.reset()
        
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset the environment"""
        super().reset(seed=seed)
        
        self.current_step = 0
        
        # Random initial steering angle
        self.steering_angle = self.np_random.uniform(-45, 45)
        self.steering_velocity = 0.0
        
        # Set steering wheel position
        if self.drive_api:
            self.drive_api.GetTargetPositionAttr().Set(float(self.steering_angle))
        
        # Reset arm to default pose
        init_pos = np.array([0.0, -0.3, 0.5, 0.0, 0.5, 0.0])
        self.piper_arm.set_joint_positions(init_pos)
        
        # Step simulation to settle
        for _ in range(10):
            self.world.step(render=False)
        
        # Calculate target position
        self._update_target_position()
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(
        self, action: np.ndarray
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute one step"""
        self.current_step += 1
        
        # Apply action (joint position deltas)
        current_positions = self.piper_arm.get_joint_positions()
        
        # Scale action from [-1, 1] to actual joint limits
        action_scaled = action * 0.1  # Max 0.1 radian change per step
        new_positions = np.clip(
            current_positions + action_scaled,
            -np.pi, np.pi
        )
        
        self.piper_arm.set_joint_positions(new_positions)
        
        # Update steering (simulate changing input)
        self.steering_velocity = self.np_random.uniform(-5, 5)
        self.steering_angle += self.steering_velocity * (1.0/60.0)
        self.steering_angle = np.clip(self.steering_angle, -90, 90)
        
        if self.drive_api:
            self.drive_api.GetTargetPositionAttr().Set(float(self.steering_angle))
        
        # Step simulation
        self.world.step(render=(self.render_mode == "human"))
        
        # Update target
        self._update_target_position()
        
        # Calculate reward
        observation = self._get_observation()
        reward = self._calculate_reward(observation, action)
        
        # Check termination
        terminated = self._is_terminated(observation)
        truncated = self.current_step >= self.max_episode_steps
        
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation"""
        joint_positions = self.piper_arm.get_joint_positions()
        joint_velocities = self.piper_arm.get_joint_velocities()
        
        # Get end-effector position
        ee_position, _ = self.piper_arm.get_world_pose()
        
        # Calculate distance to target
        distance = np.linalg.norm(ee_position - self.target_position)
        
        observation = np.concatenate([
            [self.steering_angle],
            [self.steering_velocity],
            joint_positions,
            joint_velocities,
            self.target_position,
            [distance]
        ]).astype(np.float32)
        
        return observation
    
    def _update_target_position(self):
        """Calculate target position on steering wheel rim"""
        wheel_center = np.array([0.3, 0.0, 0.625])
        wheel_radius = 0.15
        target_rad = np.radians(self.steering_angle)
        
        angle_offset = np.radians(45)
        total_angle = target_rad + angle_offset
        
        local_target = np.array([
            wheel_radius * np.sin(total_angle),
            wheel_radius * np.cos(total_angle),
            0
        ])
        
        self.target_position = wheel_center + local_target
    
    def _calculate_reward(self, observation: np.ndarray, action: np.ndarray) -> float:
        """Calculate reward"""
        distance = observation[-1]
        joint_velocities = observation[8:14]
        
        # Distance penalty (want to be close to target)
        distance_reward = -10.0 * (distance ** 2)
        
        # Smoothness penalty (want low velocities)
        smoothness_penalty = -0.5 * np.sum(joint_velocities ** 2)
        
        # Energy penalty (want small actions)
        energy_penalty = -0.1 * np.sum(action ** 2)
        
        # Success bonus
        success_bonus = 10.0 if distance < 0.02 else 0.0
        
        # Total reward
        reward = distance_reward + smoothness_penalty + energy_penalty + success_bonus
        
        return float(reward)
    
    def _is_terminated(self, observation: np.ndarray) -> bool:
        """Check if episode should terminate"""
        distance = observation[-1]
        
        # Terminate if too far from target
        if distance > 0.5:
            return True
        
        return False
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional info"""
        return {
            "steering_angle": self.steering_angle,
            "steering_velocity": self.steering_velocity,
            "target_position": self.target_position.copy(),
            "current_step": self.current_step
        }
    
    def render(self):
        """Render the environment"""
        if self.render_mode == "human":
            # Isaac Sim handles rendering
            pass
        elif self.render_mode == "rgb_array":
            # TODO: Capture camera image
            pass
    
    def close(self):
        """Clean up"""
        if hasattr(self, 'simulation_app'):
            self.simulation_app.close()


# Test the environment
if __name__ == "__main__":
    print("Testing Piper G29 Environment...")
    
    env = PiperG29Environment(render_mode="human", headless=False)
    
    print("Observation space:", env.observation_space)
    print("Action space:", env.action_space)
    
    obs, info = env.reset()
    print(f"\nInitial observation shape: {obs.shape}")
    print(f"Initial info: {info}")
    
    print("\nRunning 100 random steps...")
    for i in range(100):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 20 == 0:
            print(f"Step {i}: Reward={reward:.2f}, Distance={obs[-1]:.3f}m")
        
        if terminated or truncated:
            print(f"Episode ended at step {i}")
            obs, info = env.reset()
    
    env.close()
    print("\nEnvironment test complete!")
