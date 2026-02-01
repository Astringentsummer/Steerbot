import os
import yaml
import logging

class KinematicControlEngine:
    """
    Operational Controller: Deterministic Kinematic Mapping.
    Handles the direct translation of telemetry to actuator commands.
    """
    def __init__(self, config_path="config/system_parameters.yaml"):
        self.logger = logging.getLogger("System.Control")
        self.config = self._load_config(config_path)
        self.active_mode = "DETERMINISTIC_KINEMATICS"
        
    def _load_config(self, path):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Config missing, using defaults: {e}")
            return {}

    def compute_command(self, observation):
        """
        Standardized Control API.
        Args:
            observation (np.array): Telemetry vector [angle, velocity, torque]
        Returns:
            action (np.array): Joint velocity/position commands
        """
        return self._kinematic_mapping(observation)

    def _kinematic_mapping(self, obs):
        # Direct mathematical mapping: Input Angle -> Base Rotation
        scaling_factor = self.config.get("kinematics", {}).get("scaling_factor", 0.2)
        return obs[0] * scaling_factor
