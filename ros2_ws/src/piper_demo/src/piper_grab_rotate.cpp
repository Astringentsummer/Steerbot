#include "piper_demo/piper_grab_rotate.hpp"

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <moveit_msgs/msg/robot_trajectory.hpp>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <thread>
#include <vector>

using namespace std::chrono_literals;

// If the quaternion is (almost) zero-length, return identity.
static tf2::Quaternion normalizedQuat(const tf2::Quaternion& q_in)
{
  tf2::Quaternion q = q_in;
  if (q.length2() < 1e-12) return tf2::Quaternion(0, 0, 0, 1);
  q.normalize();
  return q;
}

// Rotate an orientation around a WORLD-FRAME axis by angle_rad.
static geometry_msgs::msg::Quaternion rotateQuatAroundAxisWorld(
    const geometry_msgs::msg::Quaternion& q_in,
    const tf2::Vector3& axis_world,
    double angle_rad)
{
  tf2::Quaternion q0;
  tf2::fromMsg(q_in, q0);
  q0 = normalizedQuat(q0);

  // Normalize axis; fallback to +Z if axis is invalid
  tf2::Vector3 a = axis_world;
  if (a.length2() < 1e-12) a = tf2::Vector3(0, 0, 1);
  a.normalize();

  // Build rotation quaternion around the world axis
  tf2::Quaternion qrot;
  qrot.setRotation(a, angle_rad);
  qrot = normalizedQuat(qrot);

  // Pre-multiply => rotate in world frame around axis_world
  tf2::Quaternion q = qrot * q0;
  q = normalizedQuat(q);
  return tf2::toMsg(q);
}

// PiperGrabRotate constructor
PiperGrabRotate::PiperGrabRotate(rclcpp::Node::SharedPtr node, Config cfg)
: node_(std::move(node)),
  logger_(node_->get_logger()),
  cfg_(std::move(cfg)),
  arm_(node_, cfg_.arm_group),
  gripper_(node_, cfg_.gripper.group)
{
  // TF listener used to resolve the wheel pose and transform between frames
  tf_buffer_ = std::make_unique<tf2_ros::Buffer>(node_->get_clock());
  tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

  // MoveIt planning settings (timeouts, retry attempts, etc.)
  arm_.setPlanningTime(cfg_.motion.planning_time_s);
  arm_.setNumPlanningAttempts(cfg_.motion.planning_attempts);


  // Optionally override the end-effector link used for pose targets
  if (!cfg_.ee_link_override.empty())
    arm_.setEndEffectorLink(cfg_.ee_link_override);

  // Cache the planning/world frame and the end-effector link name
  planning_frame_ = arm_.getPlanningFrame();
  ee_link_ = arm_.getEndEffectorLink();

  // Normalize static wheel quaternion once
  cfg_.wheel.q = normalizedQuat(cfg_.wheel.q);

  RCLCPP_INFO(logger_, "Planning frame: %s", planning_frame_.c_str());
  RCLCPP_INFO(logger_, "EE link: %s", ee_link_.c_str());
  RCLCPP_INFO(logger_, "Wheel TF frame: '%s' (require=%s)",
              cfg_.wheel.tf_frame.c_str(),
              cfg_.require_wheel_tf ? "true" : "false");
  RCLCPP_INFO(logger_, "Wheel static pose frame: '%s' center=(%.4f %.4f %.4f)",
              cfg_.wheel.frame.c_str(),
              cfg_.wheel.center.x(), cfg_.wheel.center.y(), cfg_.wheel.center.z());
}

/*
 Strategy:
 1) If cfg_.wheel.tf_frame is set: try TF lookup (planning_frame <- wheel.tf_frame)
    - If successful, use that as wheel center/orientation.
    - If required and it fails -> return nullopt.
    - If not required and it fails -> fall back to static config.
 2) Static fallback: wheel.center and (optional) wheel.q provided in cfg_.wheel.frame.
    - If cfg_.wheel.frame != planning_frame, transform it via TF. If TF fails, use raw values.
  Wheel normal:
    - If orientation is used, the wheel normal is wheel-local +Z rotated into planning frame.
    - Otherwise, assume the wheel normal is +Z in planning frame.
*/
std::optional<PiperGrabRotate::WheelState> PiperGrabRotate::resolveWheel() const
{
  WheelState ws{};

  // Primary source: TF frame for the wheel (best, because it moves with the world/sim)
  if (!cfg_.wheel.tf_frame.empty())
  {
    try
    {
      auto T = tf_buffer_->lookupTransform(planning_frame_, cfg_.wheel.tf_frame, tf2::TimePointZero);
      tf2::Transform tf;
      tf2::fromMsg(T.transform, tf);

      // Wheel center and orientation in planning frame
      ws.c = tf.getOrigin();
      ws.q = normalizedQuat(tf.getRotation());

      // Wheel normal = rotated +Z of the wheel frame into planning frame
      ws.n = tf2::quatRotate(ws.q, tf2::Vector3(0, 0, 1));
      if (ws.n.length2() < 1e-12) ws.n = tf2::Vector3(0, 0, 1);
      ws.n.normalize();

      return ws;
    }
    catch (const tf2::TransformException& ex)
    {
      // If TF is mandatory, fail hard
      if (cfg_.require_wheel_tf)
      {
        RCLCPP_ERROR(logger_, "Wheel TF required, but lookupTransform(%s <- %s) failed: %s",
                     planning_frame_.c_str(), cfg_.wheel.tf_frame.c_str(), ex.what());
        return std::nullopt;
      }

      // Otherwise: warn and continue with fallback
      RCLCPP_WARN(logger_, "Wheel TF lookupTransform(%s <- %s) failed: %s. Falling back to static wheel pose.",
                  planning_frame_.c_str(), cfg_.wheel.tf_frame.c_str(), ex.what());
    }
  }

  // Fallback: static wheel pose in cfg_.wheel.frame
  tf2::Vector3 c_src = cfg_.wheel.center;
  // If use_orientation is false, use identity and assume normal is +Z
  tf2::Quaternion q_src = cfg_.wheel.use_orientation ? normalizedQuat(cfg_.wheel.q) : tf2::Quaternion(0, 0, 0, 1);


  if (cfg_.wheel.frame == planning_frame_)
  {
    // Static pose already in planning frame
    ws.c = c_src;
    ws.q = q_src;
  }
  else
  {
    // Transform static pose into the planning frame
    try
    {
      auto T = tf_buffer_->lookupTransform(planning_frame_, cfg_.wheel.frame, tf2::TimePointZero);
      tf2::Transform tf;
      tf2::fromMsg(T.transform, tf);

      // Point transform and rotation composition
      ws.c = tf * c_src;
      ws.q = normalizedQuat(tf.getRotation() * q_src);
    }
    catch (const tf2::TransformException& ex)
    {
      // Last resort: use raw values without any TF transform
      RCLCPP_WARN(logger_, "Static wheel TF lookupTransform(%s <- %s) failed: %s. Using raw static values (no TF).",
                  planning_frame_.c_str(), cfg_.wheel.frame.c_str(), ex.what());
      ws.c = c_src;
      ws.q = q_src;
    }
  }

  // Determine wheel normal based on whether we trust/used orientation
  ws.n = cfg_.wheel.use_orientation
           ? tf2::quatRotate(ws.q, tf2::Vector3(0, 0, 1))
           : tf2::Vector3(0, 0, 1);

  if (ws.n.length2() < 1e-12) ws.n = tf2::Vector3(0, 0, 1);
  ws.n.normalize();

  return ws;
}

// Compute a point on the wheel rim for an angle in the wheel plane.
// The wheel plane is defined by ws.q and center ws.c.
// Create a local XY point on the circle and rotate it into planning frame.
tf2::Vector3 PiperGrabRotate::rimPoint(const WheelState& ws, double angle_rad) const
{
  const tf2::Vector3 local(cfg_.radius * std::cos(angle_rad),
                           cfg_.radius * std::sin(angle_rad),
                           0.0);
  return tf2::quatRotate(ws.q, local) + ws.c;
}


// Compute radial and tangential directions at a rim contact point.
// r_out: unit radial direction in the wheel plane (from center towards contact)
// t_out: unit tangential direction in the wheel plane (normal x radial)
// Ensure r lies in the wheel plane by projecting out the component along ws.n.
void PiperGrabRotate::rimFrame(const WheelState& ws, const tf2::Vector3& contact,
                               tf2::Vector3& r_out, tf2::Vector3& t_out) const
{
  tf2::Vector3 r = contact - ws.c;

  // Project r into the wheel plane (remove normal component)
  r = r - ws.n * r.dot(ws.n);
  if (r.length2() < 1e-12) r = tf2::Vector3(1, 0, 0);
  r.normalize();
  // Tangent direction: n x r (right-hand rule)
  tf2::Vector3 t = ws.n.cross(r);
  if (t.length2() < 1e-12) t = tf2::Vector3(0, 1, 0);
  t.normalize();

  r_out = r;
  t_out = t;
}


/*
Build a grasp orientation for the tool at the rim contact
Defining a local frame for the tool:
  - tool Z axis points either:
    - into the wheel plane normal (-ws.n) if tool_z_to_normal is true, or
    - towards the wheel center direction (-r) otherwise
  - tool X axis aligned with rim tangent direction (t)
Then compute Y = Z x X and re-orthogonalize to ensure a valid rotation matrix.
 */
geometry_msgs::msg::Quaternion PiperGrabRotate::makeGraspOrientation(
    const WheelState& ws, const tf2::Vector3& contact) const
{
  tf2::Vector3 r, t;
  rimFrame(ws, contact, r, t);

  // Choose what the tool's Z axis should align with
  tf2::Vector3 z_axis = cfg_.tool_z_to_normal ? (-ws.n) : (-r);
  if (z_axis.length2() < 1e-12) z_axis = tf2::Vector3(0, 0, -1);
  z_axis.normalize();

  // Tool X axis along the tangent direction
  tf2::Vector3 x_axis = t;
  x_axis.normalize();

  // Tool Y axis completes right-handed frame
  tf2::Vector3 y_axis = z_axis.cross(x_axis);
  if (y_axis.length2() < 1e-12) y_axis = tf2::Vector3(0, 1, 0);
  y_axis.normalize();

  // Re-orthogonalize X to avoid accumulated numerical skew
  x_axis = y_axis.cross(z_axis);
  if (x_axis.length2() < 1e-12) x_axis = tf2::Vector3(1, 0, 0);
  x_axis.normalize();

  // Build rotation matrix with columns = (x, y, z)
  tf2::Matrix3x3 R(
    x_axis.x(), y_axis.x(), z_axis.x(),
    x_axis.y(), y_axis.y(), z_axis.y(),
    x_axis.z(), y_axis.z(), z_axis.z()
  );

  tf2::Quaternion q;
  R.getRotation(q);
  q = normalizedQuat(q);

  return tf2::toMsg(q);
}

// Pose post-processing: shift along tool's local Z
// Apply an offset along the TCP's local +Z axis without changing the grasp reference point in the wheel geometry
void PiperGrabRotate::applyTcpLocalZ(geometry_msgs::msg::PoseStamped& p) const
{
  const double dz = cfg_.tcp_local_z;
  if (std::abs(dz) < 1e-9) return;

  tf2::Quaternion q;
  tf2::fromMsg(p.pose.orientation, q);
  q = normalizedQuat(q);

  // Local Z axis expressed in planning frame
  const tf2::Vector3 z_axis = tf2::quatRotate(q, tf2::Vector3(0, 0, 1));

  p.pose.position.x += dz * z_axis.x();
  p.pose.position.y += dz * z_axis.y();
  p.pose.position.z += dz * z_axis.z();
}

/*
Create an approach pose above the rim contact.
Steps:
  - Compute the rim contact point for angle_rad.
  - Move along +wheel normal by approach_offset (stand-off).
  - Optionally set grasp orientation.
  - Apply TCP local Z correction.
*/
geometry_msgs::msg::PoseStamped PiperGrabRotate::makeApproachPose(
    const WheelState& ws,
    const geometry_msgs::msg::PoseStamped& seed,
    double angle_rad) const
{
  geometry_msgs::msg::PoseStamped out;
  out.header.frame_id = planning_frame_;
  out.pose = seed.pose;

  const tf2::Vector3 contact = rimPoint(ws, angle_rad);

  out.pose.position.x = contact.x();
  out.pose.position.y = contact.y();
  out.pose.position.z = contact.z();

  // Stand off along wheel normal (+n)
  out.pose.position.x += cfg_.approach_offset * ws.n.x();
  out.pose.position.y += cfg_.approach_offset * ws.n.y();
  out.pose.position.z += cfg_.approach_offset * ws.n.z();

  if (cfg_.set_grasp_orientation)
    out.pose.orientation = makeGraspOrientation(ws, contact);

  applyTcpLocalZ(out);
  return out;
}

/**
Create a grasp pose at/inside the rim from an approach pose.
Steps:
  - Undo approach offset to go back to the rim.
  - Inset along -normal by rim_inset (push into the rim slightly).
  - Optionally recompute grasp orientation.
  - Apply TCP local Z correction.
*/
geometry_msgs::msg::PoseStamped PiperGrabRotate::makeGraspPose(
    const WheelState& ws,
    const geometry_msgs::msg::PoseStamped& approach) const
{
  geometry_msgs::msg::PoseStamped out = approach;

  // Return from approach stand-off to actual rim contact
  out.pose.position.x -= cfg_.approach_offset * ws.n.x();
  out.pose.position.y -= cfg_.approach_offset * ws.n.y();
  out.pose.position.z -= cfg_.approach_offset * ws.n.z();

  const tf2::Vector3 contact(out.pose.position.x, out.pose.position.y, out.pose.position.z);

  // Inset along -normal (toward wheel) to "grip" the rim
  out.pose.position.x -= cfg_.rim_inset * ws.n.x();
  out.pose.position.y -= cfg_.rim_inset * ws.n.y();
  out.pose.position.z -= cfg_.rim_inset * ws.n.z();

  if (cfg_.set_grasp_orientation)
    out.pose.orientation = makeGraspOrientation(ws, contact);

  applyTcpLocalZ(out);
  return out;
}

// Set velocity/acceleration scaling for the arm. Values typically in [0..1].
void PiperGrabRotate::setSpeed(double scale)
{
  arm_.setMaxVelocityScalingFactor(scale);
  arm_.setMaxAccelerationScalingFactor(scale);
}

// Plan + execute a MoveIt pose target for the end effector. true if planning and execution succeeded.
bool PiperGrabRotate::moveToPose(const geometry_msgs::msg::PoseStamped& pose)
{
  arm_.setStartStateToCurrentState();
  arm_.clearPoseTargets();
  arm_.setPoseTarget(pose, ee_link_);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  if (arm_.plan(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "Planning failed.");
    return false;
  }

  if (arm_.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "Execution failed.");
    return false;
  }
  return true;
}

// Plan + execute a joint target move (partial targets allowed)
bool PiperGrabRotate::moveToJoints(const std::map<std::string, double>& joints)
{
  arm_.setStartStateToCurrentState();
  arm_.clearPoseTargets();
  arm_.setJointValueTarget(joints);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  if (arm_.plan(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "Joint planning failed.");
    return false;
  }

  if (arm_.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "Joint execution failed.");
    return false;
  }
  return true;
}

// Move the gripper to a joint target (open/close presets).
// Uses MoveGroupInterface::move() for simple single-group motion.
void PiperGrabRotate::moveGripper(const std::map<std::string, double>& target)
{
  gripper_.setStartStateToCurrentState();
  gripper_.setJointValueTarget(target);
  auto code = gripper_.move();
  if (code != moveit::core::MoveItErrorCode::SUCCESS)
    RCLCPP_WARN(logger_, "Gripper move failed.");
  else
    RCLCPP_INFO(logger_, "Gripper move ok.");
}

// Rotate along the wheel rim using a single Cartesian path.
// Builds waypoints on the rim, optionally rotating the tool orientation around the wheel normal (world axis ws.n),
// then calls computeCartesianPath().
bool PiperGrabRotate::rotateArcCartesian(const WheelState& ws,
                                        const geometry_msgs::msg::PoseStamped& grasp_pose,
                                        double start_angle_rad)
{
  const int steps = std::max(3, cfg_.rotate_steps);
  const double total_rad = cfg_.rotate_deg * M_PI / 180.0;

  std::vector<geometry_msgs::msg::Pose> waypoints;
  waypoints.reserve(static_cast<size_t>(steps));

  for (int i = 1; i <= steps; ++i)
  {
    const double s = static_cast<double>(i) / static_cast<double>(steps);
    const double a = start_angle_rad + total_rad * s;

    geometry_msgs::msg::Pose p = grasp_pose.pose;

    // Put TCP on the rim at angle a
    const tf2::Vector3 rim = rimPoint(ws, a);
    p.position.x = rim.x();
    p.position.y = rim.y();
    p.position.z = rim.z();

    // Maintain the rim inset
    p.position.x -= cfg_.rim_inset * ws.n.x();
    p.position.y -= cfg_.rim_inset * ws.n.y();
    p.position.z -= cfg_.rim_inset * ws.n.z();

    // Optionally rotate tool orientation with the wheel motion
    if (cfg_.rotate_orientation_with_wheel)
      p.orientation = rotateQuatAroundAxisWorld(grasp_pose.pose.orientation, ws.n, total_rad * s);

    waypoints.push_back(p);
  }

  moveit_msgs::msg::RobotTrajectory traj;
  arm_.setStartStateToCurrentState();

  // Compute cartesian path through the waypoint list
  const double fraction = arm_.computeCartesianPath(
      waypoints,
      cfg_.motion.eef_step,
      cfg_.motion.jump_thresh,
      traj,
      true);

  RCLCPP_INFO(logger_, "Cartesian path fraction: %.3f", fraction);

  // Reject paths that are too incomplete
  if (fraction < cfg_.motion.min_fraction)
  {
    RCLCPP_WARN(logger_, "Cartesian path too small (%.3f < %.3f).", fraction, cfg_.motion.min_fraction);
    return false;
  }

  // Execute the computed trajectory
  moveit::planning_interface::MoveGroupInterface::Plan plan;
  plan.trajectory_ = traj;

  if (arm_.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "Cartesian execute failed.");
    return false;
  }

  return true;
}


// Rotate along the wheel rim by planning/executing each waypoint separately.
bool PiperGrabRotate::rotateArcStep(const WheelState& ws,
                                   const geometry_msgs::msg::PoseStamped& grasp_pose,
                                   double start_angle_rad)
{
  const int steps = std::max(1, cfg_.rotate_steps);
  const double total_rad = cfg_.rotate_deg * M_PI / 180.0;

  RCLCPP_INFO(logger_, "Rotate along arc (plan/step): %d steps, total_deg=%.1f",
              steps, cfg_.rotate_deg);

  for (int i = 1; i <= steps; ++i)
  {
    const double s = static_cast<double>(i) / static_cast<double>(steps);
    const double a = start_angle_rad + total_rad * s;

    geometry_msgs::msg::PoseStamped p = grasp_pose;
    p.header.frame_id = planning_frame_;

    // Rim position at angle a
    const tf2::Vector3 rim = rimPoint(ws, a);
    p.pose.position.x = rim.x();
    p.pose.position.y = rim.y();
    p.pose.position.z = rim.z();

    // Keep inset into rim
    p.pose.position.x -= cfg_.rim_inset * ws.n.x();
    p.pose.position.y -= cfg_.rim_inset * ws.n.y();
    p.pose.position.z -= cfg_.rim_inset * ws.n.z();

    // Optionally rotate tool orientation with wheel rotation
    if (cfg_.rotate_orientation_with_wheel)
      p.pose.orientation = rotateQuatAroundAxisWorld(grasp_pose.pose.orientation, ws.n, total_rad * s);

    applyTcpLocalZ(p);

    if (!moveToPose(p))
      return false;
  }

  return true;
}

/*
Add a small delta to one joint and execute the motion.
  - Reads current joint values.
  - Adds delta_rad to joint_name.
  - Optionally clamps to joint limits.
  - Plans and executes with a speed scaling.
*/
bool PiperGrabRotate::nudgeJoint(const std::string& joint_name,
                                 double delta_rad,
                                 double speed_scale,
                                 bool clamp)
{
  const auto names = arm_.getJointNames();
  auto vals = arm_.getCurrentJointValues();


  // Find index of the requested joint
  int idx = -1;
  for (size_t i = 0; i < names.size(); ++i)
  {
    if (names[i] == joint_name) { idx = static_cast<int>(i); break; }
  }

  if (idx < 0 || idx >= static_cast<int>(vals.size()))
  {
    RCLCPP_WARN(logger_, "nudgeJoint: joint '%s' not found in group '%s'",
                joint_name.c_str(), cfg_.arm_group.c_str());
    return false;
  }

  double target = vals[idx] + delta_rad;

  // Optionally clamp to joint bounds from the robot model
  if (clamp)
  {
    const auto state = arm_.getCurrentState();
    if (state)
    {
      const auto* jm = state->getRobotModel()->getJointModel(joint_name);
      if (jm && !jm->getVariableBounds().empty())
      {
        const auto& b = jm->getVariableBounds()[0];
        if (b.position_bounded_)
        {
          target = std::min(std::max(target, b.min_position_), b.max_position_);
        }
      }
    }
  }

  vals[idx] = target;

  setSpeed(speed_scale);
  arm_.setStartStateToCurrentState();
  arm_.clearPoseTargets();
  arm_.setJointValueTarget(vals);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  if (arm_.plan(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "nudgeJoint: planning failed for %s (delta=%.3f rad)",
                joint_name.c_str(), delta_rad);
    return false;
  }

  if (arm_.execute(plan) != moveit::core::MoveItErrorCode::SUCCESS)
  {
    RCLCPP_WARN(logger_, "nudgeJoint: execution failed for %s", joint_name.c_str());
    return false;
  }

  RCLCPP_INFO(logger_, "nudgeJoint: %s += %.2f deg",
              joint_name.c_str(), delta_rad * 180.0 / M_PI);
  return true;
}

// Main sequence: open -> approach -> grasp -> rotate -> release -> retract
bool PiperGrabRotate::run()
{
  // Resolve wheel center/orientation/normal in planning frame  
  auto ws_opt = resolveWheel();
  if (!ws_opt)
    return false;

  const WheelState& ws = *ws_opt;

  RCLCPP_INFO(logger_, "Wheel(planning): c=(%.4f %.4f %.4f) n=(%.4f %.4f %.4f)",
              ws.c.x(), ws.c.y(), ws.c.z(),
              ws.n.x(), ws.n.y(), ws.n.z());

  // Start angle on the wheel rim (in radians)
  const double a0 = cfg_.start_angle_deg * M_PI / 180.0;

  // Use current EE pose as seed for orientation/other fields
  auto seed = arm_.getCurrentPose(ee_link_);

  // Optional: set joint6 to a pre-grasp configuration to help IK stability
  if (cfg_.use_pregrasp_joint6)
  {
    RCLCPP_INFO(logger_, "Pregrasp: setting joint6 to %.3f rad", cfg_.pregrasp_joint6_rad);
    std::map<std::string, double> j;
    j["joint6"] = cfg_.pregrasp_joint6_rad;
    setSpeed(cfg_.motion.fast);
    if (!moveToJoints(j))
      return false;

    seed = arm_.getCurrentPose(ee_link_);
  }

  // Build approach + grasp poses for the rim contact at angle a0
  auto approach = makeApproachPose(ws, seed, a0);
  auto grasp    = makeGraspPose(ws, approach);

  RCLCPP_INFO(logger_, "Approach target: x=%.3f y=%.3f z=%.3f (frame=%s)",
              approach.pose.position.x, approach.pose.position.y, approach.pose.position.z,
              approach.header.frame_id.c_str());
  RCLCPP_INFO(logger_, "Grasp target:    x=%.3f y=%.3f z=%.3f (frame=%s)",
              grasp.pose.position.x, grasp.pose.position.y, grasp.pose.position.z,
              grasp.header.frame_id.c_str());

  setSpeed(cfg_.motion.fast);

  // A) Ensure gripper is open before approaching
  RCLCPP_INFO(logger_, "A) Gripper open");
  moveGripper(cfg_.gripper.open);
  std::this_thread::sleep_for(400ms);

  // 1) Move to stand-off approach pose
  RCLCPP_INFO(logger_, "1) Move to approach");
  if (!moveToPose(approach))
    return false;

  // 2) Move into grasp pose slowly (more control near contact)
  RCLCPP_INFO(logger_, "2) Move to grasp (slow)");
  setSpeed(cfg_.motion.slow);
  if (!moveToPose(grasp))
    return false;

  // 3) Close gripper to grasp the rim
  RCLCPP_INFO(logger_, "3) Close gripper");
  moveGripper(cfg_.gripper.close);
  std::this_thread::sleep_for(600ms);

  // 4) Rotate the wheel by moving along the rim arc
  RCLCPP_INFO(logger_, "4) Rotate along wheel plane");
  setSpeed(cfg_.motion.slow);

  bool ok = false;
  if (cfg_.motion.cartesian)
    ok = rotateArcCartesian(ws, grasp, a0);
  else
    ok = rotateArcStep(ws, grasp, a0);

  if (!ok)
    return false;

  setSpeed(cfg_.motion.fast);

  // 5) Release the rim
  RCLCPP_INFO(logger_, "5) Open gripper (release)");
  moveGripper(cfg_.gripper.open);
  std::this_thread::sleep_for(400ms);

  // Small corrective joint move (often used to avoid singularities / improve clearance
  if (!nudgeJoint("joint4", -2.0 * M_PI / 180.0, cfg_.motion.slow))
    return false;

  // 6) Retract along TCP local -Z (relative to current tool orientation)
  RCLCPP_INFO(logger_, "6) Retract along TCP local -Z");
  auto retract = arm_.getCurrentPose(ee_link_);
  {
    tf2::Quaternion q;
    tf2::fromMsg(retract.pose.orientation, q);
    q = normalizedQuat(q);
    // TCP local +Z expressed in planning/world frame
    tf2::Vector3 z = tf2::quatRotate(q, tf2::Vector3(0,0,1));
    // Move backwards along tool axis (i.e., along local -Z)
    retract.pose.position.x += (-0.10) * z.x();
    retract.pose.position.y += (-0.10) * z.y();
    retract.pose.position.z += (-0.10) * z.z();
  }
  if (!moveToPose(retract))
    return false;

  // 7) Return to approach pose (safe stand-off position)
  RCLCPP_INFO(logger_, "7) Return to approach");
  if (!moveToPose(approach))
    return false;

  RCLCPP_INFO(logger_, "Grab+Rotate finished.");
  return true;
}
