import sys
import os
from Config.global_config import config

def disable_print():
    """Disable the print function."""
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    """Enable the print function."""
    sys.stdout = sys.__stdout__

def debug_print(message):
    """Custom debug print function."""
    if config.GENERAL.debug_mode:
        print(message)

def main():
    while True:
        user_input = input("Type 'enable' to allow printing, 'disable' to suppress printing, or 'exit' to quit: ").strip().lower()
        if user_input == 'enable':
            enable_print()
            print("Printing is now enabled!")
        elif user_input == 'disable':
            disable_print()
            enable_print()  # Switch stdout back to show the message
            print("Printing is now disabled!")
        elif user_input == 'exit':
            enable_print()  # Ensure printing is restored before exiting
            print("Exiting the program. Goodbye!")
            break
        else:
            enable_print()  # Switch stdout back to show the message
            print("Invalid input. Please type 'enable', 'disable', or 'exit'.")

if __name__ == "__main__":
    main()
