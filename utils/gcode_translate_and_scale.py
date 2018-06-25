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
        elif isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW) or isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW) or isinstance(gcode, pygcode.gcodes.GCodeRapidMove):
            if self._mode == MachineMode.ABSOLUTE:
                gcode.params['X'].value += x
                gcode.params['Y'].value += y

                if 'Z' in gcode.params:
                    gcode.params['Z'].value += z
            elif self._mode == MachineMode.INCREMENTAL:
                pass
            else:
                assert(False)

            gcode.params['X'].value *= scale
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

def main():
    parser = argparse.ArgumentParser(
        description='Perform G-Code xyz translation')
    parser.add_argument('--input-file', dest='input_file', help='The input file name', required=True)
    parser.add_argument('--output-file', dest='output_file', help='The output file name', required=True)
    parser.add_argument('--x', type=float, help='X amout to be translated', default=0)
    parser.add_argument('--y', type=float, help='Y amout to be translated', default=0)
    parser.add_argument('--z', type=float, help='Z amout to be translated', default=0)
    parser.add_argument('--scale', type=float, help='scale', default=1)
    args = parser.parse_args()

    translator_and_scaler = TranslatorAndScaler()

    with open(args.input_file, 'r') as input_f:
        with open(args.output_file, 'w') as output_f:
            for input_line in input_f:
                if input_line.startswith('#'):
                    continue

                line = pygcode.Line(input_line)
                for gcode in line.block.gcodes:
                    output_gcode = translator_and_scaler.convert(
                        gcode,
                        args.x,
                        args.y,
                        args.z,
                        args.scale,
                    )
                    output_f.write(str(output_gcode) + '\n')

if __name__ == '__main__':
    main()
