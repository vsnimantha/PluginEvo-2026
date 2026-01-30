import random
from Program_Generator.Template_Handler.template_handler_common import TemplateHandler
from Program_Generator.placeholder_info import PlaceholderInfo
import Utilities.file_management_utils as file_management_utils
import Utilities.program_generator_utils as program_generator_utils


class TemplateHandlerMulti(TemplateHandler):
    def __init__(self, grammar,output_folder_path):
        super().__init__(grammar,output_folder_path)

    def get_template(self):
        generate_random_template = self.config.PROGRAM_GENERATION.build_a_random_template

        template_content=""
        if generate_random_template:
            template_content = self.template_manager.build_custom_template()
        else:
            use_random_templates = self.config.PROGRAM_GENERATION.use_random_templates
            template = ""
            if use_random_templates:
                template = random.choice(self.template_manager.templates)
                print(f'Randomly Selected Template: {template}')
            else:
                template = self.config.PROGRAM_GENERATION.specific_template
    
            if template == "":
                print(f"\x1b[31mError: No template selected. Please check the config.ini file\x1b[0m") 
                print(f"\x1b[32mFor specific template configure 'specific_template' key with your desired template \x1b[32m") 
                print(f"\x1b[32mFor random template selection set 'use_random_templates' to True\x1b[32m")
                print(f"\x1b[32mFor random template generation 'build_a_random_template' to True\x1b[32m")
                return
            else:
                template_content = self.template_manager.read_template(template)

        return template_content

    def generate_program(self):
        
        rendered_template_list=[]

        template_content=self.get_template()
                
        if self.config.PROGRAM_GENERATION.print_template_to_console:
            print(f"Non-rendered template content: \n \n {template_content}")

        place_holders = self.utils.extract_template_placeholders(template_content)

        number_of_combinations = self.config.PROGRAM_GENERATION.combination_limit
        if number_of_combinations and number_of_combinations != "OFF":
            number_of_combinations = int(number_of_combinations)
        else:
            number_of_combinations = random.randint(1,1000)

        print(f"{number_of_combinations} - Smart programs requested from the program generator \n") #Debug Print


        placeholder_data = self.process_template(place_holders,number_of_combinations)

        for i in range(number_of_combinations):
            rendered_template = self.render_template(i,place_holders,template_content,placeholder_data)

            if self.config.PROGRAM_GENERATION.format_generated_code:
                rendered_template = self.code_formatter.format_cpp_code_with_clang_format(rendered_template)

            if self.config.PROGRAM_GENERATION.print_rendered_template_to_console:
                print(f"Rendered template content: \n {rendered_template}")

            if self.config.PROGRAM_GENERATION.static_analysis_of_generate_code:
                is_correct, message = self.cpp_static_analyser.check_syntax_from_string(rendered_template)
                print(f"Static analyser message: {message}")

                if is_correct:
                    file_name= f"generated_program_{file_management_utils.generate_timestamp()}{program_generator_utils.get_the_generated_program_exstension()}"
                    if self.config.PROGRAM_GENERATION.save_generated_programs:
                        path=f"{self.config.PATHS.current_generating_code_path}/{self.config.PATHS.generated_program_output}"
                        file_name=self.save_rendered_template(rendered_template,path,file_name)

                    rendered_template_list.append((rendered_template, file_name))
                else:
                    print("Generated code is syntactically not correct")
            else:
                file_name= f"generated_program_{file_management_utils.generate_timestamp()}{program_generator_utils.get_the_generated_program_exstension()}"
                if self.config.PROGRAM_GENERATION.save_generated_programs:
                    path=f"{self.config.PATHS.current_generating_code_path}/{self.config.PATHS.generated_program_output}"
                    file_name=self.save_rendered_template(rendered_template,path,file_name)

                rendered_template_list.append((rendered_template, file_name))

        return rendered_template_list

    def render_template(self, current_processing_template,extracted_place_holders,template_content,placeholder_data=[]):

        for item in extracted_place_holders:
            relevant_generated_data = []
            

            if self.utils.is_function(item):
                parts = item.split(':')
                unique_id = parts[0]
                place_holder = parts[1]

                for data in placeholder_data:
                    data_parts=data[0].split(':')
                    if len(data_parts)>1:
                        data_unique_id = data_parts[0]
                        data_place_holder = data_parts[1]
                        if data_unique_id == unique_id:
                            relevant_generated_data.extend(data[1])

                info = relevant_generated_data[current_processing_template]

                if info is not None and place_holder != info.placeholder:
                    function_name, function_return_type = self.ast_utils.get_function_info_from_ast(info.ast_tree)
                    func_code_element = ""
                    if place_holder == 'FUNCTION_CALL':
                        if info.is_parameterised:
                            if info.parameters is not None:
                                param_values = [param.identifier_value for param in info.parameters]
                                params = ",".join(param_values)
                                for param in info.parameters:
                                    func_code_element += f"{param.data_type_value} {param.identifier_value} = {param.data_value}; \n"

                            func_code_element += f'\n{function_name}({params});'
                        else:
                            if info.recursive_function:
                                func_code_element += f'\n{function_name}({10}, {20});'
                            else:
                                func_code_element = f'{function_name}();'

                    template_content = template_content.replace(f"{{{{{item}}}}}", func_code_element)
                else:
                    template_content = template_content.replace(f"{{{{{item}}}}}", info.generated_code)
            else:
                for data in placeholder_data:
                    if data and data[0] == item:
                        relevant_generated_data.extend(data[1])
                if len(relevant_generated_data) > 0:
                    info = relevant_generated_data[current_processing_template]
                    if info is not None:
                        template_content = template_content.replace(f"{{{{{item}}}}}", info.generated_code)
        return template_content
    

    def process_template(self, place_holders,number_of_combinations):
        place_holder_data=[]

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
                grammar_rule = random.choice(grammar_rule_data.split("|")) if "|" in grammar_rule_data else grammar_rule_data



                generated_combinations=self.grammar_parser.generate_code_multi(grammar_rule,number_of_combinations)
                print(f"Generated combinations for {item_to_process}: {len(generated_combinations)}")
                placeholder_infos = []
                for decl in generated_combinations:
                    # Each 'decl' is already the tuple (generated_code, ast_list, param_list, is_param_function, is_recursive_function)
                    generated_code, ast_tree, param_list, is_param_function, is_recursive_function = decl

                    if self.config.PROGRAM_GENERATION.print_ast_to_console:
                        self.ast_utils.print_ast_tree(ast_tree)

                    if self.config.PROGRAM_GENERATION.save_ast:
                        self.ast_utils.save_ast(ast_tree, grammar_rule_data)

                    if self.config.PROGRAM_GENERATION.save_ast_as_json:
                        self.ast_utils.save_ast_as_json(ast_tree, grammar_rule_data,item)

                    info = PlaceholderInfo(item, item_to_process, unique_id, grammar_rule, generated_code, ast_tree, param_list, is_param_function, is_recursive_function)
                    placeholder_infos.append(info)
                
                place_holder_data.append((item, placeholder_infos))

        return place_holder_data
