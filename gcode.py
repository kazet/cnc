from pygcode import Line


def interpret(machine, input_text):
    for input_line in input_text.split('\n'):
        if input_line.startswith('#'):
            continue

        line = Line(input_line)
        for gcode in line.block.gcodes:
            machine.feed(gcode)
