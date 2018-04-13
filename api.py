import sys

from flask import (
    Flask,

    jsonify,
    render_template,
    request,
    send_from_directory,
)

import gcode
import config
import machine_process

app = Flask(__name__, static_url_path='')


@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)


@app.route("/gcode/", methods=["POST"])
def gcode_command():
    input_text = request.json['gcode']
    machine_process.send_message_gcode(input_text)
    return 'OK'


@app.route("/initialize/", methods=["POST"])
def initialize_command():
    machine_process.send_message_initialize()
    return 'OK'


@app.route("/abort/", methods=["POST"])
def abort_command():
    machine_process.kill()
    return 'OK'


@app.route("/get_logs/", methods=["POST"])
def get_logs():
    return machine_process.get_logs()


@app.route("/")
def index():
    return render_template('index.html')
