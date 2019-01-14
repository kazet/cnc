import os
import traceback

from flask import (
    Flask,

    jsonify,
    render_template,
    request,
    send_from_directory,
)

import gcode_interpreter
import machine.simulated_machine
import machine_process
import moves_to_svg

from utils import python_to_gcode

app = Flask(__name__, static_url_path='')


@app.route('/static/<path:path>')
def endpoint_serve_static_files(path):
    return send_from_directory('static', path)


@app.route("/gcode/", methods=["POST"])
def endpoint_run_gcode_command():
    input_text = request.json['gcode']
    machine_process.send_message_gcode(python_to_gcode.python_to_gcode(input_text))
    return 'OK'


@app.route("/simulate/", methods=["POST"])
def endpoint_simulate_moves_json():
    input_text = request.json['gcode']

    try:
        simulated_machine = machine.simulated_machine.SimulatedMachine()
        interpreter = gcode_interpreter.GCodeInterpreter(simulated_machine)
        interpreter.run_gcode_string(python_to_gcode.python_to_gcode(input_text))
        moves = simulated_machine.simulated_moves

        return jsonify(moves)
    except Exception as e:
        traceback.print_exc()
        return repr(e), 400


@app.route("/simulate_svg/", methods=["POST"])
def endpoint_simulate_moves_svg():
    input_text = request.json['gcode']

    try:
        simulated_machine = machine.simulated_machine.SimulatedMachine()
        interpreter = gcode_interpreter.GCodeInterpreter(simulated_machine)
        interpreter.run_gcode_string(python_to_gcode.python_to_gcode(input_text))
        moves = simulated_machine.simulated_moves

        return moves_to_svg.moves_to_svg(
            moves,
            float(request.json['tool_diameter'])
        )
    except Exception as e:
        traceback.print_exc()
        return repr(e), 400


@app.route("/initialize/", methods=["POST"])
def endpoint_initialize():
    machine_process.send_message_initialize()
    return 'OK'


@app.route("/abort/", methods=["POST"])
def endpoint_abort():
    machine_process.kill()
    return 'OK'


@app.route("/get_logs/", methods=["POST"])
def endpoint_get_logs():
    return jsonify(machine_process.get_logs())


@app.route("/")
def endpoint_index():
    def load(name):
        with open(os.path.join(os.path.dirname(__file__), 'gcode_modules', name)) as f:
            return f.read()

    return render_template('index.html', modules=[
        (name, load(name))
        for name in sorted(os.listdir(os.path.join(os.path.dirname(__file__), 'gcode_modules')))
        if name != '.' and name != '..' and name != '__init__.py' and name != '__pycache__'
    ])
