import math
import typing

from typeguard import typechecked

from utils.typing import Numeric


@typechecked
def euclidean_distance(
        point1: typing.Tuple[Numeric, Numeric, Numeric],
        point2: typing.Tuple[Numeric, Numeric, Numeric]) -> Numeric:
    """
    Returns the euclidean distance between two points.

    Args:
        point1: a 3-tuple of point coordinates
        point2: a 3-tuple of point coordinates
    """
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
