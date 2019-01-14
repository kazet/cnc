import multiprocessing
import queue
import time
import traceback

import config
import gcode_interpreter


class WorkerProcessAlreadyStartedException(Exception):
    pass


class WorkerProcessLogItemLevel():
    INFO = 'INFO'
    ERROR = 'ERROR'


class WorkerProcessMessage():
    INITIALIZE = 'INITIALIZE'
    GCODE = 'GCODE'


class WorkerProcess():
    def __init__(self):
        self._started = False

    @staticmethod
    def create_and_start():
        worker_process = WorkerProcess()
        worker_process.start()
        return worker_process

    def start(self):
        if self._started:
            raise WorkerProcessAlreadyStartedException("This particular worker process has already benn started")
        else:
            self._command_queue = multiprocessing.Queue()
            self._log_queue = multiprocessing.Queue()
            self._process = multiprocessing.Process(
                target=WorkerProcess._run,
                args=(self._command_queue, self._log_queue),
            )
            self._process.start()

    def send_message_initialize(self):
        self._command_queue.put((WorkerProcessMessage.INITIALIZE, ''))

    def send_message_gcode(self, gcode):
        self._command_queue.put((WorkerProcessMessage.GCODE, gcode))

    def kill(self):
        self._process.terminate()
        self._started = False

    def get_logs(self):
        result = []
        try:
            while True:
                result.append(self._log_queue.get_nowait())
        except queue.Empty:
            pass

        return result

    @staticmethod
    def _run(command_queue, log_queue):
        machine = config.MACHINE

        while True:
            message, data = command_queue.get()

            try:
                if message == WorkerProcessMessage.INITIALIZE:
                    machine.initialize()
                    log_queue.put({
                        'level': WorkerProcessLogItemLevel.INFO,
                        'message': "Machine initialized successfully"
                    })
                elif message == WorkerProcessMessage.GCODE:
                    start_time = time.time()

                    gcode_interpreter.GCodeInterpreter(machine).run_gcode_string(data)
                    gcode_execution_time = time.time() - start_time

                    log_queue.put({
                        'level': WorkerProcessLogItemLevel.INFO,
                        'message': "gcode interpreted successfully, took %.02f seconds" % gcode_execution_time,
                    })
                else:
                    assert(False)
            except Exception as e:
                traceback.print_exc()
                log_queue.put({
                    'level': WorkerProcessLogItemLevel.ERROR,
                    'message': "%s" % str(e),
                })
