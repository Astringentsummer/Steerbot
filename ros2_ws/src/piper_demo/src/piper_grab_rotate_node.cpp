#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/single_threaded_executor.hpp>

#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose_stamped.hpp>

#include <chrono>
#include <thread>
#include <map>

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

using namespace std::chrono_literals;

static bool plan_and_execute_pose(moveit::planning_interface::MoveGroupInterface& arm,
                                 const geometry_msgs::msg::PoseStamped& pose,
                                 const std::string& ee_link,
                                 rclcpp::Logger logger)
{
  arm.setStartStateToCurrentState();
  arm.clearPoseTargets();
  arm.setPoseTarget(pose, ee_link);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  auto res = arm.plan(plan);
  if (res == moveit::core::MoveItErrorCode::SUCCESS)
  {
    auto exec_res = arm.execute(plan);
    if (exec_res != moveit::core::MoveItErrorCode::SUCCESS)
    {
      RCLCPP_WARN(logger, "Execution failed.");
      return false;
    }
    return true;
  }

  RCLCPP_WARN(logger, "Planning failed.");
  return false;
}

static void move_gripper(moveit::planning_interface::MoveGroupInterface& gripper,
                         const std::map<std::string, double>& target,
                         rclcpp::Logger logger)
{
  gripper.setStartStateToCurrentState();
  gripper.setJointValueTarget(target);
  (void)gripper.move();
  RCLCPP_INFO(logger, "Gripper command sent.");
}

static geometry_msgs::msg::PoseStamped apply_local_z_offset(const geometry_msgs::msg::PoseStamped& in,
                                                            double local_z_m)
{
  geometry_msgs::msg::PoseStamped out = in;

  tf2::Quaternion q;
  tf2::fromMsg(in.pose.orientation, q);
  tf2::Matrix3x3 R(q);

  tf2::Vector3 offset_local(0.0, 0.0, local_z_m);
  tf2::Vector3 offset_world = R * offset_local;

  out.pose.position.x += offset_world.x();
  out.pose.position.y += offset_world.y();
  out.pose.position.z += offset_world.z();
  return out;
}

static geometry_msgs::msg::PoseStamped rotate_about_local_z(const geometry_msgs::msg::PoseStamped& in,
                                                           double angle_rad)
{
  geometry_msgs::msg::PoseStamped out = in;

  tf2::Quaternion q_cur;
  tf2::fromMsg(in.pose.orientation, q_cur);

  tf2::Quaternion q_delta;
  q_delta.setRotation(tf2::Vector3(0.0, 0.0, 1.0), angle_rad);

  tf2::Quaternion q_new = q_cur * q_delta;
  q_new.normalize();

  out.pose.orientation = tf2::toMsg(q_new);
  return out;
}

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("piper_grab_rotate_node");

  const std::string arm_group = node->declare_parameter<std::string>("arm_group", "arm");
  const std::string gripper_group = node->declare_parameter<std::string>("gripper_group", "gripper");

  const double target_x = node->declare_parameter<double>("target_x", 0.93);
  const double target_y = node->declare_parameter<double>("target_y", -0.15);
  const double target_z = node->declare_parameter<double>("target_z", 0.805);

  const double hover_z_offset = node->declare_parameter<double>("hover_z_offset", 0.10);
  const double local_z_offset = node->declare_parameter<double>("local_z_offset", 0.075);

  const double rotate_deg = node->declare_parameter<double>("rotate_deg", 90.0);

  const double vel_scale = node->declare_parameter<double>("vel_scale", 1.0);
  const double acc_scale = node->declare_parameter<double>("acc_scale", 1.0);

  const double slow_vel_scale = node->declare_parameter<double>("slow_vel_scale", 0.2);
  const double slow_acc_scale = node->declare_parameter<double>("slow_acc_scale", 0.2);

  const double gripper_open_j7 = node->declare_parameter<double>("gripper_open_joint7", 0.035);
  const double gripper_open_j8 = node->declare_parameter<double>("gripper_open_joint8", -0.035);
  const double gripper_close_j7 = node->declare_parameter<double>("gripper_close_joint7", 0.0);
  const double gripper_close_j8 = node->declare_parameter<double>("gripper_close_joint8", 0.0);

  RCLCPP_INFO(node->get_logger(), "Arm group: %s", arm_group.c_str());
  RCLCPP_INFO(node->get_logger(), "Gripper group: %s", gripper_group.c_str());

  rclcpp::executors::SingleThreadedExecutor exec;
  exec.add_node(node);
  std::thread spinner([&exec]() { exec.spin(); });

  std::this_thread::sleep_for(2s);

  moveit::planning_interface::MoveGroupInterface arm(node, arm_group);
  moveit::planning_interface::MoveGroupInterface gripper(node, gripper_group);

  arm.setPlanningTime(10.0);
  arm.setNumPlanningAttempts(10);
  arm.setMaxVelocityScalingFactor(vel_scale);
  arm.setMaxAccelerationScalingFactor(acc_scale);

  const std::string planning_frame = arm.getPlanningFrame();
  const std::string ee_link = arm.getEndEffectorLink();

  RCLCPP_INFO(node->get_logger(), "Planning frame: %s", planning_frame.c_str());
  RCLCPP_INFO(node->get_logger(), "EE link: %s", ee_link.c_str());

  std::map<std::string, double> gr_open{{"joint7", gripper_open_j7}, {"joint8", gripper_open_j8}};
  std::map<std::string, double> gr_close{{"joint7", gripper_close_j7}, {"joint8", gripper_close_j8}};

  auto base_pose = arm.getCurrentPose(ee_link);

  geometry_msgs::msg::PoseStamped hover;
  hover.header.frame_id = planning_frame;
  hover.pose = base_pose.pose;
  hover.pose.position.x = target_x;
  hover.pose.position.y = target_y;
  hover.pose.position.z = target_z + hover_z_offset;

  geometry_msgs::msg::PoseStamped grasp = hover;
  grasp.pose.position.z = target_z;

  hover = apply_local_z_offset(hover, local_z_offset);
  grasp = apply_local_z_offset(grasp, local_z_offset);

  geometry_msgs::msg::PoseStamped lift = hover;

  const double rotate_rad = rotate_deg * M_PI / 180.0;
  geometry_msgs::msg::PoseStamped rotated = rotate_about_local_z(lift, rotate_rad);

  move_gripper(gripper, gr_open, node->get_logger());
  std::this_thread::sleep_for(400ms);

  if (!plan_and_execute_pose(arm, hover, ee_link, node->get_logger())) goto shutdown;

  arm.setMaxVelocityScalingFactor(slow_vel_scale);
  arm.setMaxAccelerationScalingFactor(slow_acc_scale);
  if (!plan_and_execute_pose(arm, grasp, ee_link, node->get_logger())) goto shutdown;
  arm.setMaxVelocityScalingFactor(vel_scale);
  arm.setMaxAccelerationScalingFactor(acc_scale);

  move_gripper(gripper, gr_close, node->get_logger());
  std::this_thread::sleep_for(600ms);

  if (!plan_and_execute_pose(arm, lift, ee_link, node->get_logger())) goto shutdown;

  arm.setMaxVelocityScalingFactor(slow_vel_scale);
  arm.setMaxAccelerationScalingFactor(slow_acc_scale);
  if (!plan_and_execute_pose(arm, rotated, ee_link, node->get_logger())) goto shutdown;
  arm.setMaxVelocityScalingFactor(vel_scale);
  arm.setMaxAccelerationScalingFactor(acc_scale);

  RCLCPP_INFO(node->get_logger(), "Grab + rotate done.");

shutdown:
  exec.cancel();
  if (spinner.joinable()) spinner.join();
  rclcpp::shutdown();
  return 0;
}
