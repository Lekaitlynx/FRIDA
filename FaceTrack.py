import cv2
import time
import subprocess
from gpiozero import Servo
import gpiozero

# Setup PiGPIO for hardware PWM
#factory = PiGPIOFactory(host='localhost')
#pigpio.pi('soft', 8888)

# Setup servos on BCM pins 18 (X) and 13 (Y)
servo = Servo(17, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000)

def angle_to_servo(val):                # Converts 0–180 to -1 to 1
    return (val / 90.0) - 1.0

# Load face cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

print("Starting face tracking using fswebcam...")

try:
    while True:
        # Capture image using fswebcam
        subprocess.run([
            'fswebcam',
            '--quiet',
            '-r', '320x240',
            '--no-banner',
            'snapshot.jpg'
        ])

        # Load the image and convert to grayscale
        img = cv2.imread('snapshot.jpg')
        if img is None:
            print("Failed to capture image.")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            xn = (x + x + w) / 2
            yn = (y + y + h) / 2

            # Print face position in the image
            print(f"Face detected at X: {xn}, Y: {yn}")
            
            # Draw rectangle around face
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Convert image back to BGR for display
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # Show the image with detected faces
            cv2.imshow('Face Detection', img_bgr)

            # Wait for a key press to close the window or refresh the image
            key = cv2.waitKey(1)  # 1 ms delay
            if key == 27:  # ESC key
                break
                
                
            # Horizontal control (commented out for now)
            if xn > 200:
                tx = max(-1, tx - 0.05)
                print(f"Hleft: {xn:.2f}")
            elif xn < 100:
                tx = min(1, tx + 0.05)
                print(f"Hright: {xn:.2f}")
            else:
                print(f"Hcentered: {xn:.2f}")
        
            # Vertical control (commented out for now)
            if yn > 180:
                ty = max(-1, ty - 0.05)
                print(f"Vdown: {yn:.2f}")
            elif yn < 120:
                ty = min(1, ty + 0.05)
                print(f"Vup: {yn:.2f}")
            else:
                print(f"Vcentered: {yn:.2f}")
            
            servo_x.value = tx
            servo_y.value = ty

            break  # Process only one face
        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")

# Cleanup servo values (commented out for now)
finally:
    servo_x.value = None
    servo_y.value = None
