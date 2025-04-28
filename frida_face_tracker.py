import time
import random
import cv2

from gpiozero import Servo, LED

# ————— Hardware Setup —————
LED_PIN     = 17
SERVO_PIN   = 18
AUTOTIMEOUT = 4.0    # seconds before re-sweeping if no face

led   = LED(LED_PIN)
servo = Servo(SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

def angle_to_servo(a: float) -> float:
    return (a / 90.0) - 1.0

def move_servo_smooth(start: int, end: int, speed_dps: float):
    step  = 1 if end > start else -1
    delay = 1.0 / speed_dps
    for a in range(start, end + step, step):
        servo.value = angle_to_servo(a)
        time.sleep(delay)

def autonomous_sweep(curr: int) -> int:
    choice = random.choice(['small','medium','large'])
    if choice=='small':
        delta, speed = random.randint(-20,20), random.uniform(40,80)
    elif choice=='medium':
        delta, speed = random.randint(-60,60), random.uniform(20,40)
    else:
        delta, speed = (0 if curr>90 else 180)-curr, random.uniform(10,20)
    target = max(0, min(180, curr+delta))
    move_servo_smooth(curr, target, speed)
    time.sleep(random.uniform(0.3,1.5))
    return target

# ————— OpenCV Face Detection —————
cap = cv2.VideoCapture(0)  
cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
def face_present() -> bool:
    ret, frame = cap.read()
    if not ret:
        return False
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 5)
    return len(faces) > 0

# ————— Main Loop —————
try:
    curr = 90
    servo.value = angle_to_servo(curr)
    last_seen = time.time()

    while True:
        if face_present():
            led.off()
            last_seen = time.time()
            # hold position until face disappears
            time.sleep(0.1)
        else:
            led.on()
            # if we just lost the face and it's been >AUTOTIMEOUT, sweep again
            if time.time() - last_seen > AUTOTIMEOUT:
                curr = autonomous_sweep(curr)
                last_seen = time.time()
            else:
                time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    cap.release()
    servo.detach()
    led.off()
