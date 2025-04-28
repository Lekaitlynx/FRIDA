#!/usr/bin/env python3
import time
import serial

from gpiozero import Servo, LED

# ——————— Configuration ————————
SERIAL_PORT       = '/dev/ttyUSB0'
BAUD_RATE         = 115200
AUTOSWEEP_DELAY_S = 4.0    # ms > this → start sweep()

# GPIO pins
LED_PIN    = 17            # approximate Arduino LED_BUILTIN
SERVO_PIN  = 18

# Servo pulse widths (tweak if your servo is twitchy)
MIN_PULSE = 0.0005
MAX_PULSE = 0.0025

# ——————— Globals ———————
ser           = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
led           = LED(LED_PIN)
servo         = Servo(SERVO_PIN, min_pulse_width=MIN_PULSE, max_pulse_width=MAX_PULSE)

init_pos      = 90        # start at 90°
curr_pos      = 90
received_int  = 0
last_move_ts  = time.time()

# ——————— Helpers ———————
def angle_to_servo(a: float) -> float:
    """Map 0–180° → gpiozero’s -1…+1"""
    return (a / 90.0) - 1.0

def move_servo(initial: int, final: int, speed: float):
    """
    Smoothly move from initial→final.
    `speed` here is the same value you passed to Arduino (deg/sec);
    we convert it into a delay per 2° step.
    """
    global curr_pos, last_move_ts
    # 1000/speed was your ms-per-2°; convert to seconds:
    time_step = (1000.0 / speed) / 1000.0
    # clamp to max 40 ms (Arduino min(time_step,40))
    delay = min(time_step, 0.04)
    step  = 2 if final > initial else -2

    for pos in range(initial, final + step, step):
        # if a “face” serial msg arrived, bail out early
        if not check_face():      
            return
        curr_pos = pos
        servo.value = angle_to_servo(curr_pos)
        time.sleep(delay)

def sweep():
    """Alternate sweeping to 0° then 180°."""
    move_servo(curr_pos, 0,   10)
    time.sleep(0.1)
    move_servo(curr_pos, 180, 10)

def check_face() -> bool:
    """
    Read one line from serial if available:
     - “OK” blink → LED off  
     - store int in received_int  
    Then, if received_int≠0, step curr_pos by ±1 at rate ∝ |received_int|,
    exactly like your Arduino code.  
    Returns True if received_int≠0 (i.e. we “moved”).
    """
    global received_int, curr_pos, last_move_ts

    if ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        print("OK")
        led.off()
        try:
            received_int = int(line)
        except ValueError:
            received_int = 0

    # if non-zero, we’ll “nudge” the head
    if received_int < 0:
        last_move_ts = time.time()
        step_delay = min((-1.0 / received_int), 0.04)
        curr_pos = min(180, curr_pos + 1)
        time.sleep(step_delay)

    elif received_int > 0:
        last_move_ts = time.time()
        step_delay = min((1.0 / received_int), 0.04)
        curr_pos = max(0, curr_pos - 1)
        time.sleep(step_delay)

    else:
        # no data → LED on (waiting)
        led.on()

    # always update the servo
    servo.value = angle_to_servo(curr_pos)
    # return whether we actually moved
    return (received_int != 0)

# ——————— Main loop ———————
if __name__ == "__main__":
    try:
        # home position
        servo.value = angle_to_servo(init_pos)

        while True:
            # handle any incoming serial “face” commands
            check_face()

            # if it’s been quiet for >AUTOSWEEP_DELAY_S, do a sweep()
            if time.time() - last_move_ts > AUTOSWEEP_DELAY_S:
                sweep()
                last_move_ts = time.time()

    except KeyboardInterrupt:
        pass

    finally:
        servo.detach()
        ser.close()
        led.off()
