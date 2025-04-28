from gpiozero import Servo
from time import sleep

servo = Servo(17, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000)

while True:
    print("Moving to 0")
    servo.min()
    sleep(1)
    
    print("Moving to 15")
    servo.min()
    sleep(1)
    
    print("Moving to 45")
    servo.min()
    sleep(1)
    
    print("Moving to 60")
    servo.min()
    sleep(1)
    
    print("Moving to 90")
    servo.value = 0
    sleep(1)
    
    print("Moving to 110")
    servo.value = 0
    sleep(1)
    
    print("Moving to 180")
    servo.max()
    sleep(1)
