#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/single_threaded_executor.hpp>

#include "piper_demo/piper_grab_rotate.hpp"

#include <thread>
#include <chrono>

using namespace std::chrono_literals;

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("piper_grab_rotate_node");

  // Mode-Parameter (rotate | hold)
  const std::string mode = node->declare_parameter<std::string>("mode", "rotate");

  // Executor (for TF, MoveIt etc.)
  rclcpp::executors::SingleThreadedExecutor exec;
  exec.add_node(node);
  std::thread spinner([&exec]() { exec.spin(); });

  // Wait until TF / MoveIt are safely there
  std::this_thread::sleep_for(2s);

  // App + Config
  PiperGrabRotate::Config cfg;
  // cfg.ee_link_override = "tool0"; // optional

  PiperGrabRotate app(node, cfg);

  // Mode selection
  bool ok = false;
  if (mode == "rotate")
  {
    RCLCPP_INFO(node->get_logger(), "Mode = ROTATE");
    ok = app.run();
  }
  else if (mode == "hold")
  {
    RCLCPP_INFO(node->get_logger(), "Mode = HOLD (Ctrl+C to stop)");
    ok = app.runHold();   // runs endlessly until launch is completed
  }
  else
  {
    RCLCPP_ERROR(node->get_logger(),
                 "Unknown mode '%s'. Use: rotate | hold",
                 mode.c_str());
    ok = false;
  }
  
  exec.cancel();
  if (spinner.joinable())
    spinner.join();

  rclcpp::shutdown();
  return ok ? 0 : 1;
}
