import multiprocessing
import queue
import time
import traceback

import config
import gcode_interpreter


class WorkerProcessMessage():
    INITIALIZE = 'INITIALIZE'
    GCODE = 'GCODE'


class WorkerProcessLogItemLevel():
    INFO = 'INFO'
    ERROR = 'ERROR'


def worker_process(command_queue, log_queue):
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


def spawn_worker_process():
    command_queue = multiprocessing.Queue()
    log_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=worker_process, args=(command_queue, log_queue))
    process.start()

    return process, command_queue, log_queue


def send_message_initialize():
    WORKER_COMMAND_QUEUE.put((WorkerProcessMessage.INITIALIZE, ''))


def send_message_gcode(gcode):
    WORKER_COMMAND_QUEUE.put((WorkerProcessMessage.GCODE, gcode))


def kill():
    WORKER_PROCESS.terminate()


def get_logs():
    result = []
    try:
        while True:
            result.append(WORKER_LOG_QUEUE.get_nowait())
    except queue.Empty:
        pass

    return result


WORKER_PROCESS, WORKER_COMMAND_QUEUE, WORKER_LOG_QUEUE = spawn_worker_process()
