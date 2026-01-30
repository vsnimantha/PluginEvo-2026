from Program_Generator.program_generator_common import ProgramGenerator
from Template_Manager.template_manager_impl import TemplateManagerImpl
from Data.block_map_loader import load_block_map
from Config.global_config import config
from Program_Generator.Template_Handler.template_handler_single import TemplateHandlerSingle
from Program_Generator.Template_Handler.template_handler_multi import TemplateHandlerMulti
from Utilities.file_management_utils import create_folder_with_timestamp,create_folder
from Utilities.constants import Constants
import subprocess
import os


class ProgramGeneratorFull_GP_Compiler_Test(ProgramGenerator):
    def __init__(self, num_programs: int = 1, language: str = "C++", template_type: str = "random"):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.initialized = True
            self.template_manager = TemplateManagerImpl(config.PATHS.template_path)
            self.block_map = load_block_map()

        # Store parameters
        self.num_programs = num_programs
        self.language = language
        self.template_type = template_type

        # Update config dynamically (optional, if other parts of system rely on it)
        config.update_config_value("PROGRAM_GENERATION", "combination_limit", self.num_programs)
        config.update_config_value("PROGRAM_GENERATION", "programming_language", self.language)
        config.update_config_value("PROGRAM_GENERATION", "specific_template", self.template_type)
        config.update_config_value("PROGRAM_GENERATION", "format_generated_code", False)
        config.update_config_value("PROGRAM_GENERATION", "static_analysis_of_generate_code", False)

    def generate_program(self):
        folder_path, time_stamp = create_folder_with_timestamp(config.PATHS.output_path)
        config.update_config_value('PATHS', 'current_generating_code_path', folder_path)
        config.update_config_value("PROGRAM_GENERATION", "smart_generation", True)

        # Always use smart generation
        templateHandler = TemplateHandlerMulti(self.grammar_parser, folder_path)
        generated_program_list = templateHandler.generate_program()

        # Reset path
        config.update_config_value('PATHS', 'current_generating_code_path', Constants.DEFAULT_OUTPUT_PATH)

        return generated_program_list, time_stamp

