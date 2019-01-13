# An experimental milling machine driver with a web interface
Disclaimer: this tool may not be stable. If you want to get actual stuff done,
you may prefer to use different, production-ready milling machine software.

## How to connect
This tool uses Raspberry PI GPIO pins to interface with stepper motor drivers.
The GPIO pin numbers for `DIR` and `PUL` stepper motor driver inputs for each
axis are described in `config.py`.

## How to run
To run the web interface, execute the following commands:

```bash
virtualenv -p /usr/bin/python3 venv
. venv/bin/activate
pip install -r requirements
./launch.sh
```

The interface will listen on http://0.0.0.0:5000/.

## How to check code quality (via flake8)
To check the code quality, execute the following commands:

```bash
. venv/bin/activate
flake8 .
```

## How to run the tests
To run the tests, execute the following commands:

```bash
. venv/bin/activate
PYTHONPATH=.:src python -m unittest discover
```
