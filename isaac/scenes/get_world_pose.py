import omni.usd
from pxr import UsdGeom

stage = omni.usd.get_context().get_stage()

parent = "/World/BAKScene2/g29_rotate_right_tilted27degrees"

def ensure_xform(path):
    prim = stage.GetPrimAtPath(path)
    if prim.IsValid():
        return
    UsdGeom.Xform.Define(stage, path)
    print("Created:", path)

ensure_xform(parent + "/grasp_marker")
ensure_xform(parent + "/center_marker")

print("Done. Now select and move the markers with W.")
