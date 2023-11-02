import unittest
from unittest.mock import patch, MagicMock
from src import ProgressMonitor 
import threading
import time

class TestProgressMonitor(unittest.TestCase):

    def setUp(self):
        self.update_interval = 1
        self.monitor = ProgressMonitor(update_interval=self.update_interval)
        self.shutdown_event = threading.Event()

    def mock_sender(self, sent, failed, alive):
        sender = MagicMock()
        sender.sent_count = sent
        sender.failed_count = failed
        sender.is_alive = MagicMock(return_value=alive)
        return sender

    def test_start(self):
        self.monitor.start()
        self.assertIsNotNone(self.monitor.start_time)

    def test_update(self):
        sent_before = self.monitor.total_sent
        failed_before = self.monitor.total_failed

        self.monitor.update(10, 2)
        
        self.assertEqual(self.monitor.total_sent, sent_before + 10)
        self.assertEqual(self.monitor.total_failed, failed_before + 2)

    def test_print_report(self):
        with patch('builtins.print') as mock_print:
            self.monitor.start_time = time.time()
            self.monitor.total_sent = 100
            self.monitor.total_failed = 20
            self.monitor.print_report()
            mock_print.assert_called()

    @patch('time.sleep', return_value=None)  # This will replace time.sleep with a mock that does nothing
    def test_monitor(self, mock_sleep):
        self.monitor.start()
        senders = [self.mock_sender(50, 10, False), self.mock_sender(50, 10, False)]
        
        with patch.object(self.monitor, 'print_report') as mock_print_report, patch('builtins.print') as mock_print:
                self.shutdown_event.set()  
                # We will manually call the monitor method for testing
                self.monitor.monitor(None, senders, self.shutdown_event)
                mock_print_report.assert_called()

    def test_monitor_with_shutdown(self):
        self.monitor.start()
        senders = [self.mock_sender(50, 10, True)]
        self.shutdown_event.set()  # Simulate shutdown
        
        with patch.object(self.monitor, 'print_report') as mock_print_report, patch('builtins.print') as mock_print:
                self.monitor.monitor(None, senders, self.shutdown_event)
                mock_print_report.assert_called_once()

if __name__ == '__main__':
    unittest.main()
