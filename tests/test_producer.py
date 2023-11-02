import unittest
import threading
import string
from unittest.mock import patch, MagicMock
from src import MessageProducer 
from queue import Queue

class TestMessageProducer(unittest.TestCase):

    def setUp(self):
        self.message_count = 10
        self.message_queue = Queue()
        self.message_producer = MessageProducer(
            message_queue=self.message_queue,
            message_count=self.message_count
        )

    def test_generate_text(self):
        text = self.message_producer.generate_text()
        self.assertEqual(len(text), 100)
        self.assertTrue(all(c in string.ascii_letters + string.digits for c in text))

    def test_generate_phone_number(self):
        phone_number = self.message_producer.generate_phone_number()
        self.assertEqual(len(phone_number), 10)
        self.assertTrue(all(c in string.digits for c in phone_number))

    def test_produce(self):
        shutdown_event = threading.Event()
        self.message_producer.produce(shutdown_event)
        self.assertEqual(self.message_queue.qsize(), self.message_count)
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self.assertIn('text', message)
            self.assertIn('phone_number', message)
            self.assertIn('retry_count', message)

    def test_produce_with_shutdown(self):
        shutdown_event = threading.Event()
        message_producer = MessageProducer(self.message_queue, message_count=10)

        with patch.object(shutdown_event, 'is_set', side_effect=[False] * (message_producer.message_count // 2) + [True] * (message_producer.message_count // 2)):
            message_producer.produce(shutdown_event)
            self.assertEqual(self.message_queue.qsize(), message_producer.message_count // 2)

if __name__ == '__main__':
    unittest.main()
