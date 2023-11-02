import random
import threading
import time
import queue

class MessageSender():
    def __init__(self, mean_wait_time, failure_rate, message_queue):
        self.message_queue = message_queue
        self.mean_wait_time = mean_wait_time
        self.failure_rate = failure_rate
        self.sent_count = 0
        self.failed_count = 0
        self.alive = True

    def run(self, shutdown_event=threading.Event(), resend_failed_msg=False, max_resend_attempts=3):
        while not self.message_queue.empty():
            if shutdown_event.is_set():
                break
            try: # message could be taken by another thread
                message = self.message_queue.get(self.mean_wait_time)
                # Send the message and update the counters
                if self.send_message(message):
                    self.sent_count += 1
                    if resend_failed_msg and message['retry_count'] > 0:
                        self.failed_count -= 1 # Reduce the failed count if the message was resent successfully
                else:
                    if message['retry_count'] == 0:
                        self.failed_count += 1
                    # Check the retry count before putting it back in the queue
                    if resend_failed_msg and message['retry_count'] < max_resend_attempts:
                        message['retry_count'] += 1
                        self.message_queue.put(message)  # Put the message back in the queue for retry

            except queue.Empty:
                continue

        self.alive = False

    @property
    def is_alive(self):
        return self.alive   

    def random_wait(self):
        return random.expovariate(1/self.mean_wait_time)

    def send_message(self, message):
        # Sleep for a random time distributed around the mean wait time
        time.sleep(self.random_wait())
        # Simulate message sending with a success based on failure rate
        return random.random() >= self.failure_rate
