from Utilities.constants import Constants
import random
import os
import re
import uuid

# def differentiate_list_type(nested_list):
#     """
#     Differentiate between a list of lists containing single strings and a list containing a single list with multiple strings.
#     Returns 'single_string_list' for the first type and 'multiple_string_list' for the second type.
#     """
#     if all(isinstance(sublist, list) and len(sublist) == 1 and isinstance(sublist[0], str) for sublist in nested_list):
#         return Constants.SINGLE_STRING_LIST
#     elif len(nested_list) == 1 and all(isinstance(item, str) for item in nested_list[0]):
#         return Constants.MULTIPLE_STRING_LIST
#     else:
#         return Constants.UNKNOWN_LIST

def differentiate_list_type(nested_list):
    """
    Differentiate between:
    1. A list of lists containing single strings (single_string_list).
    2. A list containing a single list with multiple strings (multiple_string_list).
    3. A list of lists where some sublists contain multiple strings (mixed_list).
    """
    # Check if it's a single string list
    if all(isinstance(sublist, list) and len(sublist) == 1 and isinstance(sublist[0], str) for sublist in nested_list):
        return Constants.SINGLE_STRING_LIST
    
    # Check if it's a multiple string list
    elif len(nested_list) == 1 and all(isinstance(item, str) for item in nested_list[0]):
        return Constants.MULTIPLE_STRING_LIST
    
    # Check if it's a mixed list (some sublists have multiple strings)
    elif all(isinstance(sublist, list) and all(isinstance(item, str) for item in sublist) for sublist in nested_list):
        return Constants.MIXED_LIST
    
    else:
        return Constants.UNKNOWN_LIST

def extract_function_metadata(generated_code):
    """
    Extracts the function name and function definition from the generated code.
    """
    # Regex to match function definitions (e.g., "float alphaFunc() { ... }")
    function_pattern = re.compile(r"(\w+\s+\w+\(.*?\))\s*\{")
    match = function_pattern.search(generated_code)
    if match:
        function_definition = match.group(1)  # e.g., "float alphaFunc()"
        function_name = function_definition.split()[1].split("(")[0]  # e.g., "alphaFunc"
        return function_name, function_definition
    return None, None
    
def extract_template_placeholders(template_content):
    pattern = re.compile(r'\{\{(.*?)\}\}')
    components = pattern.findall(template_content)
    return components

def format_code_element(element, indent_level):
    """
    Formats a code element with proper indentation and line breaks.
    """
    indent = " " * indent_level
    if element == "{":
        return " {\n" + indent
    elif element == "}":
        return "\n" + indent + "}\n"
    elif element.endswith(";"):
        return indent + element.strip() + "\n"
    elif element in ("(", ")"):
        return element  # No extra spaces around parentheses
    elif element.strip() in ("while", "if", "for"):
        return " " + element.strip() + " "  # Handle control statements
    elif element.strip() in ("double", "int", "boolean", "float", "std::cout<<"):
        return element.strip() + " "
    else:
        return indent + element.strip()  # Indent other elements and remove excess spaces

def read_files_from_folder(folder_path, file_extension=None):
        file_contents = []
        
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' does not exist.")
            return {}

        try:
            for filename in os.listdir(folder_path):
                # print(filename)
                if file_extension is not None and not filename.endswith(file_extension):
                    continue 

                file_path = os.path.join(folder_path, filename)

        except Exception as e:
            print(f"Error listing directory '{folder_path}': {e}")
 
def generate_unique_id():
    """
    Generates a unique identifier using UUID.
    """
    return str(uuid.uuid4())[:8]  # Using first 8 characters of a UUID

def is_function(identifier):
    """
    Checks if the given identifier is a function.
    """
    return identifier.startswith("fid")

def extract_parameter_references(params):
    """
    Extracts the parameter references from the given list of parameters.
    """
    pattern = r'\[\[(.*?)\]\]'

    match = re.search(pattern, params)
    if match:
        extracted = match.group(1)
        return extracted
    return None

# # Examples
# list1 = [['alpha'], ['beta'], ['gamma'], ['delta']]
# list2 = [['while', '(', '<boolean_literal>', ')', '{', '<statement>', '}']]

# print(differentiate_list_type(list1))  # Output: single_string_list
# print(differentiate_list_type(list2))  # Output: multiple_string_list
