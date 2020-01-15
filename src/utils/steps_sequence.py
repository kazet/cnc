import typing

from typeguard import typechecked

from utils.typing import Numeric


@typechecked
def create_steps_sequence(num_steps: Numeric, axis: str) -> typing.List[typing.Tuple[float, str]]:
    """
    Returns a list of num_steps tuples: [float, str], with given string parameter, and
    the floating-point parameter increasing lineairly from 0 to 1.

    Example:

    >>> create_steps_sequence(5, 'X')
    [(0.0, 'X'), (0.2, 'X'), (0.4, 'X'), (0.6, 'X'), (0.8, 'X')]
    """
    if isinstance(num_steps, float):
        num_steps = int(num_steps)

    if num_steps == 0:
        return []

    sequence = []
    for step in range(num_steps):
        sequence.append((step * 1.0 / num_steps, axis))
    return sequence


@typechecked
def create_xyz_steps_sequence(
        num_x_steps: int,
        num_y_steps: int,
        num_z_steps: int) -> typing.List[typing.Tuple[float, str]]:
    """
    Let's assume, you want to execute num_x_steps stepper motor steps on X axis, num_y_steps on Y axis, num_z_steps
    on Z axis in one time period (e.g. one second).

    This function returns a list of tuples what paricular step on what axis in what time period should be executed.

    Example:

    >>> create_xyz_steps_sequence(num_x_steps=5, num_y_steps=2, num_z_steps=0)
    [(0.0, 'X'), (0.0, 'Y'), (0.2, 'X'), (0.4, 'X'), (0.5, 'Y'), (0.6, 'X'), (0.8, 'X')]
    """
    sequence_x = create_steps_sequence(num_x_steps, 'X')
    sequence_y = create_steps_sequence(num_y_steps, 'Y')
    sequence_z = create_steps_sequence(num_z_steps, 'Z')

    return sorted(
        sequence_x +
        sequence_y +
        sequence_z
    )
