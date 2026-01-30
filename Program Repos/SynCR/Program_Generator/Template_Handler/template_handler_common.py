import random
from abc import ABC, abstractmethod
from Template_Manager.template_manager_impl import TemplateManagerImpl
from Config.global_config import config
from Data.block_map_loader import load_block_map
import Utilities.utils as utils
import Utilities.ast_utils as ast_utils
import Utilities.file_management_utils as file_management_utils
import Code_Formatter.code_formatter as code_formatter
import Code_Formatter.static_analyser as cpp_static_analyser
import os
import Utilities.program_generator_utils as program_generator_utils


class TemplateHandler(ABC):
    def __init__(self,grammar_parser,output_folder_path):
        self.config = config
        self.template_manager = TemplateManagerImpl(config.PATHS.template_path)
        self.block_map = load_block_map()
        self.grammar_parser = grammar_parser
        self.utils = utils
        self.ast_utils = ast_utils
        self.cpp_static_analyser = cpp_static_analyser
        self.code_formatter = code_formatter
        self.output_folder_path=output_folder_path
    
    @abstractmethod
    def generate_program(self):
        pass
    
    @abstractmethod
    def render_template(self, template_path="", random_template_mode=False):
        pass
    
    @abstractmethod
    def process_template(self, place_holders):
        pass
    
    def save_rendered_templates(self, templates, output_path):
        for item in templates:
            self.save_rendered_template(item,output_path)

    def save_rendered_template(self, template_content, output_path,program_name=""):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        if program_name =="":
            program_name= f"generated_program_{file_management_utils.generate_timestamp()}{program_generator_utils.get_the_generated_program_exstension()}"

            
        file_name = f'{output_path}/{program_name}'

        with open(file_name, "w") as output_file:
            output_file.write(template_content)
        
        return program_name
