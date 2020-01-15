import math

from typeguard import typechecked


@typechecked
def code(radius: int = 15, num_sides: int = 6) -> str:
    """
    Example G-code module, an asterisk.

    Please simulate first, before milling.
    """
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
