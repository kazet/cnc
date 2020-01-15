from machine.arduino.machine import Arduino3AxisSerialMachine

STEPS_PER_REVOLUTION = 200.0 * 32.0

MACHINE = Arduino3AxisSerialMachine(
    # Because the X and Y axes screw pitch is 3mm, Z axis is 4mm on my machine.
    # Feel free to configure as you see fit.
    steps_per_mm_x=STEPS_PER_REVOLUTION / 3,
    steps_per_mm_y=STEPS_PER_REVOLUTION / 3,
    steps_per_mm_z=STEPS_PER_REVOLUTION / 4,
    invert_x=False,
    invert_y=False,
    invert_z=False,
    default_feed_rate=500,
    rapid_move_feed_rate=500,
)
