set -e

# Standardwerte
fake_hardware=false
use_sim_time=false

echo "Übergebene Argumente: $@"

# Argumente auswerten (-r = real, -s = sim)
while getopts "rs" opt; do
  case $opt in
    r)
      echo "Echte Hardware gewählt (-r)"
      fake_hardware=false
      use_sim_time=false
      ;;
    s)
      echo "Simulation gewählt (-s)"
      fake_hardware=true
      use_sim_time=true
      ;;
    *)
      echo "Ungültiges Argument. Verwende -r (real) oder -s (sim)."
      exit 1
      ;;
  esac
done

echo "use_fake_hardware=${fake_hardware}"
echo "use_sim_time=${use_sim_time}"
echo ""

# Funktion: neues Terminal starten
start_terminal() {
  gnome-terminal -- bash -c "$1; exec bash" &
  terminal_pids+=($!)
}

# Funktion: alle gestarteten Terminals schließen
kill_all() {
  echo ""
  echo "Beende alle gestarteten ROS2-Terminals..."
  for pid in "${terminal_pids[@]}"; do
    kill -9 "$pid" 2>/dev/null || true
  done
  # als Fallback ALLE gnome-terminals killen, die noch laufen
  pkill -9 gnome-terminal || true
  echo "Alle Terminals beendet."
}

# Array für gestartete Terminals
terminal_pids=()

# --- STARTS ---
echo "Starte Controller Bringup..."
start_terminal "cd ~/Steerbot/ros2_ws; \
  source /opt/ros/humble/setup.bash; \
  source install/setup.bash; \
  ros2 launch piper_with_gripper_moveit controller_bringup_gripper.launch.py fake_hardware:=${fake_hardware}"

sleep 6

echo "Starte MoveIt DT..."
start_terminal "cd ~/Steerbot/ros2_ws; \
  source /opt/ros/humble/setup.bash; \
  source install/setup.bash; \
  ros2 launch piper_with_gripper_moveit moveit_dt_gripper.launch.py use_sim_time:=${use_sim_time}"

sleep 3

echo ""
echo "========================================="
echo "Drücke [ENTER], um **ALLE Terminals** zu schließen."
echo "========================================="
read -r

# --- STOP ---
kill_all

