from pygcode import Line


def interpret(machine, input_text):
    for input_line in input_text.split('\n'):
        line = Line(input_line)
        for gcode in line.block.gcodes:
            machine.feed(gcode)
