from flask import Flask
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

@sock.route('/camera_feed')
def feed(ws):
    while True:
        ws.send("video stream")

@sock.route('/camera_controls')
def camera_controls(ws):
    while True:
        command = ws.receive()
        ws.send(f'Camera move {command}')

@sock.route('/laser_controls')
def laser_command(ws):
    while True:
        command = ws.receive()
        ws.send(f'Laser move {command}')

if __name__ == '__main__':
    socketio.run(app)