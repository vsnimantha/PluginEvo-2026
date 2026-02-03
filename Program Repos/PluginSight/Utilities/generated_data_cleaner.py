import Utilities.file_management_utils as file_management_utils
import Plugin_Manager.coverage_generator as coverage_generator
from Config.global_config import config

def clean_data():
    file_management_utils.clean_directory(config.PATHS.main_report_path)
    file_management_utils.clean_directory(config.PATHS.generated_program_save_path)
    coverage_generator.clean_up(config.PATHS.plugin_output_path)

if __name__ == "__main__":
    clean_data()

# python3 -m Utilities.generated_data_cleaner 

