"""
Isaac Gym Task for G29 + Piper Arm Control
Uses GPU-accelerated parallel environments for fast RL training
"""

from omni.isaac.gym.vec_env import VecEnvBase
import torch
import numpy as np
from omni.isaac.core.utils.torch.rotations import *
from omni.isaac.core.utils.torch.maths import *


class G29PiperTask(VecEnvBase):
    """
    Isaac Gym vectorized task for training Piper arm to track G29 steering wheel
    
    Features:
    - 512 parallel environments on GPU
    - 18D observation space (steering, joints, target)
    - 6D action space (joint deltas)
    - Reward: distance + smoothness + energy
    
    Training time: ~30 minutes for 10M steps (vs 50+ hours single-threaded)
    """
    
    def __init__(self, name, sim_config, env, offset=None):
        # Environment configuration
        self._num_envs = sim_config.task_config["env"]["numEnvs"]
        self._env_spacing = sim_config.task_config["env"]["envSpacing"]
        self._max_episode_length = sim_config.task_config["env"]["episodeLength"]
        
        # Observation and action spaces
        # 18 (original) + 4 (gripper pos/vel for 2 joints) = 22
        self._num_observations = 22
        # 6 (arm) + 1 (gripper) = 7
        self._num_actions = 7
        
        # Reward weights
        self.distance_weight = 10.0
        self.smoothness_weight = 0.5
        self.energy_weight = 0.1
        self.success_bonus = 10.0
        
        # Workspace bounds
        self.arm_base_pos = torch.tensor([-0.3, 0.0, 0.425], device="cuda:0")
        self.max_arm_reach = 0.65
        self.min_arm_reach = 0.15
        
        super().__init__(name, env, sim_config, offset)
        
        # Allocate buffers
        self.obs_buf = torch.zeros(
            (self._num_envs, self._num_observations),
            device=self._device,
            dtype=torch.float
        )
        
        self.rew_buf = torch.zeros(
            self._num_envs, device=self._device, dtype=torch.float
        )
        
        self.reset_buf = torch.ones(
            self._num_envs, device=self._device, dtype=torch.long
        )
        
        self.progress_buf = torch.zeros(
            self._num_envs, device=self._device, dtype=torch.long
        )
        
        # State tensors
        self.steering_angles = torch.zeros(
            self._num_envs, device=self._device, dtype=torch.float
        )
        
        self.steering_velocities = torch.zeros(
            self._num_envs, device=self._device, dtype=torch.float
        )
        
        self.target_positions = torch.zeros(
            (self._num_envs, 3), device=self._device, dtype=torch.float
        )
        
    def set_up_scene(self, scene) -> None:
        """
        Create the simulation scene with G29 wheel + Piper arm
        Instantiated num_envs times in parallel
        """
        from omni.isaac.core.utils.stage import add_reference_to_stage
        from omni.isaac.core.articulations import ArticulationView
        from omni.isaac.core.prims import RigidPrimView
        import omni.usd
        
        # Import URDF for Piper arm
        urdf_path = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description/urdf/piper_description.urdf"
        
        # Create environments
        for i in range(self._num_envs):
            env_path = f"/World/envs/env_{i}"
            
            # Create environment prim
            env_prim = scene.stage.DefinePrim(env_path, "Xform")
            
            # Set environment position (grid layout)
            from pxr import Gf
            row = i // int(np.sqrt(self._num_envs))
            col = i % int(np.sqrt(self._num_envs))
            pos = Gf.Vec3d(
                col * self._env_spacing,
                row * self._env_spacing,
                0.0
            )
            from pxr import UsdGeom
            xform = UsdGeom.Xformable(env_prim)
            xform.AddTranslateOp().Set(pos)
            
            # Add table (fixed)
            from omni.isaac.core.objects import FixedCuboid
            table = FixedCuboid(
                prim_path=f"{env_path}/Table",
                name=f"table_{i}",
                size=np.array([1.2, 0.8, 0.05]),
                position=np.array([0.0, 0.0, 0.4]),
                color=np.array([0.6, 0.4, 0.2])
            )
            scene.add(table)
            
            # Add steering wheel base
            wheel_base = FixedCuboid(
                prim_path=f"{env_path}/WheelBase",
                name=f"wheel_base_{i}",
                size=np.array([0.15, 0.15, 0.2]),
                position=np.array([0.3, 0.0, 0.525]),
                color=np.array([0.1, 0.1, 0.1])
            )
            scene.add(wheel_base)
            
            # Add steering wheel (revolute joint)
            self._create_steering_wheel(scene.stage, env_path)
            
            # Import Piper arm
            self._import_piper_arm(scene, env_path, urdf_path)
            
        # Create articulation views (batched access to all arms)
        self.piper_arms = ArticulationView(
            prim_paths_expr="/World/envs/env_*/piper_arm",
            name="piper_arms"
        )
        scene.add(self.piper_arms)
        
        # Create rigid prim view for steering wheels
        self.steering_wheels = RigidPrimView(
            prim_paths_expr="/World/envs/env_*/SteeringWheel",
            name="steering_wheels"
        )
        scene.add(self.steering_wheels)
        
        super().set_up_scene(scene)
        
    def _create_steering_wheel(self, stage, env_path):
        """Create steering wheel with revolute joint"""
        from pxr import UsdGeom, UsdPhysics, Gf, Sdf
        
        wheel_path = f"{env_path}/SteeringWheel"
        wheel_prim = stage.DefinePrim(wheel_path, "Xform")
        
        # Create cylinder mesh
        cylinder_path = wheel_path + "/WheelMesh"
        cylinder = UsdGeom.Cylinder.Define(stage, cylinder_path)
        cylinder.GetRadiusAttr().Set(0.15)
        cylinder.GetHeightAttr().Set(0.04)
        cylinder.GetAxisAttr().Set("Z")
        
        # Position
        xform = UsdGeom.Xformable(wheel_prim)
        xform.AddTranslateOp().Set(Gf.Vec3d(0.3, 0.0, 0.625))
        
        # Physics
        UsdPhysics.RigidBodyAPI.Apply(wheel_prim)
        mass_api = UsdPhysics.MassAPI.Apply(wheel_prim)
        mass_api.GetMassAttr().Set(0.5)
        
        UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(cylinder_path))
        
        # Revolute joint
        joint_path = f"{env_path}/WheelJoint"
        joint = UsdPhysics.RevoluteJoint.Define(stage, joint_path)
        joint.CreateBody0Rel().SetTargets([Sdf.Path(f"{env_path}/WheelBase")])
        joint.CreateBody1Rel().SetTargets([Sdf.Path(wheel_path)])
        joint.CreateAxisAttr("Z")
        joint.CreateLowerLimitAttr(-90)
        joint.CreateUpperLimitAttr(90)
        
    def _import_piper_arm(self, scene, env_path, urdf_path):
        """Import Piper arm URDF"""
        from isaacsim.asset.importer.urdf import _urdf
        import omni.kit.commands
        
        import_config = _urdf.ImportConfig()
        import_config.merge_fixed_joints = False
        import_config.fix_base = True
        
        status, piper_path = omni.kit.commands.execute(
            "URDFParseAndImportFile",
            urdf_path=urdf_path,
            import_config=import_config,
            dest_path=f"{env_path}/piper_arm"
        )
        
        # Position arm
        from pxr import UsdGeom, Gf
        piper_prim = scene.stage.GetPrimAtPath(piper_path)
        xformable = UsdGeom.Xformable(piper_prim)
        xformable.ClearXformOpOrder()
        xformable.AddTranslateOp().Set(Gf.Vec3d(-0.3, 0.0, 0.425))
        
    def get_observations(self) -> dict:
        """
        Compute observations for all environments
        Returns batched observations (num_envs x 22)
        """
        # Get joint states (batched)
        # Expecting 8 joints (6 arm + 2 gripper) from valid Piper URDF
        all_joint_positions = self.piper_arms.get_joint_positions(clone=False)  # (num_envs, 8)
        all_joint_velocities = self.piper_arms.get_joint_velocities(clone=False)  # (num_envs, 8)
        
        # Verify shape (fallback if URDF only has 6 joints, though unlikely if using correct URDF)
        if all_joint_positions.shape[1] < 8:
             # Pad if necessary or warn? assuming correct URDF for now.
             pass

        # Split arm and gripper
        arm_positions = all_joint_positions[:, :6]
        gripper_positions = all_joint_positions[:, 6:8]
        
        arm_velocities = all_joint_velocities[:, :6]
        gripper_velocities = all_joint_velocities[:, 6:8]

        # Get end-effector positions
        ee_positions, _ = self.piper_arms.get_world_poses(clone=False)  # (num_envs, 3)
        
        # Calculate distances to targets
        distances = torch.norm(ee_positions - self.target_positions, dim=1, keepdim=True)  # (num_envs, 1)
        
        # Concatenate observations
        # Order: Steering(2), ArmJoints(6+6), Gripper(2+2), Target(3), Distance(1)
        self.obs_buf = torch.cat([
            self.steering_angles.unsqueeze(1),      # (num_envs, 1)
            self.steering_velocities.unsqueeze(1),  # (num_envs, 1)
            arm_positions,                           # (num_envs, 6)
            arm_velocities,                          # (num_envs, 6)
            gripper_positions,                       # (num_envs, 2)
            gripper_velocities,                      # (num_envs, 2)
            self.target_positions,                   # (num_envs, 3)
            distances                                # (num_envs, 1)
        ], dim=1)
        
        observations = {
            self.piper_arms.name: {
                "obs_buf": self.obs_buf
            }
        }
        
        return observations
        
    def pre_physics_step(self, actions: torch.Tensor) -> None:
        """
        Apply actions before physics step
        actions: (num_envs, 7) joint position deltas + gripper
        """
        # Reset environments that need it
        reset_env_ids = self.reset_buf.nonzero(as_tuple=False).squeeze(-1)
        if len(reset_env_ids) > 0:
            self.reset_idx(reset_env_ids)
            
        # Split actions
        # First 6: Arm joint deltas
        # 7th: Gripper command (-1 to 1) -> Currently mapped to Open/Close
        arm_actions = actions[:, :6]
        gripper_action = actions[:, 6]
        
        # Scale actions from [-1, 1] to actual joint deltas
        actions_scaled = arm_actions * 0.1  # Max 0.1 radian change per step
        
        # Get current joint positions (8 DOFs)
        current_positions = self.piper_arms.get_joint_positions(clone=False)
        current_arm_pos = current_positions[:, :6]
        
        # Compute new arm positions
        new_arm_pos = torch.clamp(
            current_arm_pos + actions_scaled,
            -np.pi, np.pi
        )
        
        # Compute gripper positions
        # Logic: -1 (Close) -> 0.0, 1 (Open) -> 0.035
        # Mapped to [-1, 1] input range
        # Joint 7: 0 to 0.035
        # Joint 8: -0.035 to 0
        
        # Map [-1, 1] to [0, 1]
        gripper_cmd_norm = (gripper_action + 1.0) * 0.5
        gripper_cmd_norm = torch.clamp(gripper_cmd_norm, 0.0, 1.0)
        
        # Target positions
        target_j7 = gripper_cmd_norm * 0.035
        target_j8 = -gripper_cmd_norm * 0.035
        
        # Construct full target (num_envs, 8)
        new_positions = torch.cat([
            new_arm_pos,
            target_j7.unsqueeze(1),
            target_j8.unsqueeze(1)
        ], dim=1)
        
        # Apply to all arms
        self.piper_arms.set_joint_positions(new_positions)
        
        # Update steering (simulate changing input)
        self.steering_velocities = torch.rand(
            self._num_envs, device=self._device
        ) * 10.0 - 5.0  # Random velocity [-5, 5]
        
        self.steering_angles += self.steering_velocities * (1.0/60.0)
        self.steering_angles = torch.clamp(self.steering_angles, -90, 90)
        
        # Update target positions
        self._update_target_positions()
        
    def post_physics_step(self) -> None:
        """
        Compute rewards and check termination after physics step
        """
        self.progress_buf += 1
        
        # Calculate rewards
        self.rew_buf[:] = self.compute_rewards()
        
        # Check termination
        self.reset_buf = self.compute_resets()
        
    def compute_rewards(self) -> torch.Tensor:
        """
        Compute rewards for all environments
        Returns: (num_envs,) tensor of rewards
        """
        # Get observations
        # Index changed due to expanded obs buffer
        # Distance is still last element.
        distances = self.obs_buf[:, -1]
        
        # Velocities are now indices 16-21 (arm) and 22-23 (gripper)?
        # Obs structure:
        # 0: Steering Angle
        # 1: Steering Vel
        # 2-7: Arm Pos
        # 8-13: Arm Vel
        # 14-15: Gripper Pos
        # 16-17: Gripper Vel
        # 18-20: Target
        # 21: Distance
        
        # So arm velocities are obs_buf[:, 8:14] -- Unchanged index relative to start, IF steering is first.
        # Yes: Steering(2) + ArmPos(6) = 8. So 8 is start of ArmVel.
        joint_velocities = self.obs_buf[:, 8:14] 
        
        # Distance penalty (want to be close to target)
        distance_reward = -self.distance_weight * (distances ** 2)
        
        # Smoothness penalty (want low velocities)
        smoothness_penalty = -self.smoothness_weight * torch.sum(joint_velocities ** 2, dim=1)
        
        # Success bonus (within 2cm)
        success_bonus = torch.where(
            distances < 0.02,
            torch.tensor(self.success_bonus, device=self._device),
            torch.tensor(0.0, device=self._device)
        )
        
        # Total reward
        total_reward = distance_reward + smoothness_penalty + success_bonus
        
        return total_reward
        
    def compute_resets(self) -> torch.Tensor:
        """
        Check which environments should reset
        Returns: (num_envs,) tensor of booleans
        """
        # Reset if too far from target
        distances = self.obs_buf[:, -1]
        too_far = distances > 0.5
        
        # Reset if episode too long
        timeout = self.progress_buf >= self._max_episode_length
        
        # Combine conditions
        reset = too_far | timeout
        
        return reset
        
    def reset_idx(self, env_ids: torch.Tensor) -> None:
        """
        Reset specified environments
        env_ids: indices of environments to reset
        """
        num_resets = len(env_ids)
        
        # Random initial steering angles
        self.steering_angles[env_ids] = torch.rand(
            num_resets, device=self._device
        ) * 90.0 - 45.0  # [-45, 45]
        
        self.steering_velocities[env_ids] = 0.0
        
        # Reset arm to default pose
        # Must provide 8 values now
        init_pos = torch.tensor(
            [0.0, -0.3, 0.5, 0.0, 0.5, 0.0, 0.035, -0.035], # 6 arm + 2 gripper (open)
            device=self._device
        ).repeat(num_resets, 1)
        
        self.piper_arms.set_joint_positions(init_pos, indices=env_ids)
        self.piper_arms.set_joint_velocities(
            torch.zeros((num_resets, 8), device=self._device),
            indices=env_ids
        )
        
        # Update targets
        self._update_target_positions()
        
        # Reset progress
        self.progress_buf[env_ids] = 0
        self.reset_buf[env_ids] = 0
        
    def _update_target_positions(self) -> None:
        """Calculate target positions on steering wheel rim for all envs"""
        wheel_center = torch.tensor(
            [0.3, 0.0, 0.625],
            device=self._device
        ).unsqueeze(0).repeat(self._num_envs, 1)
        
        wheel_radius = 0.15
        target_rad = torch.deg2rad(self.steering_angles)
        
        angle_offset = torch.deg2rad(torch.tensor(45.0, device=self._device))
        total_angle = target_rad + angle_offset
        
        local_target = torch.stack([
            wheel_radius * torch.sin(total_angle),
            wheel_radius * torch.cos(total_angle),
            torch.zeros_like(total_angle)
        ], dim=1)
        
        self.target_positions = wheel_center + local_target
