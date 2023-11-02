import unittest
import threading
from unittest.mock import patch, MagicMock
from src import MessageSender 
from queue import Queue, Empty

class TestMessageSender(unittest.TestCase):

    def setUp(self):
        self.message_queue = Queue()
        self.mean_wait_time = 1
        self.failure_rate = 0.5
        self.message_sender = MessageSender(
            mean_wait_time=self.mean_wait_time,
            failure_rate=self.failure_rate,
            message_queue=self.message_queue
        )

    def test_send_message_success(self):
        # Assume send_message always succeeds
        with patch.object(self.message_sender, 'send_message', return_value=True):
            message = {'text': 'test', 'phone_number': '1234567890', 'retry_count': 0}
            self.message_queue.put(message)
            shutdown_event = threading.Event()
            self.message_sender.run(shutdown_event)
            self.assertEqual(self.message_sender.sent_count, 1)
            self.assertEqual(self.message_sender.failed_count, 0)

    def test_send_message_failure_and_retry_success(self):
        # First call to send_message fails, second succeeds
        with patch.object(self.message_sender, 'send_message', side_effect=[False, True]):
            message = {'text': 'test', 'phone_number': '1234567890', 'retry_count': 0}
            self.message_queue.put(message)
            shutdown_event = threading.Event()
            self.message_sender.run(shutdown_event, resend_failed_msg=True, max_resend_attempts=3)
            self.assertEqual(self.message_sender.sent_count, 1)
            self.assertEqual(self.message_sender.failed_count, 0)

    def test_send_message_failure_and_retry_exceeded(self):
        # send_message always fails
        with patch.object(self.message_sender, 'send_message', return_value=False):
            message = {'text': 'test', 'phone_number': '1234567890', 'retry_count': 0}
            self.message_queue.put(message)
            shutdown_event = threading.Event()
            self.message_sender.run(shutdown_event, resend_failed_msg=True, max_resend_attempts=1)
            self.assertEqual(self.message_sender.sent_count, 0)
            self.assertEqual(self.message_sender.failed_count, 1)

    def test_send_message_failure_no_retry(self):
        # send_message fails without retry
        with patch.object(self.message_sender, 'send_message', return_value=False):
            message = {'text': 'test', 'phone_number': '1234567890', 'retry_count': 0}
            self.message_queue.put(message)
            shutdown_event = threading.Event()
            self.message_sender.run(shutdown_event, resend_failed_msg=False)
            self.assertEqual(self.message_sender.sent_count, 0)
            self.assertEqual(self.message_sender.failed_count, 1)

    def test_random_wait(self):
        # Test if random wait is within expected range
        with patch('random.expovariate', return_value=self.mean_wait_time):
            wait_time = self.message_sender.random_wait()
            self.assertEqual(wait_time, self.mean_wait_time)

    def test_shutdown_event_stops_processing(self):
        # send_message success but should not be called if shutdown_event is set
        with patch.object(self.message_sender, 'send_message') as mock_send_message:
            message = {'text': 'test', 'phone_number': '1234567890', 'retry_count': 0}
            self.message_queue.put(message)
            shutdown_event = threading.Event()
            shutdown_event.set()  # Simulate shutdown
            self.message_sender.run(shutdown_event)
            mock_send_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()
