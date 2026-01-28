import random
import Utilities.ast_utils as ast_utils
from Program_Generator.program_generator_common import ProgramGenerator
from Program_Generator.placeholder_info import PlaceholderInfo
from Template_Manager.template_manager_impl import TemplateManagerImpl
from Data.block_map_loader import load_block_map
import Utilities.utils as utils
import Utilities.ast_utils as ast_utils

class ProgramGeneratorFull(ProgramGenerator):
    
    def __init__(self):
        if not hasattr(self, 'initialized'):  
            super().__init__()
            # self.folder_path = folder_path
            self.initialized =True
            self.template_manager = TemplateManagerImpl('Program_Templates')
            self.block_map=load_block_map()
            
    def generate_program(self):
        # template=random.choice(self.template_manager.templates)
        template='Template_1.tmpl'
        template='Reference_Programs/Templates/array_reverse.tmpl'
        rendered_template=self.render_template(template)
        # print(rendered_template)


        # self.template_manager.save_rendered_template(rendered_template,template)

        # print(f'template data {rendered_template}')

    def render_template(self,template_path):
        template_content=self.template_manager.read_template(template_path)
        place_holders = utils.extract_template_placeholders(template_content)
        placeholder_infos = self.process_template(place_holders)
        print(placeholder_infos)

        # for item in place_holders:
        #     if utils.is_function(item):
        #         parts=item.split(':')
        #         unique_id=parts[0]
        #         place_holder=parts[1]
        #         info={info.unique_id: info for info in placeholder_infos}.get(unique_id, None)

        #         if info is not None and place_holder != info.placeholder:
        #             function_name, function_return_type = ast_utils.get_function_info_from_ast(info.ast_tree)
        #             func_code_element = None
        #             if place_holder=='FUNCTION_PROTOTYPE_DEFINITION':
        #                 func_code_element = f'{function_return_type} {function_name}();'
        #             elif place_holder=='FUNCTION_CALL':
        #                 func_code_element = f'{function_name}();'

        #             template_content = template_content.replace(f"{{{{{item}}}}}", func_code_element)
        #         else:    
        #             template_content = template_content.replace(f"{{{{{item}}}}}", info.generated_code)
        #     else:    
        #         info={info.placeholder_block: info for info in placeholder_infos}.get(item,None)
        #         if info is not None:
        #             template_content = template_content.replace(f"{{{{{item}}}}}", info.generated_code)

        return template_content
    

    def process_template(self, place_holders):
        # grouped_placeholders = self.template_manager.group_placeholders_by_id(place_holders)
        # # print(grouped_placeholders)
        placeholder_infos = []

        for item in place_holders:
            parts = item.split(':')
            unique_id = None
            name=None
            place_hoder_data = None
            item_to_process = None
            params = []


            if len(parts) > 1:
                if parts[0]:
                    id_var=parts[0].split(',')
                    if len(id_var)>1:
                        unique_id = id_var[0]
                        name=id_var[1]
                    else:
                        unique_id = parts[0]
                
                place_hoder_data = parts[1]
            else:
                place_hoder_data = parts[0]    
            
            params_parts = place_hoder_data.split('@')

            item_to_process = params_parts[0]
            if len(params_parts) > 1:
                params = params_parts[1].split(',')
                print(params)
                for param in params:
                    ref_var=utils.extract_parameter_references(param)
                    if ref_var is not None:
                        print(ref_var)
                    else:
                        print(param)
                        
                # processed_params = self.process_params(params)


            grammar_rule = self.block_map.get(item_to_process)
            if grammar_rule is not None:
                generated_code, ast_tree = self.grammar_parser.generate_code(grammar_rule)
                
                # Create PlaceholderInfo object and add it to the list
                info = PlaceholderInfo(item,item_to_process ,unique_id, grammar_rule, generated_code, ast_tree, params,name)
                placeholder_infos.append(info)
                

        return placeholder_infos

    # TODO:: Implement this method
    def process_params(self, params):
        processed_params = []
        

        return processed_params
    
    def save_rendered_template(self, template_content, output_path):
        """
        Writes the rendered template to the output file.
        """
        with open(output_path, "w") as output_file:
            output_file.write(template_content)


def generate_program_main():   
    program_generator = ProgramGeneratorFull()
    program_generator.generate_program()


if __name__ == '__main__':

 generate_program_main()

   #python3 -m Program_Generator.program_generator_tmpl_parfunction