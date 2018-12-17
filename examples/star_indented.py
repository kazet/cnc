import math
    
def code(radius=15, num_sides=10):
    result = ["G90"]

    num_sides = num_sides * 2

    for i in range(num_sides):
        if i % 2 == 0:
            radius2 = radius
        else:
            radius2 = radius / 2

        x = radius - radius2 * math.cos(2 * math.pi * i / num_sides)
        y = radius2 * math.sin(2 * math.pi * i / num_sides)
        result.append("G0 X%0.2f Y%0.2f" % (
            x,
            y
        ))

    result.append("G0 X0 Y0")
    return '\n'.join(result)
