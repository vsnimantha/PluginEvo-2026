import os
from datetime import datetime

def generate_timestamp():
    """Generate a timestamp string in the format YYYY-MM-DD_HH-MM-SS."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def create_folder(path):
    """Create a folder at the specified path."""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Folder '{path}' created successfully.")
    except OSError as error:
        print(f"Error creating folder: {error}")

def create_folder_with_timestamp(path_prefix):
    """Create a folder with a timestamp in its name at the specified path."""
    timestamp = generate_timestamp()
    folder_path = os.path.join(path_prefix, timestamp)
    create_folder(folder_path)
    return folder_path

# Example usage
# path_prefix = "/path/to/your/folder"
# new_folder_path = create_folder_with_timestamp(path_prefix)
# print(f"New folder created at: {new_folder_path}")
