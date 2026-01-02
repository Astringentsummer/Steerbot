#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/single_threaded_executor.hpp>

#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose_stamped.hpp>

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

#include <chrono>
#include <thread>
#include <map>
#include <string>

using namespace std::chrono_literals;

static bool planAndExecutePose(moveit::planning_interface::MoveGroupInterface& group,
                              const geometry_msgs::msg::PoseStamped& target,
                              const std::string& ee_link,
                              rclcpp::Logger logger)
{
  group.setStartStateToCurrentState();
  group.clearPoseTargets();
  group.setPoseTarget(target, ee_link);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  const auto res = group.plan(plan);
  if (res != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Planning failed (pose).");
    return false;
  }

  const auto exec_res = group.execute(plan);
  if (exec_res != moveit::core::MoveItErrorCode::SUCCESS)
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
  const auto res = group.plan(plan);
  if (res != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger, "Planning failed (joints).");
    return false;
  }

  const auto exec_res = group.execute(plan);
  if (exec_res != moveit::core::MoveItErrorCode::SUCCESS)
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
  // Gripper direkt als move() ohne separates plan/execute
  gripper.setStartStateToCurrentState();
  gripper.setJointValueTarget(target);
  (void)gripper.move();
  RCLCPP_INFO(logger, "Gripper command sent.");
}

// Quaternion-Rotation * lokaler Offset -> Welt-Offset
static tf2::Vector3 localOffsetToWorld(const geometry_msgs::msg::Quaternion& q_msg,
                                       const tf2::Vector3& offset_local)
{
  tf2::Quaternion q;
  tf2::fromMsg(q_msg, q);
  tf2::Matrix3x3 R(q);
  return R * offset_local;
}

static void applyWorldOffset(geometry_msgs::msg::PoseStamped& pose, const tf2::Vector3& d)
{
  pose.pose.position.x += d.x();
  pose.pose.position.y += d.y();
  pose.pose.position.z += d.z();
}

// Konfiguration 
struct PickPlaceConfig
{
  // Dose / Objekt Position (im planning_frame)
  double can_x = 0.75228;
  double can_y = -0.15218;
  double can_z = 0.80589;

  // Hover über Objekt
  double z_hover_offset = 0.10;

  // Lokaler Offset entlang EE-local Z (z.B. "ein Stück nach vorne" bei gegebener Orientierung)
  double ee_local_z_offset = 0.075;

  // Place Position relativ zur Dose
  double place_dx = 0.20;
  double place_dy = 0.20;
  double place_down_extra = 0.00;

  // Slow Place
  double place_vel_scale = 0.2;
  double place_acc_scale = 0.2;

  // Joint Targets
  std::map<std::string, double> joints_home{
      {"joint1", 0.0}, {"joint2", 0.0}, {"joint3", 0.0},
      {"joint4", 0.0}, {"joint5", 0.0}, {"joint6", 0.0},
  };

  // Gripper
  std::map<std::string, double> gripper_open{{"joint7", 0.035}, {"joint8", -0.035}};
  std::map<std::string, double> gripper_close{{"joint7", 0.0}, {"joint8", 0.0}};

  // kurze Wartezeiten (Simulation/Controller Zeit geben)
  std::chrono::milliseconds wait_short{500};
  std::chrono::milliseconds wait_grasp{600};
  std::chrono::milliseconds wait_release{600};
};

// App-Klasse: kapselt Setup + Ablauf
class PickPlaceApp
{
public:
  PickPlaceApp(const rclcpp::Node::SharedPtr& node,
               const std::string& arm_group,
               const std::string& gripper_group)
  : node_(node),
    arm_(node_, arm_group),
    gripper_(node_, gripper_group),
    logger_(node_->get_logger())
  {
    // Arm-Planungsparameter
    arm_.setPlanningTime(10.0);
    arm_.setNumPlanningAttempts(10);

    planning_frame_ = arm_.getPlanningFrame();
    ee_link_ = arm_.getEndEffectorLink();

    RCLCPP_INFO(logger_, "Planning frame: %s", planning_frame_.c_str());
    RCLCPP_INFO(logger_, "EE link: %s", ee_link_.c_str());
  }

  bool run(const PickPlaceConfig& cfg)
  {
    // 1) Zielposen berechnen
    const auto poses = computePoses(cfg);

    // 2) Ablauf 
    RCLCPP_INFO(logger_, "A) Gripper öffnen (Start)");
    sendGripper(gripper_, cfg.gripper_open, logger_);
    std::this_thread::sleep_for(cfg.wait_short);

    RCLCPP_INFO(logger_, "1) Hover über Objekt");
    if (!moveToPose(poses.pick_hover)) return false;

    RCLCPP_INFO(logger_, "2) Runterfahren (Pick)");
    if (!moveToPose(poses.pick_grasp)) return false;

    RCLCPP_INFO(logger_, "3) Greifer schließen (Greifen)");
    sendGripper(gripper_, cfg.gripper_close, logger_);
    std::this_thread::sleep_for(cfg.wait_grasp);

    RCLCPP_INFO(logger_, "4) Hoch (zurück Hover)");
    if (!moveToPose(poses.pick_hover)) return false;

    RCLCPP_INFO(logger_, "5) Über Ablageposition (Hover)");
    if (!moveToPose(poses.place_hover)) return false;

    RCLCPP_INFO(logger_, "6) Langsam runter (Place)");
    if (!moveToPoseScaled(poses.place_down, cfg.place_vel_scale, cfg.place_acc_scale)) return false;

    RCLCPP_INFO(logger_, "7) Loslassen (Gripper öffnen)");
    sendGripper(gripper_, cfg.gripper_open, logger_);
    std::this_thread::sleep_for(cfg.wait_release);

    RCLCPP_INFO(logger_, "8) Hoch (Place Hover)");
    if (!moveToPose(poses.place_hover)) return false;

    RCLCPP_INFO(logger_, "9) Gripper schließen (leer)");
    sendGripper(gripper_, cfg.gripper_close, logger_);
    std::this_thread::sleep_for(400ms);

    RCLCPP_INFO(logger_, "10) Zurück in Home (Joints)");
    if (!moveToJoints(cfg.joints_home)) return false;

    RCLCPP_INFO(logger_, "Pick & Place abgeschlossen.");
    return true;
  }

private:
  struct Poses
  {
    geometry_msgs::msg::PoseStamped pick_hover;
    geometry_msgs::msg::PoseStamped pick_grasp;
    geometry_msgs::msg::PoseStamped place_hover;
    geometry_msgs::msg::PoseStamped place_down;
  };

  Poses computePoses(const PickPlaceConfig& cfg)
  {
    // Orientierung vom aktuellen EE übernehmen
    const auto current = arm_.getCurrentPose(ee_link_);

    Poses p;
    p.pick_hover.header.frame_id = planning_frame_;
    p.pick_hover.pose = current.pose;
    p.pick_hover.pose.position.x = cfg.can_x;
    p.pick_hover.pose.position.y = cfg.can_y;
    p.pick_hover.pose.position.z = cfg.can_z + cfg.z_hover_offset;

    p.pick_grasp = p.pick_hover;
    p.pick_grasp.pose.position.z = cfg.can_z;

    // optionaler "lokaler" Offset entlang EE-Z (wird in Weltkoordinaten gedreht)
    const tf2::Vector3 offset_local(0.0, 0.0, cfg.ee_local_z_offset);
    const tf2::Vector3 offset_world = localOffsetToWorld(p.pick_hover.pose.orientation, offset_local);

    applyWorldOffset(p.pick_hover, offset_world);
    applyWorldOffset(p.pick_grasp, offset_world);

    RCLCPP_INFO(logger_,
                "Applied EE local-Z offset %.3f => world dx=%.3f dy=%.3f dz=%.3f",
                cfg.ee_local_z_offset, offset_world.x(), offset_world.y(), offset_world.z());

    // Place: xy verschoben, z wie zuvor
    p.place_hover = p.pick_hover;
    p.place_hover.pose.position.x = cfg.can_x + cfg.place_dx;
    p.place_hover.pose.position.y = cfg.can_y + cfg.place_dy;

    p.place_down = p.place_hover;
    p.place_down.pose.position.z = cfg.can_z + cfg.place_down_extra;

    return p;
  }

  bool moveToPose(const geometry_msgs::msg::PoseStamped& target)
  {
    return planAndExecutePose(arm_, target, ee_link_, logger_);
  }

  bool moveToPoseScaled(const geometry_msgs::msg::PoseStamped& target,
                        double vel_scale, double acc_scale)
  {
    // Temporär langsamer machen
    const double old_vel = 1.0;
    const double old_acc = 1.0;

    arm_.setMaxVelocityScalingFactor(vel_scale);
    arm_.setMaxAccelerationScalingFactor(acc_scale);

    const bool ok = planAndExecutePose(arm_, target, ee_link_, logger_);

    // wieder zurück
    arm_.setMaxVelocityScalingFactor(old_vel);
    arm_.setMaxAccelerationScalingFactor(old_acc);

    return ok;
  }

  bool moveToJoints(const std::map<std::string, double>& joints)
  {
    return planAndExecuteJoints(arm_, joints, logger_);
  }

private:
  rclcpp::Node::SharedPtr node_;
  moveit::planning_interface::MoveGroupInterface arm_;
  moveit::planning_interface::MoveGroupInterface gripper_;
  rclcpp::Logger logger_;

  std::string planning_frame_;
  std::string ee_link_;
};


int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("piper_pick_place_node");

  const std::string arm_group = node->declare_parameter<std::string>("arm_group", "arm");
  const std::string gripper_group = node->declare_parameter<std::string>("gripper_group", "gripper");

  RCLCPP_INFO(node->get_logger(), "Arm group: %s", arm_group.c_str());
  RCLCPP_INFO(node->get_logger(), "Gripper group: %s", gripper_group.c_str());

  // Executor spinnen (MoveIt braucht Callback-Verarbeitung)
  rclcpp::executors::SingleThreadedExecutor exec;
  exec.add_node(node);
  std::thread spinner([&exec]() { exec.spin(); });

  std::this_thread::sleep_for(2s);  // kurz warten bis alles "steht"

  // App + Config
  PickPlaceConfig cfg;
  PickPlaceApp app(node, arm_group, gripper_group);

  // Run
  const bool ok = app.run(cfg);
  if (!ok)
    RCLCPP_ERROR(node->get_logger(), "Pick & Place abgebrochen (Fehler).");

  exec.cancel();
  if (spinner.joinable()) spinner.join();
  rclcpp::shutdown();
  return ok ? 0 : 1;
}
