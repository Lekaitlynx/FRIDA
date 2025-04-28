from gpiozero import Servo
from time import sleep

# === CONFIG ===
GPIO_PIN       = 17
MIN_PULSE      = 0.5/1000    # 0.5 ms = your 0°
MAX_PULSE      = 2.5/1000    # 2.5 ms = your 180°
STEP_DELAY     = 0.1         # seconds between each 1° micro-step
PAUSE_AT_TARGET = 2          # seconds to hold at each target angle
ANGLES         = [0, 15, 45, 60, 90, 110, 180]
# ===============

servo = Servo(GPIO_PIN, min_pulse_width=MIN_PULSE, max_pulse_width=MAX_PULSE)

def angle_to_value(angle):
    """Map 0–180° → -1…+1 for gpiozero.Servo.value."""
    return (angle / 90.0) - 1

def slow_to(angle, delay=STEP_DELAY):
    """
    Sweep from current → angle in 1° steps,
    pausing `delay` seconds between each.
    """
    # clamp into [0,180]
    angle = max(0, min(180, angle))

    # figure out where we are now
    cur_val = servo.value if servo.value is not None else -1
    cur_ang = (cur_val + 1) * 90   # back to 0–180°

    step = 1 if angle > cur_ang else -1
    # micro-step in 1° increments
    for deg in range(int(cur_ang), int(angle) + step, step):
        servo.value = angle_to_value(deg)
        sleep(delay)
    # land exactly on the target
    servo.value = angle_to_value(angle)

# === MAIN SWEEP ===
for tgt in ANGLES:
    print(f"Moving to {tgt}°…")
    slow_to(tgt)                   # slow sweep
    print(f"Holding at {tgt}° for {PAUSE_AT_TARGET}s")
    sleep(PAUSE_AT_TARGET)

print("Done sweeping all angles. Exiting.")
