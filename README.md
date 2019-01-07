# A toy milling machine driver with a web interface

## How to run

```bash
virtualenv -p /usr/bin/python3 venv
. venv/bin/activate
pip install -r requirements
./launch.sh
```

## How to check code quality (via flake8)

```bash
. venv/bin/activate
flake8 .
```

## How to run the unit tests

```bash
. venv/bin/activate
PYTHONPATH=.:src python -m unittest discover
```
