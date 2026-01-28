import random
import string
from Utilities.utils import Constants, differentiate_list_type


def process_variable_data_type(variable_data_type, grammar):
    grammar_element = f'<value_{variable_data_type}>'
    element_data = [d[grammar_element] for d in grammar if grammar_element in d]

    data = process_element_data(element_data)

    return_data = None
    if data == '<rand>':
        if variable_data_type == 'int':
            return_data = str(random.randint(0, 100))
        elif variable_data_type == 'float':
            return_data = f'{random.uniform(0, 100)}f'
        elif variable_data_type == 'string':
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            return_data=f'"{str(random_string)}"'
        elif variable_data_type == 'char':
            random_char = random.choice(string.ascii_uppercase)
            return_data=f"'{random_char}'"
        elif variable_data_type == 'bool':
            return_data = random.choice(['true', 'false'])
        elif variable_data_type == 'double':
            return_data = str(random.uniform(0, 100))
        else:
            return_data = None
    else:
        return_data = data
    return return_data

def process_return_type(return_type, grammar):
    grammar_element = f'<function_return_{return_type}>'
    element_data = [d[grammar_element] for d in grammar if grammar_element in d]

    data = process_element_data(element_data)
    return_data = None
    if data == '<rand>':
        if return_type == 'int':
            return_data = str(random.randint(0, 100))
        elif return_type == 'float':
            return_data = f'{random.uniform(0, 100)}f'
        elif return_type == 'string':
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            return_data=f'"{str(random_string)}"'
        elif return_type == 'char':
            random_char = random.choice(string.ascii_uppercase)
            return_data=f"'{random_char}'"
        elif return_type == 'bool':
            return_data = random.choice(['true', 'false'])
        elif return_type == 'double':
            return_data = str(random.uniform(0, 100))
        else:
            return_data = None
    else:
        return_data = data
    return return_data

def process_rand_string():
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    return_data=f'"{random_str}"'

    return return_data

def process_param_values(param_data_type):
    return_data = None
    if param_data_type == 'int':
        return_data = str(random.randint(0, 100))
    elif param_data_type == 'float':
        return_data = f'{random.uniform(0, 100)}f'
    elif param_data_type == 'string':
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return_data=f'"{str(random_string)}"'
    elif param_data_type == 'char':
        random_char = random.choice(string.ascii_uppercase)
        return_data=f"'{random_char}'"
    elif param_data_type == 'bool':
        return_data = random.choice(['true', 'false'])
    elif param_data_type == 'double':
        return_data = str(random.uniform(0, 100))
    else:
        return_data = None

    return return_data

def process_element_data(element_data):
    if element_data:
        for item in element_data:
            list_type = differentiate_list_type(item)
            if list_type == Constants.SINGLE_STRING_LIST:
                str_item = str(random.choice(item)[0])
                return str_item
            elif list_type == Constants.MULTIPLE_STRING_LIST:
                inner_list = item[0]
                for inner_item in reversed(inner_list):
                    str_item = str(inner_item)
                    return str_item
            else:
                print(f"{element_data} not found.")
    else:
        print(f"{element_data} not found.")

def process_element_data_for_strings(element_data, message=None):
    if element_data:
        for item in element_data:
            list_type = differentiate_list_type(item)
            if list_type == Constants.SINGLE_STRING_LIST:
                str_item = str(random.choice(item)[0])
                return str_item
            elif list_type == Constants.MULTIPLE_STRING_LIST:
                inner_list = item[0]
                # Join all parts and replace <message> placeholder
                result = ''.join(str(inner_item) for inner_item in inner_list)
                if message is not None:
                    result = result.replace('<message>', str(message))
                return result
            else:
                print(f"{element_data} not found.")
    else:
        print(f"{element_data} not found.")
    return ""  # Return empty string if no data found

def process_element_data_for_array(element_data,array_length,identifier,grammar):
    if element_data:
        for item in element_data:
            list_type = differentiate_list_type(item)
            if list_type == Constants.SINGLE_STRING_LIST:
                str_item = str(random.choice(item)[0])
                return str_item
            elif list_type == Constants.MULTIPLE_STRING_LIST:
                inner_list = item[0]
                result=""
                for inner_item in inner_list:
                    if inner_item=="<for_loop_initialization>":
                        result+="int i=0;"
                    elif inner_item=="<for_loop_condition>":
                        result+=f"i<{array_length};"
                    elif inner_item=="<for_loop_update>":
                        result+=f"i++"
                    elif inner_item=="<for_loop_body>":
                        grammar_element = '<print_statement>'
                        element_data = [d[grammar_element] for d in grammar if grammar_element in d]
                        processed_element = process_element_data_for_strings(element_data,f"{identifier}[i]")
                        result+= processed_element
                    else:
                        result+=inner_item
                    

                # Join all parts and replace <message> placeholder
                # result = ''.join(str(inner_item) for inner_item in inner_list)
                return result
            else:
                print(f"{element_data} not found.")
    else:
        print(f"{element_data} not found.")
    return ""  # Return empty string if no data found

def ast_to_list(node):
    result = [node.type, node.value]
    for child in node.children:
        result.append(ast_to_list(child))
    return result

import random


import random

def check_duplicate_params(param_list, str_item, available_param_names):
    """Check for duplicate parameter names and return a unique name from available options.
    
    Args:
        param_list: List of ParameterInfo objects
        str_item: Parameter name to check (string)
        available_param_names: List of allowed parameter names (must be strings or convertable to strings)
        
    Returns:
        Original name if not duplicate, or a new unique name from available options
        
    Raises:
        ValueError: If no available names remain
    """
    # Safely collect existing names
    existing_names = set()
    for item in param_list:
        try:
            if hasattr(item, 'identifier_value'):
                existing_names.add(str(item.identifier_value))
        except (AttributeError, TypeError):
            continue

    # Ensure the input name is a string
    try:
        str_item = str(str_item)
    except:
        str_item = "param"

    # Check if current name is a duplicate
    if str_item in existing_names:
        # Convert all available names to strings and filter out non-strings
        usable_names = []
        for name in available_param_names:
            try:
                usable_names.append(str(name[0]))
            except:
                continue
        
        if not usable_names:
            raise ValueError("No valid parameter names available in the provided list")
            
        # Get unused names that are in our available list
        unused_names = [name for name in usable_names 
                       if name not in existing_names]
        
        if not unused_names:
            raise ValueError(f"No available parameter names remaining. All {len(usable_names)} options are used.")
        
        # print(f"Unused param names {unused_names}") #Debug print
        new_name = random.choice(unused_names)
        print(f"Renamed duplicate parameter '{str_item}' to '{new_name}'")
        return new_name
    
    return str_item

def process_params_data(param_list, grammar):
    print_statements = []
    math_equation = ""
    first_num_param = True  # Flag to track first numerical parameter
    
    for item in param_list:
        if item.data_type_value in ["int", "double", "float"]:
            if not first_num_param:
                # Only add math operation if this isn't the first numerical param
                grammar_element = '<math_operation>'
                element_data = [d[grammar_element] for d in grammar if grammar_element in d]
                math_operation = process_element_data(element_data)
                math_equation += f" {math_operation} "
            
            math_equation += item.identifier_value
            first_num_param = False
            
        elif item.data_type_value == "bool":
            grammar_element = '<print_statement>'
            element_data = [d[grammar_element] for d in grammar if grammar_element in d]
            processed_element = process_element_data_for_strings(element_data,item.identifier_value)
            print_statements.append(processed_element)
        elif item.data_type_value == "string":
            grammar_element = '<print_statement>'
            element_data = [d[grammar_element] for d in grammar if grammar_element in d]
            processed_element = process_element_data_for_strings(element_data,item.identifier_value)
            print_statements.append(processed_element)
        else:
            print("Data type is not supported yet")


    if math_equation!="":
        grammar_element = '<print_statement>'
        element_data = [d[grammar_element] for d in grammar if grammar_element in d]
        processed_element = process_element_data_for_strings(element_data,math_equation)
        print_statements.append(processed_element)

    return print_statements,math_equation


def generate_array_data(data_type, identifier,length,grammar):
    data_array = []

    for _ in range(length):
        random_data=process_variable_data_type(data_type,grammar)
        if random_data is not None:
            data_array.append(random_data)       

    grammar_element = '<for_loop>'
    element_data = [d[grammar_element] for d in grammar if grammar_element in d]
    iterative_data_loop = process_element_data_for_array(element_data,length,identifier,grammar)
    
    # print(f"Generate for loop: {iterative_data_loop}") #Debug Print

    # Join the array into a single string with proper formatting
    return f"{{{','.join(data_array)}}}",iterative_data_loop
