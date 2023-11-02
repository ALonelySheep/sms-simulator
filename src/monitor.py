import time

class ProgressMonitor:
    def __init__(self, update_interval):
        self.update_interval = update_interval
        self.total_sent = 0
        self.total_failed = 0
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def update(self, sent, failed):
        self.total_sent += sent
        self.total_failed += failed

    def print_report(self):
        elapsed_time = time.time() - self.start_time
        total_messages = self.total_sent + self.total_failed
        fail_rate = self.total_failed / total_messages if total_messages > 0 else 0
        average_time_per_message = elapsed_time / total_messages if total_messages > 0 else 0
        
        # Calculate hours, minutes and seconds
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format the string as HH:MM:SS
        formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        
        print(f"\n[Progress Monitor] ({formatted_time})")
        print(f" Messages sent: {self.total_sent}")
        print(f" Messages failed: {self.total_failed} ({fail_rate:.2%})")
        print(f" Average time per message: {average_time_per_message:.6f} seconds")

    def monitor(self, producer, senders, shutdown_event):
        self.start() # Start the timer
        
        while any(sender.is_alive for sender in senders):
            if shutdown_event.is_set():
                print("\n[Error] Shutdown signal received. Shutting down...")
                break            
        
            time.sleep(self.update_interval)
        
            for sender in senders:
                self.update(sender.sent_count, sender.failed_count)
                sender.sent_count = 0
                sender.failed_count = 0
        
            self.print_report()
        
        print("\n[Info] All threads have terminated. Final report:")
        self.print_report()
        shutdown_event.set()
