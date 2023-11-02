from src import MessageProducer, MessageSender, ProgressMonitor
from queue import Queue
import threading
import json

# Load configuration parameters
def load_config():
    with open('config/settings.json', 'r') as config_file:
        return json.load(config_file)

if __name__ == "__main__":

    # signal.signal(signal.SIGINT, signal_handler)
    config = load_config()

    # Shared resources
    message_queue = Queue()
    shutdown_event = threading.Event()

    # Instantiate the producer and senders with the shared resources
    producer = MessageProducer(
        message_queue=message_queue, 
        message_count=config['message_count']
    )
    
    senders = [
        MessageSender(
            mean_wait_time=sender_config['mean_wait_time'],
            failure_rate=sender_config['failure_rate'],
            message_queue=message_queue
        ) for sender_config in config['senders'] for _ in range(sender_config['quantity'])
    ]

    monitor = ProgressMonitor(config['update_interval'])

    # Start the threads
    producer_thread = threading.Thread(
        target=producer.produce,
        kwargs={"shutdown_event": shutdown_event}
    )
    
    sender_threads = [
        threading.Thread(
            target=sender.run,
            kwargs={
                "shutdown_event": shutdown_event,
                "resend_failed_msg": config["resend_failed_msg"],
                "max_resend_attempts": config['max_resend_attempts']
            },
            daemon=True
        ) for sender in senders
    ]
    
    monitor_thread = threading.Thread(
        target=monitor.monitor,
        kwargs={
            "producer": producer, 
            "senders": senders, 
            "shutdown_event": shutdown_event
        },
        daemon=True
    )

    producer_thread.start()
    monitor_thread.start()
    for thread in sender_threads:
        thread.start()

    # Wait for all sender threads to complete
    try:
        for thread in sender_threads:
            while thread.is_alive():
                thread.join(timeout=0.1)
    except KeyboardInterrupt:
        shutdown_event.set()  # If `Ctrl+C` is pressed, signal all threads for a save shutdown

    # Wait for the producer to finish
    producer_thread.join()

    # Wait for the monitor to finish
    monitor_thread.join()
