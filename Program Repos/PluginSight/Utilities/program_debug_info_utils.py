import sys
import os
from datetime import datetime
import subprocess

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, message):
        for stream in self.streams:
            stream.write(message)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def start_write_console_output_to_log_file():
    log_dir = os.path.join("Execution_Logs", datetime.now().strftime('%Y-%m-%d'))
    os.makedirs(log_dir, exist_ok=True) 

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(log_dir, f"trace_{timestamp}.log")

    log_file = open(log_path, "w")

    # Redirect sys.stdout to both console and log file
    sys.stdout = Tee(sys.__stdout__, log_file)
    sys.stderr = Tee(sys.__stderr__, log_file)
    return log_file


def stop_write_console_output_to_log_file(log_file):
    # Close the log file when done
    log_file.close()

    # Reset sys.stdout back to console only
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    
    print()
    print("Redirection complete. Check your logs!")


if __name__ == "__main__":
    # Set up log directory and file path
    log_dir = "Execution_Logs"  # Specify the directory where logs will be saved
    os.makedirs(log_dir, exist_ok=True)

    # Generate a timestamped log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(log_dir, f"trace_{timestamp}.log")

    # Open the log file
    log_file = open(log_path, "w")

    # Redirect both stdout and stderr to the log file
    original_stdout = sys.stdout  # Save original stdout
    original_stderr = sys.stderr  # Save original stderr
    sys.stdout = log_file
    sys.stderr = log_file

    # Example: Your program outputs
    print("This is a Python print statement.")
    import math
    print(f"The square root of 16 is {math.sqrt(16)}.")

    # Example: Outputs from libraries or shell commands
    os.system("echo This is shell command output")
    os.system("ls -l")  # List directory contents (on Unix/Linux)

    # Reset stdout and stderr to original
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    # Close the log file
    log_file.close()

    print(f"All outputs have been logged to: {log_path}")
