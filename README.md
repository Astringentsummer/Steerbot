Done:

Physical setup of G29 in Isaac sim: isaac/scenes/g29_rotate_right_tilted27degrees.usd 


To do:

Physical setup of Piper


Integration: a stage with G29 and Arm robot.

notice: 


Combine all developed modules (engine visualization, ROS2 communication, G29 input) into a single integrated simulation setup inside Isaac Sim

The G29 must be physically stable on the table, with correct colliders, inertia, and a properly aligned steering-wheel joint that can rotate smoothly.

The Piper arm must stand stably (fixed or supported), with all joints moving correctly and controllable from Isaac or MoveIt.

Both models must show no penetration, no jitter, and no articulation warnings when the simulation runs
