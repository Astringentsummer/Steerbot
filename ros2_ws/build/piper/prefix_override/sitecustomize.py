import sys
if sys.prefix == '/home/students_steeringwheel/ros2_env':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/students_steeringwheel/Steeringwheel-Workspace/ros2_ws/install/piper'
