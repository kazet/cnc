"""
The milling machine front-end actually doesn't execute G-code, but Python,
that emits G-code with emit() calls.
"""

import os

from typeguard import typechecked

# We want the following utilities to be visible to the executed code
# so that it is able to call them
from utils.translate_and_scale import translate_and_scale  # noqa


@typechecked
def load_example(name: str) -> str:
    """
    Load one example file with given name and return its G-code.
    """
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


@typechecked
def python_to_gcode(code: str) -> str:
    """
    Execute Python and collect the G-code that has been emitted.
    """
    def emit(s):
        emit.result_gcode += s
    emit.result_gcode = ''

    exec(code)
    return emit.result_gcode
