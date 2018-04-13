from driver import (
    mill_pin_driver,
    motor_driver,
)

import machine

MILL_PIN_DRIVER = mill_pin_driver.RaspberryPiMillPinDriver()

LOCK_PATH = '/tmp/cnc.lock'

MACHINE = machine.Machine(
    x_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'X'),
        backlash=0.5,
        mm_per_revolution=3,
        steps_per_revolution=200.0 * 32.0,
        step_time=0.000003,
    ),
    y_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'Y'),
        backlash=0.25,
        mm_per_revolution=3,
        steps_per_revolution=200.0 * 32.0,
        step_time=0.000003,
    ),
)
