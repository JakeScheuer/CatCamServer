from flask import Flask, Response, render_template, request
from flask_sock import Sock
from adafruit_servokit import ServoKit
from gpiozero import LED
import time
import atexit
import cv2
import numpy as np

camera = cv2.VideoCapture(0)
kit = ServoKit(channels=16)
laser_pin = LED(21,active_high=False)
cam_x = kit.servo[2]
cam_y = kit.servo[3]
laser_x = kit.servo[0]
laser_y = kit.servo[1]
 
def reset_servos():
    laser_x.angle = 90
    time.sleep(0.5)
    laser_y.angle = 45
    time.sleep(0.5)
    cam_x.angle = 90
    time.sleep(0.5)
    cam_y.angle = 45
    time.sleep(0.5)

def toggle_laser(turnOn):
    if turnOn:
        laser_pin.on()
    else:
        laser_pin.off()

def decrease_angle(servo):
    if servo.angle is None or servo.angle > 0:
        try:
            servo.angle -= 10
        except ValueError:
            pass

def increase_angle(servo):
    if servo.angle is None or servo.angle < 180:
        try: 
            servo.angle += 10
        except ValueError:
            pass

def move_camera(direction):
    if direction == "left":
        increase_angle(cam_x)
    elif direction == "right":
        decrease_angle(cam_x)
    elif direction == "up":
        decrease_angle(cam_y)
    elif direction == "down":
        increase_angle(cam_y)

# vals are 0-100
def move_laser(x, y):
    laser_x.angle = x
    laser_y.angle = y
    time.sleep(0.1)

def safe_close():
    print("Cleaning up...")
    reset_servos()
    print("Goodbye!")

app = Flask(__name__)
sock = Sock(app)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

def gen():
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        if ret == False:
            continue
        # encode the frame in JPEG format
        encodedImage = cv2.imencode(".jpg", frame)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + bytearray(np.array(encodedImage)) + b'\r\n')

@app.route('/')
def index():
    return 'Hello There!!!'

@app.route('/video_test')
def video_test():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundry=frame')

# laser: on, off
# cam: left, right, up, down
# move: x:100 y:10
@sock.route('/controls')
def controls(ws):
    while True:
        command = ws.receive()
        print(command)
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
            move_laser(int(x_val), int(y_val))

if __name__ == '__main__':
    try:
        socketio.run(app)
    
    except KeyboardInterrupt:
        safe_close()
    
    finally:
        safe_close()

def cleanup():
    try:
        safe_close()
    except Exception:
        pass

atexit.register(cleanup)