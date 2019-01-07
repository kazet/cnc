import math


def code(radius=15, num_sides=6):
    result = ["G90"]

    for i in range(num_sides):
        x = radius * math.cos(2 * math.pi * (i + 0.5) / num_sides)
        y = radius * math.sin(2 * math.pi * (i + 0.5) / num_sides)
        result.append("G0 X%0.2f Y%0.2f" % (
            x,
            y
        ))
        result.append("G0 X0 Y0")
    return '\n'.join(result)
