import os
import shutil

src_dir = r"c:/Users/rohit/Downloads/Steerbot-Gripper/piper_ros/src/piper_description/urdf"
dst_dir = r"c:/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/urdf"

files_to_copy = [
    "temp_piper_steering.urdf",
    "base_link.STL", "link1.STL", "link2.STL", "link3.STL", 
    "link4.STL", "link5.STL", "link6.STL", "link7.STL", "link8.STL"
]

print(f"Copying assets from {src_dir} to {dst_dir}...")

for f in files_to_copy:
    src = os.path.join(src_dir, f)
    dst = os.path.join(dst_dir, "piper_arm.urdf" if f == "temp_piper_steering.urdf" else f)
    
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied: {f} -> {dst}")
    else:
        print(f"WARNING: Source not found: {f}")

print("Done.")
