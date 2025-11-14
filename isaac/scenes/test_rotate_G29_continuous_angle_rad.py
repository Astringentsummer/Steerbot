import omni
import math, time
from pxr import UsdPhysics

stage = omni.usd.get_context().get_stage()
joint = UsdPhysics.RevoluteJoint.Get(stage, "/G29_root/RevoluteJoint")
drive = UsdPhysics.DriveAPI(joint.GetPrim(), "angular")

print("Simulating G29 input... press Ctrl+C to stop")

t = 0.0
try:
    while True:
        angle_rad = math.sin(t) * math.radians(90) 
        drive.CreateTargetPositionAttr(angle_rad * 180.0 / math.pi)
        time.sleep(0.05)
        t += 0.1
except KeyboardInterrupt:
    print("Simulation stopped.")
