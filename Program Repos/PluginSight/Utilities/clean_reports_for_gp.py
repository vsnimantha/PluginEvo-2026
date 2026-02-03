import os
import shutil
import time
from Config.global_config import config

def delete_old_items(folder_path, age_minutes=30):
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    now = time.time()
    age_seconds = age_minutes * 60

    # Walk through the directory tree from bottom up
    for root, dirs, files in os.walk(folder_path, topdown=False):
        # Delete old files
        for name in files:
            file_path = os.path.join(root, name)
            try:
                if now - os.path.getmtime(file_path) > age_seconds:
                    os.unlink(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete file {file_path}. Reason: {e}")

        # Delete old directories
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if now - os.path.getmtime(dir_path) > age_seconds:
                    shutil.rmtree(dir_path)
                    print(f"Deleted folder: {dir_path}")
            except Exception as e:
                print(f"Failed to delete folder {dir_path}. Reason: {e}")

def main():
    interval_seconds = 5 * 60  # 5 minutes

    while True:
        print(f"Cleaning folder: {config.PATHS.main_report_path}")
        delete_old_items(config.PATHS.main_report_path)
        print(f"Waiting {interval_seconds} seconds before next cleanup...\n")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()

# python3 -m Utilities.clean_reports_for_gp
