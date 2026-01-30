import Utilities.file_management_utils as file_management_utils
from Config.global_config import config

def clean_data():
    file_management_utils.clean_directory(config.PATHS.output_path)


if __name__ == "__main__":
    clean_data()

# python3 -m Utilities.generated_data_cleaner 

