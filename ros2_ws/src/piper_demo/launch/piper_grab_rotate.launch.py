from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("piper", package_name="piper_with_gripper_moveit").to_moveit_configs()
    )

    mode_arg = DeclareLaunchArgument(
        "mode",
        default_value="rotate",
        description="Mode: rotate | hold"
    )

    mode = LaunchConfiguration("mode")

    return LaunchDescription([
        mode_arg,
        Node(
            package="piper_demo",
            executable="piper_grab_rotate_node",
            output="screen",
            parameters=[
                moveit_config.robot_description,
                moveit_config.robot_description_semantic,
                moveit_config.robot_description_kinematics,
                moveit_config.planning_pipelines,
                moveit_config.trajectory_execution,
                {"use_sim_time": True},
                {"mode": mode},
            ],
        )
    ])
