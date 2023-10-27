from flask import Flask, Response, request
from flask_sock import Sock
from camera_pi import Camera
from gpiozero import LED, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

min_p = 0.05/1000
max_p = 2.5/1000
factory = PiGPIOFactory()
laser = LED(2)
cam_x = Servo("BOARD35",min_pulse_width=min_p, max_pulse_width=max_p, pin_factory=factory)
cam_y = Servo("BOARD33",min_pulse_width=min_p, max_pulse_width=max_p, pin_factory=factory)
# laser_x = Servo(1, min_pulse_width=min_p, max_pulse_width=max_p, pin_factory=factory)
# laser_y = Servo(26, min_pulse_width=min_p, max_pulse_width=max_p, pin_factory=factory)

def toggle_laser(turnOn):
    # Just to test...
    cam_x.min()
    time.sleep(2)
    cam_x.mid()
    time.sleep(2)
    cam_x.max()
    time.sleep(2)
    cam_x.mid()
    time.sleep(2)

    cam_y.min()
    time.sleep(2)
    cam_y.mid()
    time.sleep(2)
    cam_y.max()
    time.sleep(2)
    cam_y.mid()
    # laser.on() if turnOn else laser.off()

def move_left(servo):
    print(servo.value)
    if servo.value > -0.7: 
        servo.value -= 0.2 #0.01

def move_right(servo):
    print(servo.value)
    if servo.value < 0.7: 
        servo.value += 0.2 #0.01

# This may not be right...
# def move_for_period(move_function):
#     for x in range(20):
#         move_function()

def move_camera(direction):
    if direction == "left":
        move_left(cam_x)
    elif direction == "right":
        move_right(cam_x)
    elif direction == "up":
        move_left(cam_y)
    elif direction == "down":
        move_right(cam_y)

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
    cam_x.mid()
    cam_y.mid()
    # laser_x.mid()
    # laser_y.mid()
    sleep(1)
    cam_x.close()
    cam_y.close()
    laser_x.close()
    laser_y.close()
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