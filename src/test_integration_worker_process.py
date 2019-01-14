import multiprocessing
import time

from unittest import mock, TestCase

import config
from machine_process import WorkerProcess

class WorkerProcessIntegrationTestCase(TestCase):
    def test_succesful_initialization(self):
        try:
            with mock.patch('config.MACHINE') as MockMachine:
                is_initialized = multiprocessing.Value('b', False)

                def mock_initialize_method():
                    is_initialized.value = True

                MockMachine.initialize.side_effect = mock_initialize_method

                worker_process = WorkerProcess.create_and_start()
                worker_process.send_message_initialize()

                time.sleep(0.1)
                self.assertTrue(is_initialized.value)
                self.assertEqual(
                    worker_process.get_logs(),
                    [{'level': 'INFO', 'message': 'Machine initialized successfully'}],
                )
        finally:
            worker_process.kill()
        
    def test_failed_initialization(self):
        try:
            with mock.patch('config.MACHINE') as MockMachine:
                MockMachine.initialize.side_effect = Exception("Failed to initialize machine")

                worker_process = WorkerProcess.create_and_start()
                worker_process.send_message_initialize()
                time.sleep(0.1)
                self.assertEqual(
                    worker_process.get_logs(),
                    [{'level': 'ERROR', 'message': 'Failed to initialize machine'}],
                )
        finally:
            worker_process.kill()

    def test_succesful_gcode_sending(self):
        try:
            with mock.patch('config.MACHINE') as MockMachine:
                received_move_coordinates = multiprocessing.Array('c', range(100))

                def mock_move_by_method(x, y, z, feed_rate):
                    received_move_coordinates.value = b'x=%f y=%f z=%f feed_rate=%f' % (
                        x,
                        y,
                        z,
                        feed_rate,
                    )

                type(MockMachine).rapid_move_feed_rate = mock.PropertyMock(return_value=1000)
                MockMachine.move_by.side_effect = mock_move_by_method

                worker_process = WorkerProcess.create_and_start()
                worker_process.send_message_initialize()
                worker_process.send_message_gcode("G0 X3 Y2 Z1")
                time.sleep(0.1)
                self.assertEqual(received_move_coordinates.value, b'x=3.000000 y=2.000000 z=1.000000 feed_rate=1000.000000')

                logs = worker_process.get_logs()
                self.assertEqual(len(logs), 2)
                self.assertEqual(logs[0]['level'], 'INFO')
                self.assertEqual(logs[0]['message'], 'Machine initialized successfully')
                self.assertEqual(logs[1]['level'], 'INFO')
                self.assertTrue(logs[1]['message'].startswith("gcode interpreted successfully, took"))
        finally:
            worker_process.kill()
        
    def test_failed_gcode_sending(self):
        try:
            with mock.patch('config.MACHINE') as MockMachine:
                worker_process = WorkerProcess.create_and_start()
                worker_process.send_message_initialize()
                worker_process.send_message_gcode("Invalid")
                time.sleep(0.1)
                self.assertEqual(
                    worker_process.get_logs(),
                    [
                        {'level': 'INFO', 'message': 'Machine initialized successfully'},
                        {'level': 'ERROR', 'message': "word 'I' value invalid"},
                    ]
                )
        finally:
            worker_process.kill()
