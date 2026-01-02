#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/single_threaded_executor.hpp>

#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <moveit_msgs/msg/robot_trajectory.hpp>

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

#include <chrono>
#include <thread>
#include <map>
#include <string>
#include <vector>
#include <cmath>

using namespace std::chrono_literals;

// -------------------------
// Generic helpers
// -------------------------
static bool planAndExecutePose(moveit::planning_interface::MoveGroupInterface& group,
                              const geometry_msgs::msg::PoseStamped& target,
                              const std::string& ee_link,
                              rclcpp::Logger logger)
{
  group.setStartStateToCurrentState();
  group.clearPoseTargets();
  group.setPoseTarget(target, ee_link);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  if (group.plan(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Planning failed (pose).");
    return false;
  }

  if (group.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Execution failed (pose).");
    return false;
  }

  return true;
}

static bool planAndExecuteJoints(moveit::planning_interface::MoveGroupInterface& group,
                                const std::map<std::string, double>& joints,
                                rclcpp::Logger logger)
{
  group.setStartStateToCurrentState();
  group.clearPoseTargets();
  group.setJointValueTarget(joints);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  if (group.plan(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Planning failed (joints).");
    return false;
  }

  if (group.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Execution failed (joints).");
    return false;
  }

  return true;
}

static void sendGripper(moveit::planning_interface::MoveGroupInterface& gripper,
                        const std::map<std::string, double>& target,
                        rclcpp::Logger logger)
{
  gripper.setStartStateToCurrentState();
  gripper.setJointValueTarget(target);
  (void)gripper.move();
  RCLCPP_INFO(logger, "Gripper command sent.");
}

// -------------------------
// Rotate EE around wheel axis using Cartesian waypoints
// -------------------------
static bool rotateAroundAxisCartesian(moveit::planning_interface::MoveGroupInterface& arm,
                                     const std::string& ee_link,
                                     const geometry_msgs::msg::PoseStamped& start_pose,
                                     const tf2::Vector3& center,
                                     const tf2::Vector3& axis_unit,
                                     double angle_rad,
                                     int steps,
                                     double eef_step,
                                     rclcpp::Logger logger)
{
  (void)ee_link; // not needed (keeps compiler quiet)

  // Base pose
  geometry_msgs::msg::Pose p0 = start_pose.pose;

  // Vector from center to current EE position (radius vector)
  tf2::Vector3 r0(p0.position.x - center.x(),
                  p0.position.y - center.y(),
                  p0.position.z - center.z());

  // Old orientation
  tf2::Quaternion q_old;
  tf2::fromMsg(p0.orientation, q_old);

  std::vector<geometry_msgs::msg::Pose> waypoints;
  waypoints.reserve(steps);

  for (int i = 1; i <= steps; ++i)
  {
    const double a = angle_rad * (double(i) / steps);

    // rotation around axis by a
    tf2::Quaternion q_rot(axis_unit, a);

    // rotate radius vector -> new position
    tf2::Vector3 r_i = tf2::quatRotate(q_rot, r0);
    tf2::Vector3 pos = center + r_i;

    geometry_msgs::msg::Pose w = p0;
    w.position.x = pos.x();
    w.position.y = pos.y();
    w.position.z = pos.z();

    // rotate orientation along with motion
    tf2::Quaternion q_new = q_rot * q_old;
    w.orientation = tf2::toMsg(q_new);

    waypoints.push_back(w);
  }

  moveit_msgs::msg::RobotTrajectory traj;
  const double jump_threshold = 0.0; // disable jump check

  arm.setStartStateToCurrentState();
  const double fraction = arm.computeCartesianPath(waypoints, eef_step, jump_threshold, traj);

  if (fraction < 0.95)
  {
    RCLCPP_WARN(logger, "Cartesian path fraction too low: %.2f", fraction);
    return false;
  }

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  plan.trajectory_ = traj;

  if (arm.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Execution failed (rotate).");
    return false;
  }

  return true;
}

// -------------------------
// Main
// -------------------------
int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("piper_steeringwheel_rotate_node");
  auto log = node->get_logger();

  // Parameters (optional)
  const std::string arm_group     = node->declare_parameter<std::string>("arm_group", "arm");
  const std::string gripper_group = node->declare_parameter<std::string>("gripper_group", "gripper");

  rclcpp::executors::SingleThreadedExecutor exec;
  exec.add_node(node);
  std::thread spinner([&exec]() { exec.spin(); });
  std::this_thread::sleep_for(2s);

  moveit::planning_interface::MoveGroupInterface arm(node, arm_group);
  moveit::planning_interface::MoveGroupInterface gripper(node, gripper_group);

  arm.setPlanningTime(10.0);
  arm.setNumPlanningAttempts(10);

  const std::string planning_frame = arm.getPlanningFrame();
  const std::string ee_link = arm.getEndEffectorLink();

  RCLCPP_INFO(log, "Planning frame: %s", planning_frame.c_str());
  RCLCPP_INFO(log, "EE link: %s", ee_link.c_str());


  //  SET THESE VALUES
  const double grasp_x = 0.65;
  const double grasp_y = 0.0;
  const double grasp_z = 0.85;

  const double center_x = 1.48751244;
  const double center_y = 0.0;
  const double center_z = 0.9;

  double axis_x = 0.0; // TODO
  double axis_y = 0.0; // TODO
  double axis_z = 1.0; // TODO

  const double z_hover_offset = 0.10;

  const double angle_deg = 90.0;
  const double angle_rad = angle_deg * M_PI / 180.0;
  const int steps = 30;
  const double eef_step = 0.01;

  // Slow scaling for rotation (optional)
  arm.setMaxVelocityScalingFactor(0.3);
  arm.setMaxAccelerationScalingFactor(0.3);

  std::map<std::string, double> joints_home{
      {"joint1", 0.0}, {"joint2", 0.0}, {"joint3", 0.0},
      {"joint4", 0.0}, {"joint5", 0.0}, {"joint6", 0.0},
  };

  std::map<std::string, double> gripper_open{{"joint7", 0.035}, {"joint8", -0.035}};
  std::map<std::string, double> gripper_close{{"joint7", 0.0}, {"joint8", 0.0}};

  bool ok = true;

  // Normalize axis + build center
  tf2::Vector3 axis(axis_x, axis_y, axis_z);
  tf2::Vector3 center(center_x, center_y, center_z);

  if (axis.length2() < 1e-12)
  {
    RCLCPP_ERROR(log, "Axis vector is zero. Set axis_x/y/z.");
    ok = false;
  }
  else
  {
    axis.normalize();
  }

  // Main sequence (no goto!)
  do
  {
    if (!ok) break;

    // Base orientation: use current EE orientation
    auto cur = arm.getCurrentPose(ee_link);

    // Build hover + grasp pose
    geometry_msgs::msg::PoseStamped grasp_hover;
    grasp_hover.header.frame_id = planning_frame;
    grasp_hover.pose = cur.pose;
    grasp_hover.pose.position.x = grasp_x;
    grasp_hover.pose.position.y = grasp_y;
    grasp_hover.pose.position.z = grasp_z + z_hover_offset;

    geometry_msgs::msg::PoseStamped grasp_pose = grasp_hover;
    grasp_pose.pose.position.z = grasp_z;

    RCLCPP_INFO(log, "0) Open gripper");
    sendGripper(gripper, gripper_open, log);
    std::this_thread::sleep_for(400ms);

    RCLCPP_INFO(log, "1) Move to hover above wheel grasp point");
    ok = planAndExecutePose(arm, grasp_hover, ee_link, log);
    if (!ok) break;

    RCLCPP_INFO(log, "2) Move down to grasp");
    ok = planAndExecutePose(arm, grasp_pose, ee_link, log);
    if (!ok) break;

    RCLCPP_INFO(log, "3) Close gripper (grab wheel)");
    sendGripper(gripper, gripper_close, log);
    std::this_thread::sleep_for(600ms);

    // After closing, read actual pose (better start for cartesian)
    auto start_pose = arm.getCurrentPose(ee_link);

    RCLCPP_INFO(log, "4) Rotate wheel +%.1f deg", angle_deg);
    ok = rotateAroundAxisCartesian(arm, ee_link, start_pose, center, axis, +angle_rad, steps, eef_step, log);
    if (!ok) break;

    auto pose_after = arm.getCurrentPose(ee_link);

    RCLCPP_INFO(log, "5) Rotate wheel back -%.1f deg", angle_deg);
    ok = rotateAroundAxisCartesian(arm, ee_link, pose_after, center, axis, -angle_rad, steps, eef_step, log);
    if (!ok) break;

    RCLCPP_INFO(log, "6) Open gripper (release)");
    sendGripper(gripper, gripper_open, log);
    std::this_thread::sleep_for(400ms);

    RCLCPP_INFO(log, "7) Move up to hover");
    ok = planAndExecutePose(arm, grasp_hover, ee_link, log);
    if (!ok) break;

    // restore full speed
    arm.setMaxVelocityScalingFactor(1.0);
    arm.setMaxAccelerationScalingFactor(1.0);

    RCLCPP_INFO(log, "8) Go home (joints)");
    ok = planAndExecuteJoints(arm, joints_home, log);
    if (!ok) break;

    RCLCPP_INFO(log, "Done.");
  } while (false);

  // Cleanup always
  exec.cancel();
  if (spinner.joinable()) spinner.join();
  rclcpp::shutdown();

  return ok ? 0 : 1;
}
