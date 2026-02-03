import threading
import time
import sys

# Use a class to encapsulate the spinner functionality
class Spinner:
    def __init__(self,message):
        self.stop_spinner = False
        self.spinner_thread = None
        self.loading_states = [
            message, 
            f"{message} .", 
            f"{message} ..", 
            f"{message} ..."
        ]

    def _loading_spinner(self):
        idx = 0
        # Hide the cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            while not self.stop_spinner:
                # Clear the line and print new state
                sys.stdout.write("\r" + " " * 30 + f"\r{self.loading_states[idx % len(self.loading_states)]}")
                sys.stdout.flush()
                idx += 1
                time.sleep(0.5)
        finally:
            # Show cursor and clean up
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def start(self):
        """Start the spinner in a background thread"""
        self.stop_spinner = False
        self.spinner_thread = threading.Thread(target=self._loading_spinner)
        self.spinner_thread.start()

    def stop(self):
        """Stop the spinner and clean up"""
        self.stop_spinner = True
        if self.spinner_thread:
            self.spinner_thread.join()