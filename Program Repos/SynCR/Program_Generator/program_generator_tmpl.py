import random
import Utilities.ast_utils as ast_utils
from Program_Generator.program_generator_common import ProgramGenerator
from Program_Generator.placeholder_info import PlaceholderInfo
from Template_Manager.template_manager_impl import TemplateManagerImpl
from Data.block_map_loader import load_block_map
import Utilities.utils as utils
import Utilities.ast_utils as ast_utils
from Config.global_config import config
import Code_Formatter.code_formatter as code_formatter
import Code_Formatter.static_analyser as cpp_static_analyser

class ProgramGeneratorFull(ProgramGenerator):
    
    def __init__(self):
        if not hasattr(self, 'initialized'):  
            super().__init__()
            self.initialized =True
            self.template_manager = TemplateManagerImpl(config.PATHS.template_path)
            self.block_map=load_block_map()
            
    def generate_program(self):
        rendered_template=""
        generate_random_template=config.PROGRAM_GENERATION.build_a_random_template

        if generate_random_template:
            rendered_template=self.render_template(random_template_mode=generate_random_template)
        else:
            use_random_templates=config.PROGRAM_GENERATION.use_random_templates
            template=""
            if use_random_templates:
                template=random.choice(self.template_manager.templates)
                print(f'Randomly Selected Template: {template}') #Debug Print
            else:
                template=config.PROGRAM_GENERATION.specific_template

      
            if template=="":
                print(f"\x1b[31mError: No template selected. Please check the config.ini file\x1b[0m") 
                print(f"\x1b[32mFor specific template configure 'specific_template' key with your desired template \x1b[32m") 
                print(f"\x1b[32mFor random template selection set 'use_random_templates' to True and make sure templates are available in the folder confiured at 'template_path'\x1b[32m ") 
                print(f"\x1b[32mFor random template generation 'build_a_random_template' to True\x1b[32m") 
                return
              
            # print(f'Processing Template: {template}') #Debug Print
            rendered_template=self.render_template(template)

        if config.PROGRAM_GENERATION.format_generated_code:
            # print(f"Templated before formatting \n {rendered_template}") #Debug Print
            rendered_template=code_formatter.format_cpp_code_with_clang_format(rendered_template) #formatting the code using clang
            # print(f"Templated after formatting \n {rendered_template}") #Debug Print 

        if config.PROGRAM_GENERATION.print_rendered_template_to_console:
            print(f"Rendered template content: \n {rendered_template}") #Debug Print

        if config.PROGRAM_GENERATION.static_analysis_of_generate_code:
            is_correct, message = cpp_static_analyser.check_syntax_from_string(rendered_template)
            print(f"Static analyser message: {message}")  # Debug Print

            if is_correct:
                return rendered_template
            print("Generated code is syntactically not correct")  # Debug Print

        return rendered_template

        # self.template_manager.save_rendered_template(rendered_template,template) 



    def render_template(self,template_path="",random_template_mode=False):
        # print(f"Random Template Mode: {random_template_mode}") #Debug Print
        # print(f"Template path: {template_path}") #Debug Print
        template_content=""
        if random_template_mode:
            template_content=self.template_manager.build_custom_template()
        else:
            template_content=self.template_manager.read_template(template_path)

        if config.PROGRAM_GENERATION.print_template_to_console:
            print(f"Non-rendered template content: \n \n {template_content}") #Debug Print

        place_holders = utils.extract_template_placeholders(template_content)
        placeholder_infos = self.process_template(place_holders)

        for item in place_holders:
            if utils.is_function(item):
                parts=item.split(':')
                unique_id=parts[0]
                place_holder=parts[1]
                info={info.unique_id: info for info in placeholder_infos}.get(unique_id, None)

                if info is not None and place_holder != info.placeholder:
                    function_name, function_return_type = ast_utils.get_function_info_from_ast(info.ast_tree)
                    func_code_element = ""
                    if place_holder=='FUNCTION_CALL':
                        if info.is_parameterised:
                            if info.parameters is not None:
                                param_values = [param.identifier_value for param in info.parameters]  # Collect all identifier_value
                                params = ",".join(param_values)  # Join them with a comma
                                for param in info.parameters:
                                    func_code_element+=f"{param.data_type_value} {param.identifier_value} = {param.data_value}; \n"
                            
                            func_code_element += f'\n{function_name}({params});'

                            # print(f"function code elemnt : {func_code_element}") #Debug Print    
                        else:
                            if info.recursive_function:
                                    if place_holder=='FUNCTION_CALL':
                                        func_code_element += f'\n{function_name}({10},{20});' #TODO: dyanamic implementation including changing the grammar to recursive
                            else:                  
                                func_code_element = f'{function_name}();'

                    template_content = template_content.replace(f"{{{{{item}}}}}", func_code_element)
                else:
                    # print(f"info :: {info}") #Debug Print
                    # print(f"item :: {item}") #Debug Print  
                    template_content = template_content.replace(f"{{{{{item}}}}}", info.generated_code)
            else:    
                info={info.placeholder_block: info for info in placeholder_infos}.get(item,None)
                if info is not None:
                    template_content = template_content.replace(f"{{{{{item}}}}}", info.generated_code)

        return template_content
    

    def process_template(self, place_holders):
        # grouped_placeholders = self.template_manager.group_placeholders_by_id(place_holders)
        # # print(grouped_placeholders)
        placeholder_infos = []

        for item in place_holders:
            parts = item.split(':')
            unique_id = None
            item_to_process = None
            if len(parts) > 1:
                unique_id = parts[0]
                item_to_process = parts[1]
            else:
                item_to_process = parts[0]    
            

            
            grammar_rule_data = self.block_map.get(item_to_process)
            if grammar_rule_data is not None:
                if "|" in grammar_rule_data:
                    grammar_rule=random.choice(grammar_rule_data.split("|"))  # Split the string by '|'
                else:
                    grammar_rule=grammar_rule_data  

                generated_code, ast_tree, param_list,is_param_function,is_recursive_function = self.grammar_parser.generate_code(grammar_rule)

                if config.PROGRAM_GENERATION.print_ast_to_console:
                    ast_utils.print_ast_tree(ast_tree)

                if config.PROGRAM_GENERATION.save_ast:
                    ast_utils.save_ast(ast_tree,grammar_rule_data)

                if config.PROGRAM_GENERATION.save_ast_as_json:
                    ast_utils.save_ast_as_json(ast_tree,grammar_rule_data)

                # Create PlaceholderInfo object and add it to the list
                info = PlaceholderInfo(item,item_to_process ,unique_id, grammar_rule, generated_code, ast_tree,param_list,is_param_function,is_recursive_function)
                placeholder_infos.append(info)
                

        return placeholder_infos

    
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

#  for item in range(1,10):
#      generate_program_main()

   #python3 -m Program_Generator.program_generator_tmpl 