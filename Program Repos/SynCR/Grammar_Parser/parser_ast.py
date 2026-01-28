import random
import string
from Grammar_Parser.parser_common import GrammarParser
from Grammar_Parser.ast_node import ASTNode
from Grammar_Parser.parameter_info import ParameterInfo
from Utilities.utils import Constants, differentiate_list_type
import Utilities.ast_utils as ast_utils
import Utilities.grammar_parser_utils as grammar_parser_utils
from Config.global_config import config



class GrammarParserAst(GrammarParser):

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            super().__init__(file_path)
            self.initialized = True

    def parse(self):
        pass
        # for lhs, rhs in self.grammar.items():
        #     self.rules[lhs.strip('<>')] = rhs

        # for key, value in self.rules.items():
        #     for sublist in value:
        #         for item in sublist:
        #             if item.startswith('<') and item.endswith('>'):
        #                 print(item)

        #                 key_check = item[1:-1]

        #                 grammarPath = f"Grammar/Program_Constructs/{key_check}.bnf"
        #                 grammar = self.read_bnf_grammar(grammarPath)

        #                 print(grammar)

    def generate_code(self, element):
        root = ASTNode("root")
        stack = [(element, False, 0, set(), root)]  # (element, is_processed, indentation_level, local_visited, parent_node)
        code = ""
        current_line = ""
        indent_level = 0
        paren_level = 0

        # print(f"Starting generation with element: {element}")  # Debug print
        is_function = 'function' in element
        is_param_function = 'function_parameterised' in element
        is_recursive_function = 'function_recursive' in element
        current_return_type = None

        #function parameter processing
        is_param_processing=False
        param_data_type=""
        param_data_type_block=""
        param_identifier_block=""
        param_identifier=""
        param_code =""
        param_list = []
        param_value=None
        # print(f"Is param function: {is_param_function}")  # Debug print

        #recursive function data
        recursive_function_name=""
        original_function_name_processed=False

        #array processing related variables
        is_array_processing=False
        array_data_type = ""
        array_identifier = ""
        array_length = 0
        array_loop=""

        #handling variable declaration data types
        is_var_declaration_processing=False
        var_data_type=""

        def flush_line(force_newline=False):
            nonlocal code, current_line, indent_level
            if current_line.strip() or force_newline:
                code += "    " * indent_level + current_line.strip() + "\n"
                current_line = ""

        while stack:
            is_last_element = len(stack) == 1 # Check if the current element is the last element in the stack
            # print(f"Stack: {len(stack)}")  # Debug print
            current_element, is_processed, _, local_visited, parent_node = stack.pop()
            # print(f"Processing: {current_element}, Processed: {is_processed}")  # Debug print 

            if is_processed:
                if current_element == "(":
                    current_line += current_element
                    paren_level += 1
                elif current_element == ")":
                    current_line += current_element
                    paren_level -= 1
                    if paren_level == 0:
                        flush_line()
                elif current_element == "{":
                    flush_line()
                    # code += "    " * indent_level + "{\n"
                    code += f"{'    ' * indent_level}{{\n"
                    indent_level += 1
                elif current_element == "}":
                    # print(f"Paren_level: {paren_level}")  # Debug print
                    indent_level = max(0, indent_level - 1)
                    flush_line()
                    #handling the return data for function
                    # print(f"Current return type: {current_return_type}") # Debug print
                    if is_function and current_return_type!=None and is_last_element:
                        print_statements,math_equation=grammar_parser_utils.process_params_data(param_list,self.grammar)
                        # print(f'Print statments {print_statements}')  #Debug print
                        # print(f'Math equation {math_equation}')  #Debug print

                        for print_statement in print_statements:
                            code += f"{'    ' * indent_level} {print_statement}\n"

                        if current_return_type!='void':
                            function_return_data=grammar_parser_utils.process_return_type(current_return_type,self.grammar)
                            # print(f"Current return type: {current_return_type}") # Debug print
                            # print(f"Function return data: {function_return_data}") # Debug print
                            code += f"{'    ' * indent_level} return {function_return_data};\n"
                            current_return_type=None
                    # code += "    " * indent_level + "}\n"
                    code += f"{'    ' * indent_level}}}\n"
                elif current_element == ";":
                    current_line += current_element

                    if is_array_processing and config.PROGRAM_GENERATION.print_array_data:  
                        current_line+=f"\n {array_loop}"
                        is_array_processing=False
                    flush_line()
                else:
                    if not current_line and current_element in ["if", "else", "for", "while"]:
                        flush_line(True)
                    current_line += current_element + " "
                    
                node = ASTNode("terminal", current_element)
                parent_node.add_child(node)

            else:
                if current_element in local_visited:
                    continue
                local_visited.add(current_element)

                if not any(current_element in d for d in self.grammar):
                    # print(f"Element not found in grammar: {current_element}")  # Debug print
                    if current_element == "(":
                        current_line += current_element
                        paren_level += 1
                    elif current_element == ")":
                        current_line += current_element
                        paren_level -= 1
                        if paren_level == 0:
                            flush_line()
                    elif current_element == "{":
                        flush_line()
                        # code += "    " * indent_level + "{\n"
                        code += f"{'    ' * indent_level}{{\n"
                        indent_level += 1
                    elif current_element == "}":
                        # print(f"Paren_level: {paren_level}")  # Debug print
                        indent_level = max(0, indent_level - 1)
                        flush_line()
                        #handling the return data for function
                        # print(f"Current return type: {current_return_type}") # Debug print
                        if is_function and current_return_type!=None and is_last_element:
                            print_statements,math_equation=grammar_parser_utils.process_params_data(param_list,self.grammar)
                            # print(f'Print statments {print_statements}') #Debug print
                            # print(f'Math equation {math_equation}') #Debug print
                            for print_statement in print_statements:
                                code += f"{'    ' * indent_level} {print_statement}\n"

                            if current_return_type!='void':
                                function_return_data=grammar_parser_utils.process_return_type(current_return_type)
                                # print(f"Current return type: {current_return_type}") # Debug print
                                # print(f"Function return data: {function_return_data}") # Debug print
                                code += f"{'    ' * indent_level} return {function_return_data};\n"
                                current_return_type=None

                        # code += "    " * indent_level + "}\n"
                        code += f"{'    ' * indent_level}}}\n"
                    elif current_element == ";":
                        current_line += current_element
                        flush_line()
                    else:
                        if not current_line and current_element in ["if", "else", "for", "while"]:
                            flush_line(True)
                        current_line += current_element + " "
                    
                    # print(f"Current terminal element: {current_element}")  # Debug print
                    node = ASTNode("terminal", current_element)
                    parent_node.add_child(node)
                else:
                    element_data = [d[current_element] for d in self.grammar if current_element in d]
                    # print(f"Element data: {element_data}")  # Debug print
                    if element_data:
                        rule_node = ASTNode("rule", current_element)
                        parent_node.add_child(rule_node)

                        if current_element == '<parameter>':
                            is_param_processing=True
                            # print(f"Is param processing: {is_param_processing}")  # Debug print

                        if current_element == '<array>':
                            is_array_processing=True
                            # print(f"Is array processing: {is_array_processing}")  # Debug print
                        if current_element == '<var_declaration>':
                            is_var_declaration_processing=True
                            # print(f"Is var declaration processing: {is_var_declaration_processing}")  # Debug print

                        # print(f"Current Element: {current_element}")  # Debug print
                        for item in element_data:
                            list_type = differentiate_list_type(item)
                            if list_type == Constants.SINGLE_STRING_LIST:
                                str_item = str(random.choice(item)[0])
                                # print(f"String item: {str_item}")  # Debug print

                                if str_item.startswith('<') and str_item.endswith('>'):
                                    if str_item =="<rand_strings>":
                                        str_item=grammar_parser_utils.process_rand_string()
                                        stack.append((str_item, True, indent_level, set(), rule_node))
                                    elif str_item =="<rand_array_values>":
                                        str_item,iterative_data_loop= grammar_parser_utils.generate_array_data(array_data_type,array_identifier,array_length,self.grammar)
                                        array_loop=iterative_data_loop
                                        stack.append((str_item, True, indent_level, set(), rule_node))
                                    elif is_var_declaration_processing and str_item =="<rand_var_values>":
                                        str_item = grammar_parser_utils.process_variable_data_type(var_data_type,self.grammar)
                                        stack.append((str_item, True, indent_level, set(), rule_node))
                                    else:    
                                        stack.append((str_item, False, indent_level, set(), rule_node))

                                else:


                                    if is_function and current_element == "<return_type>":
                                        current_return_type = str_item
                                        # print(f"Current return type Single: {current_return_type}") # Debug print

                                        #adding parameters of the function to the list, to be used in the function call
                                    if is_param_function and is_param_processing:
                                        if current_element == "<data_type>":
                                            param_code += f"{str_item} "
                                            param_data_type_block=current_element
                                            param_data_type=str_item
                                            param_value=grammar_parser_utils.process_param_values(param_data_type)
                                            # print(f"Current data type: {str_item}") # Debug print
                                        elif current_element == "<identifier_parameter>":
                                            # print(f"Before : {str_item}")   #Debug Print
                                            str_item=grammar_parser_utils.check_duplicate_params(param_list,str_item,item)
                                            # print(f"After : {str_item}") #Debug Print

                                            param_code+=f"{str_item}"
                                            param_identifier_block=current_element
                                            param_identifier=str_item
                                            # print(f"Current identifier: {str_item}") 
                                            
                                            info = ParameterInfo(param_data_type_block, param_data_type,param_identifier_block,param_identifier,param_value, param_code)
                                            param_list.append(info)

                                            # print(f"Param List: {param_list}") # Debug print
                                                
                                            #clearing values for the next parameter if there's any
                                            param_code=""
                                            is_param_processing=False
                                            param_data_type=""
                                            param_data_type_block=""
                                            param_identifier_block=""
                                            param_identifier=""
                                            param_code =""
                                            param_value=None
 
                                    
                                    if is_array_processing:
                                        if current_element=="<data_type>":
                                            array_data_type=str_item
                                        if current_element=="<array_size>":    
                                            array_length= int(str_item)
                                        if current_element=="<identifier>":
                                            array_identifier=str_item

                                    if is_var_declaration_processing:
                                        if current_element=="<data_type>":
                                            var_data_type=str_item

                                    if is_recursive_function:
                                        if current_element=="<function_name>":
                                            if original_function_name_processed:
                                               str_item=recursive_function_name
                                            else:   
                                                recursive_function_name=str_item
                                                original_function_name_processed =True       



                                    stack.append((str_item, True, indent_level, local_visited, rule_node))


                            elif list_type == Constants.MULTIPLE_STRING_LIST:
                                inner_list = item[0]
                                for inner_item in reversed(inner_list):
                                    str_item = str(inner_item)
                                    # print(f"String item: {str_item}")  # Debug print
                                    if str_item.startswith('<') and str_item.endswith('>'):
                                        if str_item =="<rand_strings>":
                                            str_item=grammar_parser_utils.process_rand_string()
                                            stack.append((str_item, True, indent_level, set(), rule_node))
                                        elif str_item =="<rand_array_values>":
                                            str_item,iterative_data_loop= grammar_parser_utils.generate_array_data(array_data_type,array_identifier,array_length,self.grammar)
                                            array_loop=iterative_data_loop
                                            
                                            stack.append((str_item, True, indent_level, set(), rule_node))
                                        elif is_var_declaration_processing and str_item =="<rand_var_values>":
                                            str_item = grammar_parser_utils.process_variable_data_type(var_data_type,self.grammar)
                                            stack.append((str_item, True, indent_level, set(), rule_node))     
                                        else:    
                                         stack.append((str_item, False, indent_level, set(), rule_node))
                                    else:

                                        if is_function and current_element == "<return_type>":
                                            current_return_type = str_item

                                            #adding parameters of the function to the list, to be used in the function call
                                        if is_param_function and is_param_processing:
                                            if current_element == "<data_type>":
                                                param_code += f"{str_item} "
                                                param_data_type_block=current_element
                                                param_data_type=str_item
                                                param_value=grammar_parser_utils.process_param_values(param_data_type)
                                                # print(f"Current data type: {str_item}") # Debug print
                                            elif current_element == "<identifier_parameter>":
                                                param_code+=f"{str_item}"
                                                param_identifier_block=current_element
                                                param_identifier=str_item
                                                # print(f"Current identifier: {str_item}") 

                                                    
                                                info = ParameterInfo(param_data_type_block, param_data_type,param_identifier_block,param_identifier,param_value, param_code)
                                                param_list.append(info)
                                                # print(f"Param List: {param_list}") # Debug print
                                                    
                                                #clearing values for the next parameter if there's any
                                                param_code=""
                                                is_param_processing=False
                                                param_data_type=""
                                                param_data_type_block=""
                                                param_identifier_block=""
                                                param_identifier=""
                                                param_code =""
                                                param_value=None
 
                                        if is_array_processing:
                                            if current_element=="<data_type>":
                                                array_data_type=str_item
                                            if current_element=="<array_size>":    
                                                array_length= int(str_item) 
                                            if current_element=="<identifier>":
                                                array_identifier=str_item
                                        
                                        if is_var_declaration_processing:
                                            if current_element=="<data_type>":
                                                var_data_type=str_item


                                        if is_recursive_function:
                                            if current_element=="<function_name>":
                                                if original_function_name_processed:
                                                    str_item=recursive_function_name
                                                else:   
                                                    recursive_function_name=str_item
                                                    original_function_name_processed =True    

                                        stack.append((str_item, True, indent_level, local_visited, rule_node))
                            else:
                                print(f"{current_element} not found.")
                    else:
                        print(f"{current_element} not found.")

        flush_line()  # Ensure any remaining content is written
        # print(f"Final code:\n{code}")  # Debug print
        # print(f"AST structure: {self.ast_to_list(root)}")  # Debug print


        return code, grammar_parser_utils.ast_to_list(root),param_list,is_param_function,is_recursive_function

def generate_code():
    folder_path = 'Grammar/Program_Constructs'
    parser = GrammarParserAst(folder_path)
    
    # print(parser.grammar)
    
    # print("Grammar:")
    # for index, grammar_item in enumerate(parser.grammar):
    #     print(f"{index}: {grammar_item}")
    # print("\n")

    # Generate code and get AST as tree
    # element='<function_parameterised_multi>'
    # element='<var_declaration>'
    # element='<array>'
    # element='<print_statement>'
    # element='<while_loop_conditional>'
    # element='<function_recursive>'
    # element='<do_while_loop>'
    element='<for_loop>'
    code, ast_tree, param_list,is_param_function,is_recursive_function = parser.generate_code(element)
    print("Generated Code:")
    print(code)

    # print("AST Tree:")
    # print(ast_tree) #print ast tree without processing

    # print("Param List:")
    # print(param_list)

    # for item in param_list:
    #     print(f"Data Type Block: {item.data_type_block}")
    #     print(f"Data Type: {item.data_type_value}")
    #     print(f"Identifier Block: {item.identifier_block}") 
    #     print(f"Identifier: {item.identifier_value}")
    #     print(f"Value: {item.data_value}")
    #     print(f"Param Code: {item.param_code}")
    #     print   ("\n")

    # print("Is Param Function:")
    # print(is_param_function)

    # print("Processed AST Tree:")
    # ast_utils.print_ast_tree(ast_tree)

    # print("Saving AST Tree:")
    # ast_utils.save_ast(ast_tree,element)
    
    # print("Saving AST Tree as JSON:")
    # ast_utils.save_ast_as_json(ast_tree,element)


#python3 -m Grammar_Parser.parser_ast
if __name__ == "__main__":
    generate_code()