import omni.usd
from pxr import UsdGeom, Gf
import math

stage = omni.usd.get_context().get_stage()

base = stage.GetPrimAtPath("/G29_root/Steerbot_G29_base_position_27degrees")
wheel = stage.GetPrimAtPath("/G29_root/Steerbot_G29_steerwheel_position_27degrees")

if base and wheel:
    base_xform = UsdGeom.Xformable(base)
    wheel_xform = UsdGeom.Xformable(wheel)
    
    # Calculate relative rotation
    relative = wheel_xform.GetLocalTransformation() * base_xform.GetLocalTransformation().GetInverse()
    rotation = relative.ExtractRotation()
    
    # GetAngle() returns DEGREES
    angle_deg = rotation.GetAngle()  # Unit: degrees
    axis = rotation.GetAxis()
    
    # Print axis first
    print(f"Axis: ({axis[0]:.3f}, {axis[1]:.3f}, {axis[2]:.3f})")
    
    # Determine direction from axis
    if axis[1] > 0.01:
        direction = "LEFT"
    elif axis[1] < -0.01:
        direction = "RIGHT"
    else:
        direction = "CENTER"
    
    print(f"Direction: {direction}")
    
    # Process angle: modulo 360 degrees
    angle_mod_deg = angle_deg % 360.0
    
    # Convert to [-180, 180] range
    if angle_mod_deg > 180.0:
        steering_deg = angle_mod_deg - 360.0
    else:
        steering_deg = angle_mod_deg
    
    # Adjust sign based on direction
    if direction == "RIGHT":
        steering_deg = -abs(steering_deg)
    elif direction == "LEFT":
        steering_deg = abs(steering_deg)
    
    # Convert to radians
    steering_rad = steering_deg * math.pi / 180.0
    
    # Print steering angle
    print(f"Steering angle: {steering_deg:.2f}° = {steering_rad:.6f} rad")
    
    # For logging/recording, return the values
    print("\n--- Data for recording ---")
    print(f"angle_rad: {steering_rad:.6f}")
    print(f"angle_deg: {steering_deg:.2f}")
    print(f"direction: {direction}")


# out sample
# --- Data for recording ---
# angle_rad: 0.000000
# angle_deg: 0.00
# direction: CENTER

# need to fix
# Problem: When left turn exceeds 270°, it's recognized as right turn.
# When right turn exceeds 90°, it's recognized as left turn.
