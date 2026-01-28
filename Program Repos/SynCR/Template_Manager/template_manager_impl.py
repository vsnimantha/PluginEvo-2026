from Template_Manager.template_manager_common import TemplateManager
from Utilities.template_manager_constants import TemplateManagerConstants
from Utilities import template_manager_utils
from Data.block_map_loader import load_block_map
from Config.global_config import config

import random

class TemplateManagerImpl(TemplateManager):

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):  
            super().__init__(file_path)
            self.initialized =True
            self.block_map=load_block_map()

    def build_custom_template(self):
        model_template=TemplateManagerConstants.MODEL_TEMPLATE
        num_of_function=random.randrange(1,config.TEMPLATE_GENERATION.number_of_functions)

        function_definitions=""
        function_calls=""
        program_body=""
        for _ in range(1,num_of_function):
            fun_id=f'fid_{_}:'
            function_definitions+=f'{{{{{fun_id+random.choice(TemplateManagerConstants.FUNCTION_KEYS)}}}}} \n'
            function_calls+=f'{{{{{fun_id + "FUNCTION_CALL"}}}}} \n'
            
     
        program_body+=function_calls
        random_items = random.sample(list(self.block_map.keys()), config.TEMPLATE_GENERATION.number_of_other_elements)
        for item in random_items:
            if item not in TemplateManagerConstants.EXCLUDE_LIST:
                program_body+=f'{{{{{template_manager_utils.generate_id(item)+item}}}}} \n'

        model_template = model_template.replace(f"{{{{FUNCTIONS}}}}", function_definitions)
        model_template = model_template.replace(f"{{{{MAIN_BODY}}}}", program_body)

        return model_template
    
def retrieve_templates():
    
    # file_path = 'Grammar/Program_Constructs/if_statement.bnf'
    folder_path = 'Program_Templates'

    template = TemplateManagerImpl(folder_path)
    print(template.templates)
    template.build_custom_template()


if __name__ == '__main__':
    pass
    # retrieve_templates()


# python3 -m Template_Manager.template_manager_impl