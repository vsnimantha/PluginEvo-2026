import os
from datetime import datetime
import shutil


def generate_timestamp():
    """Generate a timestamp string with milliseconds"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]  # %f is microseconds, [:-3] trims to milliseconds

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
    return folder_path,timestamp

def clean_directory(directory_path):
    """Cleans the specified directory by removing all files and subdirectories."""
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return

    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)  # Remove files and symbolic links
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories recursively
            print(f"Removed: {item_path}")
        except Exception as e:
            print(f"Error removing {item_path}: {e}")

    print(f"Directory '{directory_path}' cleaned successfully.")