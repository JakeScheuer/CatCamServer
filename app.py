from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/camera_feed")
def get_feed():
    return "feed data"

@app.route("/camera_controls")
def control_camera():
    return "camera controls"

@app.route("/laser_controls")
def control_laser():
    return "laser controls"