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

  rclcpp::executors::SingleThreadedExecutor exec;
  exec.add_node(node);
  std::thread spinner([&exec]() { exec.spin(); });

  std::this_thread::sleep_for(2s);

  PiperGrabRotate::Config cfg;  // possible to change defaults here
  // cfg.ee_link_override = "tool0"; //  

  PiperGrabRotate app(node, cfg);
  (void)app.run();

  exec.cancel();
  if (spinner.joinable()) spinner.join();
  rclcpp::shutdown();
  return 0;
}
