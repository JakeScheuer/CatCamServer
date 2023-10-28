from flask import Flask, Response, request
from flask_sock import Sock
from camera_pi import Camera
from adafruit_servokit import ServoKit
import time
import atexit

kit = ServoKit(channels=16)

laser_pin = kit.servo[4]
cam_x = kit.servo[2]
cam_y = kit.servo[3]
laser_x = kit.servo[0]
laser_y = kit.servo[1]

laser_pin.set_pulse_width_range(min_pulse=0, max_pulse=4096)
laser_pin.fraction(value=1.0)
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
        laser_pin.angle = 180
    else:
        laser_pin.angle = 0

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

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return 'Hello There!!!'

@app.route('/camera_feed')
def video_feed():
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundry=frame')

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