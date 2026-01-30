import random
import string
from functools import singledispatchmethod
from Grammar_Parser.parser_common import GrammarParser
from Grammar_Parser.ast_node import ASTNode
from Grammar_Parser.parameter_info import ParameterInfo
from Utilities.utils import Constants, differentiate_list_type
import Utilities.ast_utils as ast_utils
import Utilities.grammar_parser_utils as grammar_parser_utils
from Config.global_config import config
import json
# import pandas as pd

# from Grammar_Parser.code_generator import CodeGenerator
from Grammar_Parser.Smart_Code_Generation.smart_code_generator import SmartCodeGenerator
# from typing import Dict, Any, List, Union


class GrammarParserAstAllCombi(GrammarParser):

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            super().__init__(file_path)
            self.initialized = True
            self.visited=set()

    def parse(self):
        pass

    def get_grammar_structure(self, element):
        """
        Generates a structured breakdown of all possible expansions for a grammar element
        Returns: Dictionary showing the hierarchy of possible expansions
        """
        if not any(element in d for d in self.grammar):
            return element  # Terminal case

        structure = {
            'element': element,
            'expansions': []
        }

        # Get all production rules for this element
        element_data = [d[element] for d in self.grammar if element in d]
        if not element_data:
            return structure

        for item in element_data:
            list_type = differentiate_list_type(item)
            # print(f"List type: {list_type}")  # Debug print
            if list_type == Constants.UNKNOWN_LIST:
                print(f"Unknown list type for item: {item}")
                continue
            
            if list_type == Constants.SINGLE_STRING_LIST:
                # Handle alternatives (OR cases)
                for option in item:
                    str_item = str(option[0])
                    if str_item.startswith('<') and str_item.endswith('>'):
                        # Non-terminal - add as sub-element
                        sub_structure = self.get_grammar_structure(str_item)
                        structure['expansions'].append(sub_structure)
                    else:
                        # Terminal - add directly
                        structure['expansions'].append(str_item)
            
            elif list_type == Constants.MULTIPLE_STRING_LIST:
                # Handle sequences (AND cases)
                sequence_group = {
                    'type': 'sequence',
                    'elements': []
                }
                
                for inner_item in item[0]:  # item[0] contains the sequence
                    str_item = str(inner_item)
                    if str_item.startswith('<') and str_item.endswith('>'):
                        # Non-terminal - add as sub-element
                        sub_structure = self.get_grammar_structure(str_item)
                        sequence_group['elements'].append(sub_structure)
                    else:
                        # Terminal - add directly
                        sequence_group['elements'].append(str_item)
                
                structure['expansions'].append(sequence_group)

        return structure
    
    def _generate_possible_combinations(self, structure):
        """
        Returns the structure of possible combinations without generating actual strings
        Output format: {'element': ..., 'possible_combinations': [...]}
        """
        if isinstance(structure, str):
            return {
                'element': structure,
                'possible_combinations': [structure]
            }
        
        result = {
            'element': structure.get('element', ''),
            'possible_combinations': []
        }
        
        for expansion in structure['expansions']:
            if isinstance(expansion, dict):
                if expansion.get('type') == 'sequence':
                    # For sequences, we need to combine all elements
                    sequence_combinations = []
                    for elem in expansion['elements']:
                        elem_result = self._generate_possible_combinations(elem)
                        sequence_combinations.append(elem_result)
                    
                    # Store the sequence structure rather than generating products
                    result['possible_combinations'].append({
                        'type': 'sequence',
                        'elements': sequence_combinations,
                        'description': f"Sequence of {len(sequence_combinations)} elements"
                    })
                else:
                    # For normal expansions, just add the possible sub-combinations
                    sub_result = self._generate_possible_combinations(expansion)
                    result['possible_combinations'].append(sub_result)
            else:
                # Terminal value
                result['possible_combinations'].append({
                    'element': 'terminal',
                    'value': expansion
                })
        
        return result
    
    def get_possible_combinations(self,element):
        structure = self.get_grammar_structure(element)
        return self._generate_possible_combinations(structure)

    def generate_all_combinations(self, element):
        """
        Generates all possible concrete combinations from the grammar structure
        Returns: List of all possible valid strings
        """
        structure = self.get_grammar_structure(element)
        return self._generate_from_structure(structure)

    def count_possible_combinations(self, element):
        """Counts how many total possible combinations exist for an element"""
        structure = self.get_grammar_structure(element)
        return self._count_combinations(structure)

    def _count_combinations(self, structure):
        # Base case: terminal symbol
        if isinstance(structure, str):
            return 1
        
        # Invalid structure case
        if not isinstance(structure, dict):
            return 0
        
        # Handle different grammar rule types
        if 'expansions' in structure:
            # Sum all possible expansions (OR logic)
            total = 0
            for expansion in structure['expansions']:
                if isinstance(expansion, dict) and expansion.get('type') == 'sequence':
                    # Multiply sequence elements (AND logic)
                    seq_count = 1
                    for elem in expansion.get('elements', []):
                        seq_count *= self._count_combinations(elem)
                    total += seq_count
                else:
                    # Add non-sequence expansions
                    total += self._count_combinations(expansion)
            return total
        
        # Handle direct sequences
        if structure.get('type') == 'sequence':
            count = 1
            for elem in structure.get('elements', []):
                count *= self._count_combinations(elem)
            return count
        
        # Handle leaf nodes with direct elements
        if 'element' in structure:
            return self._count_combinations(structure.get('expansions', 1))
        
        # Default case for other structures
        return 1

    def _generate_from_structure(self, structure):
        """Recursive helper to generate combinations from structure"""
        if isinstance(structure, str):
            return [structure]
            
        all_combinations = []
        
        for expansion in structure['expansions']:
            if isinstance(expansion, dict):
                if expansion.get('type') == 'sequence':
                    # Handle sequences (AND logic - combine all elements)
                    sequence_parts = []
                    for elem in expansion['elements']:
                        elem_combos = self._generate_from_structure(elem)
                        sequence_parts.append(elem_combos)
                    
                    # Generate Cartesian product of all sequence parts
                    from itertools import product
                    for combo in product(*sequence_parts):
                        all_combinations.append(' '.join(combo))
                else:
                    # Handle normal expansions (OR logic)
                    sub_combos = self._generate_from_structure(expansion)
                    all_combinations.extend(sub_combos)
            else:
                # Terminal value
                all_combinations.append(expansion)
                
        return all_combinations

    def generate_code(self, element:str):
        root = ASTNode("root",element)
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
                elif current_element == "=":
                    if is_var_declaration_processing:
                        if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and var_data_type=="string":
                            current_element = f"[] {current_element}"

                    current_line += current_element
                else:
                    if not current_line and current_element in ["if", "else", "for", "while"]:
                        flush_line(True)
                    # print(f"Current terminal element: {current_element}")  # Debug print            
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
                    elif current_element == "=":
                        if is_var_declaration_processing:
                            if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and var_data_type=="string":
                                current_element = f"[] {current_element}"

                        current_line += current_element
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
                                    elif is_array_processing and str_item=="<rand>":
                                        str_item=grammar_parser_utils.process_random_data_values("int")
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
                                            if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and str_item=="string":
                                                str_item=str_item.replace("string","char")
                                            array_data_type=str_item
                                        if current_element=="<array_size>":    
                                            array_length= int(str_item)
                                        if current_element=="<identifier>":
                                            array_identifier=str_item

                                    if is_var_declaration_processing:
                                        if current_element=="<data_type>":
                                            var_data_type=str_item
                                            if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and str_item=="string":
                                                str_item=str_item.replace("string","char")

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
                                        elif is_array_processing and str_item=="<rand>":
                                            str_item=grammar_parser_utils.process_random_data_values("int")
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
                                                if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and str_item=="string":
                                                    str_item=str_item.replace("string","char")
                                                array_data_type=str_item
                                            if current_element=="<array_size>":    
                                                array_length= int(str_item) 
                                            if current_element=="<identifier>":
                                                array_identifier=str_item
                                        
                                        if is_var_declaration_processing:
                                            if current_element=="<data_type>":
                                                var_data_type=str_item

                                            if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and str_item=="string":
                                                    str_item=str_item.replace("string","char")

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


    def generate_code_multi(self, element:str,element_count:int=10):
        
        possible_combinations_json=self.get_possible_combinations(element)

        # print(f"Possible Combinations \n {possible_combinations_json}") #Debug print

        pretty_json= json.dumps(possible_combinations_json,indent=4,sort_keys=True)

        # print(f"Pretty Json \n {pretty_json}") #Debug print

        grammar_json = json.loads(pretty_json)

        # print(f"Grammar Json \n {grammar_json}") #Debug print

        generator = SmartCodeGenerator(self.grammar, grammar_json)
        declarations = generator.generate(element_count)

        # print(f"Declarations \n {declarations}") #Debug print

        return declarations
    
def generate_code():
    folder_path = 'Grammar/Program_Constructs_C'
    # folder_path = 'Grammar/Program_Constructs_CPP'
    parser = GrammarParserAstAllCombi(folder_path)
    
    # print(parser.grammar)
    
    # print("Grammar:")
    # for index, grammar_item in enumerate(parser.grammar):
    #     print(f"{index}: {grammar_item}")
    # print("\n")

    # Generate code and get AST as tree
    # element='<function_parameterised_multi>'
    # element='<function_parameterised_multi>'
    # element='<var_declaration>'
    # element='<array>'
    # element='<print_statement>'
    # element='<function_recursive>'
    # element='<do_while_loop>'
    # element='<for_loop>'
    # element='<while_loop>'
    # element="<data_type>"
    element="<if_statement>"
    # element="<data_type>"
    # element="<switch_statement>"

    # print(parser.get_grammar_structure(element))


    # Single combination based

    print("Generated Code:")
    result = parser.generate_code(element)
    if len(result) == 5:  # Check if it matches expected count
        code, ast_tree, param_list, is_param_function, is_recursive_function = result
        print(code)
    else:
        # Handle incorrect return structure
        print(f"Unexpected return format: {result}")
        

    # Combination based

    # print(f"Number of possible combinations {parser.count_possible_combinations(element)}")
    # print()
    # print("Possible combinations..........")
    # generated_combinations=parser.generate_code_multi(element,1)
    # print("Smart Grammar:")
    # for i, decl in enumerate(generated_combinations, 1):
    #     # Each 'decl' is already the tuple (generated_code, ast_list, param_list, is_param_function, is_recursive_function)
    #     generated_code, ast_list, param_list, is_param_function, is_recursive_function = decl
        
    #     print(f"\nDeclaration {i}:")
    #     print("Generated Code:")
    #     print(generated_code)
        
        # print("\nAST Structure:")
        # print(ast_list)
        
        # print("\nParameters:")
        # for param in param_list:
        #     print(param)
        
        # print(f"\nIs Parameterised Function: {is_param_function}")
        # print(f"Is Recursive Function: {is_recursive_function}")
        # print("-" * 50)



    #Other Experimented Methods


    # longest_paths = parser.get_longest_paths(pretty_json)
    # print(longest_paths)

    # print("Generated code combinations..........")
    # combinations=parser.generate_representative_samples(parser.get_grammar_structure(element))

    # for item in combinations:
    #     print(f"Combination: {item}\n")

    # print(combinations)

    # grammar_node=parser._generate_possible_combinations(parser.get_grammar_structure(element))




    # print(parser.get_representative_samples())
    # print(parser._generate_possible_combinations(parser.get_grammar_structure(element)))
    # possible_combinations=parser._generate_possible_combinations(parser.get_grammar_structure(element))
    # parser.print_all_combinations(element)

    # print(json.dumps(possible_combinations, indent=2))

    # all_while_loops = parser.generate_all_combinations('<while_loop>')
    # print(f"Found {len(all_while_loops)} combinations:")
    # for i, combo in enumerate(all_while_loops[:10]):  # Print first 10
    #     print(f"{i+1}. {combo}")

    # Or get all combinations as a list
    # all_combinations = parser.generate_all_combinations(element)
    # print(all_combinations)


    # generator = CodeGenerator(grammar)
    
    # declarations = generator.generate(10)
    # print(declarations)
    # for i, decl in enumerate(declarations, 1):
    #     print(f"{i}. {decl}")


    

#python3 -m Grammar_Parser.parser_ast_all_combinations
if __name__ == "__main__":
    generate_code()