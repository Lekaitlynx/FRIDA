from gpiozero import Servo
from time import sleep

# initialize the servo on GPIO17 with a 0.5–2.5 ms pulse range
servo = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

def angle_to_value(angle):
    """
    Convert 0–180° → -1…+1 for gpiozero.Servo.value
    -1 is 0°, 0 is 90°, +1 is 180°
    """
    return (angle / 90.0) - 1

while True:
    print("Moving to 0°")
    servo.min()          # equivalent to value = -1
    sleep(1)

    print("Moving to 15°")
    servo.value = angle_to_value(15)
    sleep(1)

    print("Moving to 45°")
    servo.value = angle_to_value(45)
    sleep(1)

    print("Moving to 60°")
    servo.value = angle_to_value(60)
    sleep(1)

    print("Moving to 90°")
    servo.value = 0      # mid-point
    sleep(1)

    print("Moving to 110°")
    servo.value = angle_to_value(110)
    sleep(1)

    print("Moving to 180°")
    servo.max()          # equivalent to value = +1
    sleep(1)
