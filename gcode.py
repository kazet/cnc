from pygcode import Line

import config

def interpret(input_text):
    for input_line in input_text.split('\n'):
        line = Line(input_line)
        for gcode in line.block.gcodes:
            config.MACHINE.feed(gcode)
