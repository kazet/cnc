import os
import traceback

from flask import (
    Flask,

    jsonify,
    render_template,
    request,
    send_from_directory,
)
from typeguard import typechecked

import gcode_interpreter
import machine.simulated_machine
import machine_process
import moves_to_svg

from utils import python_to_gcode

app = Flask(__name__, static_url_path='')
machine_worker_process = machine_process.WorkerProcess.create_and_start()


@app.route("/")
def endpoint_index():
    """
    Serves the index page.
    """
    def load(name):
        with open(os.path.join(os.path.dirname(__file__), 'pygcode_modules', name)) as f:
            return f.read()

    return render_template('index.html', modules=[
        (name, load(name))
        for name in sorted(os.listdir(os.path.join(os.path.dirname(__file__), 'pygcode_modules')))
        if name != '.' and name != '..' and name != '__init__.py' and name != '__pycache__'
    ])


@app.route('/static/<path:path>')
@typechecked
def endpoint_serve_static_files(path: str):
    """
    Serves a static file.
    """
    return send_from_directory('static', path)


@app.route("/api/pygcode/", methods=["POST"])
def endpoint_api_run_pygcode_command():
    """
    Serves an API endpoint, running G-code.
    """
    input_text = request.json['pygcode']

    try:
        machine_worker_process.send_message_gcode(python_to_gcode.python_to_gcode(input_text))
        return jsonify({
            'status': "OK",
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': "ERROR", 'message': repr(e)})


@app.route("/api/simulate/json/", methods=["POST"])
def endpoint_api_simulate_moves_json():
    """
    Serves an API endpoint, simulating G-code moves to JSON.
    """
    input_text = request.json['pygcode']

    try:
        simulated_machine = machine.simulated_machine.SimulatedMachine()
        interpreter = gcode_interpreter.GCodeInterpreter(simulated_machine)
        interpreter.run_gcode_string(python_to_gcode.python_to_gcode(input_text))
        moves = simulated_machine.simulated_moves

        return jsonify({
            'status': "OK",
            'moves': moves,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': "ERROR", 'message': repr(e)})


@app.route("/api/simulate/svg/", methods=["POST"])
def endpoint_api_simulate_moves_svg():
    """
    Serves an API endpoint, simulating G-code moves to SVG.
    """
    input_text = request.json['pygcode']

    try:
        simulated_machine = machine.simulated_machine.SimulatedMachine()
        interpreter = gcode_interpreter.GCodeInterpreter(simulated_machine)
        interpreter.run_gcode_string(python_to_gcode.python_to_gcode(input_text))
        moves = simulated_machine.simulated_moves

        return jsonify({
            'status': "OK",
            'result': moves_to_svg.moves_to_svg(
                moves,
                float(request.json['tool_diameter'])
            )
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': "ERROR", 'message': repr(e)})


@app.route("/api/initialize/", methods=["POST"])
def endpoint_api_initialize():
    """
    Serves an API endpoint, initializing the CNC machine.
    """
    machine_worker_process.send_message_initialize()
    return jsonify({'status': "OK"})


@app.route("/api/abort/", methods=["POST"])
def endpoint_api_abort():
    """
    Serves an API endpoint, non-gracefully emergency aborting what is being done now.
    """
    machine_worker_process.kill()
    return jsonify({'status': "OK"})


@app.route("/api/get_logs/", methods=["POST"])
def endpoint_api_get_logs():
    """
    Serves an API endpoint, reading the machine logs.
    """
    return jsonify({
        'status': "OK",
        'logs': machine_worker_process.get_logs()
    })
