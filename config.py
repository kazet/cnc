try:
    __import__('RPi._GPIO')
except RuntimeError:  # no Raspberry PI GPIO modules
    # Use a dummy driver, that will fail when trying to issue actual commands
    from motor_driver.dummy import DummyMotorDriver
    MOTOR_DRIVER_CLASS = DummyMotorDriver
else:  # we succesfully imported Raspberry PI GPIO modules
    # Use Raspberry PI GPIO driver if we're on a Raspberry PI
    from motor_driver.raspberry_pi_gpio import RaspberryPiGPIOMotorDriver
    MOTOR_DRIVER_CLASS = RaspberryPiGPIOMotorDriver

import machine.stepper_motor_control_machine

LOCK_PATH = '/tmp/cnc.lock'

STEPS_PER_REVOLUTION = 200.0 * 32.0
STEP_TIME = 0.000008

MACHINE = machine.stepper_motor_control_machine.StepperMotorControlMachine(
    x_axis=machine.stepper_motor_control_machine.MachineAxis(
        motor=MOTOR_DRIVER_CLASS('X', is_inverse=False),
        backlash=0.2,
        mm_per_revolution=3,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=STEP_TIME,
    ),
    y_axis=machine.stepper_motor_control_machine.MachineAxis(
        motor=MOTOR_DRIVER_CLASS('Y', is_inverse=True),
        backlash=0.2,
        mm_per_revolution=3,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=STEP_TIME,
    ),
    z_axis=machine.stepper_motor_control_machine.MachineAxis(
        motor=MOTOR_DRIVER_CLASS('Z', is_inverse=True),
        backlash=0,
        mm_per_revolution=4,
        steps_per_revolution=STEPS_PER_REVOLUTION,
        step_time=STEP_TIME,
    ),
    default_feed_rate=500,
    rapid_move_feed_rate=5000,
)
