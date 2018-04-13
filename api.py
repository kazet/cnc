from flask import (
    Flask,

    jsonify,
    render_template,
    request,
    send_from_directory,
)

import gcode
import config

app = Flask(__name__, static_url_path='')


@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)


@app.route("/gcode/", methods=["POST"])
def gcode_command():
    input_text = request.json['gcode']

    try:
        gcode.interpret(input_text)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': e.message
        })

    return jsonify({
        'success': True,
        'message': 'OK'
    })


@app.route("/initialize/", methods=["POST"])
def initialize_command():
    config.MACHINE.initialize()
    return jsonify({
        'success': True,
        'message': 'OK'
    })


@app.route("/")
def index():
    return render_template('index.html')
