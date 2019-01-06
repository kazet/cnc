from driver import motor_driver

try:
    __import__('RPi._GPIO')
except RuntimeError:  # no Raspberry PI GPIO modules
    # Use a dummy driver, that will fail when trying to issue actual commands
    from driver.mill_pin_driver.dummy import DummyMillPinDriver
    MILL_PIN_DRIVER = DummyMillPinDriver()
else:  # we succesfully imported Raspberry PI GPIO modules
    # Use Raspberry PI GPIO driver if we're on a Raspberry PI
    from driver.mill_pin_driver.raspberry_pi import RaspberryPiMillPinDriver
    MILL_PIN_DRIVER = RaspberryPiMillPinDriver()

import machine


LOCK_PATH = '/tmp/cnc.lock'

MM_PER_REVOLUTION = 3
STEPS_PER_REVOLUTION = 200.0 * 32.0
STEP_TIME = 0.000008

MACHINE = machine.Machine(
    x_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'X', is_inverse=False),
        backlash=0.2,
        mm_per_revolution=MM_PER_REVOLUTION,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=STEP_TIME,
    ),
    y_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'Y', is_inverse=True),
        backlash=0.2,
        mm_per_revolution=MM_PER_REVOLUTION,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=STEP_TIME,
    ),
    z_axis=machine.MachineAxis(
        motor=motor_driver.MotorDriver(MILL_PIN_DRIVER, 'Z', is_inverse=True),
        backlash=0,
        mm_per_revolution=4,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=STEP_TIME,
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
        z_axis=machine.SimulatedMachineAxis(
            mm_per_revolution=4,
            steps_per_revolution=STEPS_PER_REVOLUTION,
        ),
        simulated=True,
    )
