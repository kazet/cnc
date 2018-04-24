import time
import RPi.GPIO

class RaspberryPiMillPinDriver:
    MOTOR_PINS = {
        'X': {
            'DIR': 35,
            'PUL': 37,
        },
        'Y': {
            'DIR': 33,
            'PUL': 31,
        },
    }

    def __init__(self):
        self._configure_rpi()
        self._enable_pins_for_output()

    def _configure_rpi(self):
        RPi.GPIO.setmode(RPi.GPIO.BOARD)

    def _enable_pins_for_output(self):
        for motor_pin_dict in self.MOTOR_PINS.values():
            for output_pin_id in motor_pin_dict.values():
                RPi.GPIO.setup(output_pin_id, RPi.GPIO.OUT)

    def output(self, pin, value):
        RPi.GPIO.output(pin, value)
