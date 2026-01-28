import random
import string
from Grammar_Parser.parser_common import GrammarParser
from Grammar_Parser.code_element import CodeElement
import re
from Utilities.utils import Constants, differentiate_list_type, format_code_element

class GrammarParserImpl(GrammarParser):

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            super().__init__(file_path)
            self.initialized = True

    def parse(self):
        for lhs, rhs in self.grammar.items():
            self.rules[lhs.strip('<>')] = rhs

        for key, value in self.rules.items():
            for sublist in value:
                for item in sublist:
                    if item.startswith('<') and item.endswith('>'):
                        print(item)

                        key_check = item[1:-1]

                        grammarPath = f"Grammar/Program_Constructs/{key_check}.bnf"
                        grammar = self.read_bnf_grammar(grammarPath)

                        print(grammar)

    def generate_code(self, element):
        stack = [(element, False, 0, set())]  # (element, is_processed, indentation_level, local_visited)
        code = ""
        generated_code_list = []

        while stack:
            current_element, is_processed, indent_level, local_visited = stack.pop()

            if is_processed:
                code += format_code_element(current_element.element, indent_level)
                generated_code_list.append(current_element)
            else:
                if current_element in local_visited:
                    continue
                local_visited.add(current_element)

                if not any(current_element in d for d in self.grammar):
                    code += current_element
                else:
                    element_data = [d[current_element] for d in self.grammar if current_element in d]
                    if element_data:
                        for item in element_data:
                            list_type = differentiate_list_type(item)
                            if list_type == Constants.SINGLE_STRING_LIST:
                                str_item = str(random.choice(item)[0])
                                if str_item.startswith('<') and str_item.endswith('>'):
                                    stack.append((str_item, False, indent_level + 1, set()))
                                else:
                                    code_element = CodeElement(
                                        element=str_item,
                                        grammar_rule=current_element, 
                                        variable_name=None,  
                                        value=None 
                                    )
                                    stack.append((code_element, True, indent_level, local_visited))
                            elif list_type == Constants.MULTIPLE_STRING_LIST:
                                inner_list = item[0]
                                for inner_item in reversed(inner_list):
                                    str_item = str(inner_item)
                                    if str_item.startswith('<') and str_item.endswith('>'):
                                        stack.append((str_item, False, indent_level, set()))
                                    else:
                                        code_element = CodeElement(
                                            element=str_item,
                                            grammar_rule=current_element,
                                            variable_name=None, 
                                            value=None 
                                        )
                                        stack.append((code_element, True, indent_level, local_visited))
                            else:
                                print(f"{current_element} not found.")
                    else:
                        print(f"{current_element} not found.")

        # print(f"Generated code list: {[str(elem) for elem in generated_code_list]}")
        # print()
        # print(f"Generated code: {code}")
        return code, generated_code_list

# def generate_code():
#     folder_path = 'Grammar/Program_Constructs'
#     parser = GrammarParserImpl(folder_path)
#     code, generated_code_list = parser.generate_code('<if_statement>')
#     print(code)
#     for elem in generated_code_list:
#         parent_element = elem.parent.element if elem.parent else None
#         children_elements = [child.element for child in elem.children]
#         print(f"Code Element: {elem.element}, Grammar Rule: {elem.grammar_rule}, Parent: {parent_element}, Children: {children_elements}")

# generate_code()