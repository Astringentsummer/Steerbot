import pygame
from omni.isaac.kit import SimulationApp

simulation_app = SimulationApp({"headless": False})

import omni.isaac.core.utils.prims as prim_utils
from omni.isaac.core import World
from omni.isaac.core.articulations import Articulation
from omni.isaac.urdf import _urdf

# Initialize Pygame for joystick input
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Load Piper robot from URDF
URDF_PATH = "c:/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/urdf/piper_arm.urdf"
PIPER_PRIM_PATH = "/World/Piper"
prim_utils.create_prim(PIPER_PRIM_PATH, "Xform")
urdf_interface = _urdf.acquire_urdf_interface()
urdf_interface.parse_urdf(URDF_PATH, PIPER_PRIM_PATH + "/piper")

world = World(stage_units_in_meters=1.0)
world.reset()
piper = Articulation(PIPER_PRIM_PATH + "/piper")
world.scene.add(piper)

# Joint names (adjust if needed)
joint_names = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint7"]

def get_g29_input():
    pygame.event.pump()
    steering = joystick.get_axis(0)  # Steering wheel axis
    throttle = joystick.get_axis(2)  # Pedal axis
    brake = joystick.get_axis(3)     # Pedal axis
    button_a = joystick.get_button(0)  # Example button
    return steering, throttle, brake, button_a

def send_commands_to_piper(steering, throttle, brake, button_a):
    # Map G29 input to joint positions
    joint_positions = [0.0] * 7
    joint_positions[0] = steering * 2.6  # joint1: [-2.6, 2.6] rad
    joint_positions[1] = (throttle + 1) / 2 * 3.14  # joint2: [0, 3.14] rad
    joint_positions[2] = (brake + 1) / 2 * 3.14     # joint3: [0, 3.14] rad
    # ... set other joints as needed ...
    joint_positions[6] = 0.035 if button_a else 0.0  # gripper open/close
    # Send to Isaac Sim
    piper.set_joint_positions(joint_positions, joint_names=joint_names)

while simulation_app.is_running():
    world.step(render=True)
    steering, throttle, brake, button_a = get_g29_input()
    send_commands_to_piper(steering, throttle, brake, button_a)

simulation_app.close()