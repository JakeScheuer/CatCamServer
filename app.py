from flask import Flask, Response, request
from flask_sock import Sock
from camera_pi import Camera
from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

laser = kit.servo[4]
cam_x = kit.servo[2]
cam_y = kit.servo[3]
laser_x = kit.servo[0]
laser_y = kit.servo[1]

def reset_servos():
    # cam_x.angle = 90
    # time.sleep(0.2)
    # cam_y.angle = 90
    # time.sleep(0.2)
    laser_x.angle = 90
    time.sleep(0.2)
    laser_y.angle = 90
    time.sleep(0.2)

def toggle_laser(turnOn):
    # Just to test...
    reset_servos()
    # laser.on() if turnOn else laser.off()

def move_left(servo):
    if servo.angle > 0: 
        servo.angle -= 10

def move_right(servo):
    if servo.angle < 180: 
        servo.angle += 10

def move_camera(direction):
    if direction == "left":
        move_left(laser_x)
    elif direction == "right":
        move_right(laser_x)
    elif direction == "up":
        move_left(laser_y)
    elif direction == "down":
        move_right(laser_y)

# def cord_to_pos(val):
#     # 0 -> -1
#     # 25 -> -0.5
#     # 50 -> 0
#     # 75 -> 0.5 
#     # 100 -> 1
#     return round(((val * 2)/100) - 1)

# vals are 0-100
def move_laser(x, y):
    print(x)
    print(y)
    # laser_x.value = cord_to_pos(x)
    # laser_y.value = cord_to_pos(y)
    # time.sleep(0.1)

def safe_close():
    print("Cleaning up...")
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
            move_laser(float(x_val), float(y_val))

if __name__ == '__main__':
    try:
        socketio.run(app)
    
    except KeyboardInterrupt:
        safe_close()
    
    finally:
        safe_close()