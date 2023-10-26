from flask import Flask, Response, request
from flask_sock import Sock
from camera_pi import Camera
import RPi.GPIO as GPIO
import time

LASER_PIN = 13
CAM_X_SERVO_PIN = 16
CAM_Y_SERVO_PIN = 15
LASER_X_SERVO_PIN = 11
LASER_Y_SERVO_PIN = 12
FREQUENCY_HTZ = 50

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LASER_PIN, GPIO.OUT)
GPIO.setup(CAM_X_SERVO_PIN, GPIO.OUT)
GPIO.setup(CAM_Y_SERVO_PIN, GPIO.OUT)
GPIO.setup(LASER_X_SERVO_PIN, GPIO.OUT)
GPIO.setup(LASER_Y_SERVO_PIN, GPIO.OUT)

cam_x_servo = GPIO.PWM(CAM_X_SERVO_PIN, FREQUENCY_HTZ)
cam_y_servo = GPIO.PWM(CAM_Y_SERVO_PIN, FREQUENCY_HTZ)
laser_x_servo = GPIO.PWM(LASER_X_SERVO_PIN, FREQUENCY_HTZ)
laser_y_servo = GPIO.PWM(LASER_Y_SERVO_PIN, FREQUENCY_HTZ)

cam_x_servo.start(0)
cam_y_servo.start(0)
laser_x_servo.start(0)
laser_y_servo.start(0)

app = Flask(__name__)
sock = Sock(app)

global cam_x_angle
global cam_y_angle
cam_x_angle = 0
cam_y_angle = 0

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def toggle_laser(turnOn):
    pin_setting = GPIO.HIGH if turnOn else GPIO.LOW
    GPIO.output(LASER_PIN, pin_setting)

def move_laser(x_val, y_val):
    laser_x_servo.ChangeDutyCycle(2+(x_val/18))
    laser_y_servo.ChangeDutyCycle(2+(x_val/18))
    time.sleep(0.2)
    laser_x_servo.ChangeDutyCycle(0)
    laser_y_servo.ChangeDutyCycle(0)

 def move_camera(direction):
    if direction == "left":
        if cam_x_angle < 180:
            cam_x_angle += 10
            cam_x_servo.ChangeDutyCycle(2+(cam_x_angle/18))
            time.sleep(0.5)
            cam_x_servo.ChangeDutyCycle(0)
    elif direction == "right":
        if cam_x_angle > 0:
            cam_x_angle -= 10
            cam_x_servo.ChangeDutyCycle(2+(cam_x_angle/18))
            time.sleep(0.5)
            cam_x_servo.ChangeDutyCycle(0)
    elif direction == "up":
        if cam_y_angle < 180:
            cam_y_angle += 10
            cam_y_servo.ChangeDutyCycle(2+(cam_y_angle/18))
            time.sleep(0.5)
            cam_y_servo.ChangeDutyCycle(0)
    elif direction == "left":
        if cam_y_angle > 0:
            cam_y_angle -= 10
            cam_y_servo.ChangeDutyCycle(2+(cam_y_angle/18))
            time.sleep(0.5)
            cam_y_servo.ChangeDutyCycle(0)

@app.route('/')
def index():
    return 'Hello There!!!'

@app.route('/camera_feed')
def video_feed():
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundry=frame')

# laser: on, off
# cam: left, right, up, down
# move: x:180 y:10
@sock.route('/controls')
def controls(ws):
    global cam_x_angle = 0
    global cam_y_angle = 0

    while True:
        command = ws.receive()
        args = command.split(" ")
        device = args[0]
        if device == "laser:":
            is_on = args[1] == "on"
            toggle_laser(is_on)
        elif device == "cam:":
            direction = args[1]
            move_camera(direction)
        elif device == "move:":
            x_val = args[1].split(":")[1]
            y_val = args[2].split(":")[1]
            move_laser(float(x_val), float(y_val))

if __name__ == '__main__':
    try:
        socketio.run(app)
    
    except KeyboardInterrupt:
        continue
    
    finally:
        cam_x_servo.stop()
        cam_y_servo.stop()
        laser_x_servo.stop()
        laser_y_servo.stop()
        GPIO.cleanup()
        print("Goodbye!")
        pass