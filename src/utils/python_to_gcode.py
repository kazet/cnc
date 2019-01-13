import os

# We want the following utilities to be visible to the executed code
# so that it is able to call them
from utils.translate_and_scale import translate_and_scale  # noqa


def load_example(name):
    path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'templates',
        'examples',
        name
    )
    with open(path) as f:
        code = f.read()
        return python_to_gcode(code)


def python_to_gcode(code):
    def emit(s):
        emit.result_gcode += s
    emit.result_gcode = ''

    exec(code)
    return emit.result_gcode
