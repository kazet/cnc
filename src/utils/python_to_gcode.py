import os
import sys
from io import StringIO
import contextlib


# We want the following utilities to be visible to the executed code
# so that it is able to call them
from utils.translate_and_scale import translate_and_scale  # noqa


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


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
    with stdoutIO() as s:
        exec(code)
        return s.getvalue()
