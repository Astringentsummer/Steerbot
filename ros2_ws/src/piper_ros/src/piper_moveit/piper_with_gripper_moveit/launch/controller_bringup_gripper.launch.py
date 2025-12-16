from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    fake_hardware = LaunchConfiguration("fake_hardware")

    DeclareLaunchArgument(
        "fake_hardware",
        default_value="true",
        description="Use fake ros2_control hardware"
    )

    moveit_config = (
        MoveItConfigsBuilder("piper", package_name="piper_with_gripper_moveit")
        .to_moveit_configs()
    )

    pkg_share = get_package_share_directory("piper_with_gripper_moveit")

    controllers_yaml = PathJoinSubstitution(
        [pkg_share, "config", "ros2_controllers.yaml"]
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {"use_sim_time": True},
            {"ignore_timestamp": True},
            moveit_config.robot_description,
        ],
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[
            {"use_sim_time": True},              
            moveit_config.robot_description,
            controllers_yaml,
            {"fake_hardware": fake_hardware},
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "arm_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "gripper_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    jsb_delayed = TimerAction(
        period=1.0,
        actions=[joint_state_broadcaster_spawner],
    )

    arm_and_gripper_delayed = TimerAction(
        period=2.0,
        actions=[
            arm_controller_spawner,
            gripper_controller_spawner,
        ],
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "fake_hardware",
                default_value="true",
            ),
            # rsp,
            ros2_control_node,
            jsb_delayed,
            arm_and_gripper_delayed,
        ]
    )
