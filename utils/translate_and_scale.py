import argparse

import pygcode

from machine import MachineMode

class TranslatorAndScaler():
    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._mode = MachineMode.ABSOLUTE

    def convert(self, gcode, x, y, z, scale):
        if isinstance(gcode, pygcode.gcodes.GCodeIncrementalDistanceMode):
            self._mode = MachineMode.INCREMENTAL
            return gcode
        elif isinstance(gcode, pygcode.gcodes.GCodeAbsoluteDistanceMode):
            self._mode = MachineMode.ABSOLUTE
            return gcode
        elif isinstance(gcode, pygcode.gcodes.GCodeSelectXYPlane):
            return gcode
        elif isinstance(gcode, pygcode.gcodes.GCodeFeedRate):
            return gcode
        elif isinstance(gcode, pygcode.gcodes.GCodeEndProgram):
            return gcode
        elif isinstance(gcode, pygcode.gcodes.GCodeUseMillimeters):
            return gcode
        elif (
                isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW) or
                isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW) or
                isinstance(gcode, pygcode.gcodes.GCodeRapidMove) or
                isinstance(gcode, pygcode.gcodes.GCodeLinearMove)):
            if self._mode == MachineMode.ABSOLUTE:
                if 'X' in gcode.params:
                    gcode.params['X'].value += x

                if 'Y' in gcode.params:
                    gcode.params['Y'].value += y

                if 'Z' in gcode.params:
                    gcode.params['Z'].value += z
            elif self._mode == MachineMode.INCREMENTAL:
                pass
            else:
                assert(False)

            if 'X' in gcode.params:
                gcode.params['X'].value *= scale

            if 'Y' in gcode.params:
                gcode.params['Y'].value *= scale

            if 'Z' in gcode.params:
                gcode.params['Z'].value *= scale

            if isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW) or isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW):
                assert 'I' in gcode.params
                assert 'J' in gcode.params
                assert 'R' not in gcode.params

                gcode.params['I'].value *= scale
                gcode.params['J'].value *= scale
            return gcode
        else:
            raise Exception("Unknown gcode: %s" % repr(gcode))


def translate_and_scale(content, x=0, y=0, z=0, scale=1):
    result = ''
    translator_and_scaler = TranslatorAndScaler()

    for input_line in content.split('\n'):
        if input_line.startswith('#'):
            continue

        line = pygcode.Line(input_line)
        for gcode in line.block.gcodes:
            output_gcode = translator_and_scaler.convert(
                gcode,
                x,
                y,
                z,
                scale,
            )
            result += str(output_gcode) + '\n'
    return result
