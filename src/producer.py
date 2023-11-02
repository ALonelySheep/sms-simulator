import random
import string
import threading

class MessageProducer:
    def __init__(self, message_queue, message_count=1000):
        self.message_count = message_count
        self.message_queue = message_queue

    def generate_text(self):
        # Generate a random string of up to 100 characters (letters and digits)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=100))
    
    def generate_phone_number(self):
        # Generate a random 10-digit phone number
        return ''.join(random.choices(string.digits, k=10))

    def produce(self, shutdown_event=threading.Event()):
        for _ in range(self.message_count):
            # Check if a shutdown was requested
            if shutdown_event.is_set():
                break
            
            text = self.generate_text()
            phone_number = self.generate_phone_number()
            message = {"text": text, "phone_number": phone_number, "retry_count": 0}
            
            self.message_queue.put(message)

