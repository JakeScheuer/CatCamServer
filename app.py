from flask import Flask, Response, request
from flask_sock import Sock
from camera_pi import Camera
import RPi.GPIO as GPIO
import time

LASER_PIN = 13
CAM_X_SERVO_PIN = 11
CAM_Y_SERVO_PIN = 12
LASER_X_SERVO_PIN = 15
LASER_Y_SERVO_PIN = 16
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

@app.route('/')
def index():
    return 'Hello There!!!'

@app.route('/camera_feed')
def video_feed():
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundry=frame')

@sock.route('/camera_controls')
def camera_controls(ws):
    global cam_x_angle
    global cam_y_angle

    while True:
        command = ws.receive()
        p_command = command.split(" ")[1] #ex: "cam: left"
        if p_command == "left":
            if cam_x_angle < 180:
                cam_x_angle += 10
                cam_x_servo.ChangeDutyCycle(2+(cam_x_angle/18))
                time.sleep(0.5)
                cam_x_servo.ChangeDutyCycle(0)
        if p_command == "right":
            if cam_x_angle > 0:
                cam_x_angle -= 10
                cam_x_servo.ChangeDutyCycle(2+(cam_x_angle/18))
                time.sleep(0.5)
                cam_x_servo.ChangeDutyCycle(0)
        if p_command == "up":
            if cam_y_angle < 180:
                cam_y_angle += 10
                cam_y_servo.ChangeDutyCycle(2+(cam_y_angle/18))
                time.sleep(0.5)
                cam_y_servo.ChangeDutyCycle(0)
        if p_command == "left":
            if cam_y_angle > 0:
                cam_y_angle -= 10
                cam_y_servo.ChangeDutyCycle(2+(cam_y_angle/18))
                time.sleep(0.5)
                cam_y_servo.ChangeDutyCycle(0)

@sock.route('/laser_controls')
def laser_command(ws):
    while True:
        command = ws.receive()
        if command == "turn off":
            toggle_laser(False)
        elif command == "turn on":
            toggle_laser(True)
        elif command[0:4] == "move": #ex: "move: x:120 y:10"
            vals = command.split(":")
            x_val = vals[1].split(" ")[0]
            y_val = vals[2]
            move_laser(float(x_val), float(y_val))

if __name__ == '__main__':
    try:
        socketio.run(app)
    
    except KeyboardInterrupt:
        pass
    
    finally:
        cam_x_servo.stop()
        cam_y_servo.stop()
        laser_x_servo.stop()
        laser_y_servo.stop()
        GPIO.cleanup()
        print("Goodbye!")
        pass