from driver import (
    mill_pin_driver,
    motor_driver,
)

import machine

MILL_PIN_DRIVER = mill_pin_driver.RaspberryPiMillPinDriver()

LOCK_PATH = '/tmp/cnc.lock'

MM_PER_REVOLUTION = 3
STEPS_PER_REVOLUTION = 200.0 * 32.0

MACHINE = machine.Machine(
    x_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'X'),
        backlash=0.5,
        mm_per_revolution=MM_PER_REVOLUTION,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=0.000003,
    ),
    y_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'Y'),
        backlash=0.25,
        mm_per_revolution=MM_PER_REVOLUTION,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=0.000003,
    ),
)

def create_simulation_machine():
    return machine.Machine(
        x_axis=machine.SimulatedMachineAxis(
            mm_per_revolution=MM_PER_REVOLUTION,
            steps_per_revolution=STEPS_PER_REVOLUTION,
        ),
        y_axis=machine.SimulatedMachineAxis(
            mm_per_revolution=MM_PER_REVOLUTION,
            steps_per_revolution=STEPS_PER_REVOLUTION,
        ),
        simulated=True,
    )
