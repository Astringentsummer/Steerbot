from omni.isaac.core.utils.xforms import get_world_pose

g = "/World/BAKScene2/g29_rotate_right_tilted27degrees/grasp_marker"
c = "/World/BAKScene2/g29_rotate_right_tilted27degrees/center_marker"

pos_g, quat_g = get_world_pose(g)
pos_c, quat_c = get_world_pose(c)

print("GRASP world xyz:", pos_g)
print("CENTER world xyz:", pos_c)
print("GRASP world quat:", quat_g)

