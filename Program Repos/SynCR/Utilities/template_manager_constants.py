from typing import Final

class TemplateManagerConstants:
    MODEL_TEMPLATE: Final[str] ="""#include <iostream> \n using namespace std; \n {{FUNCTIONS}} \n int main() { \n {{MAIN_BODY}} \n return 0; \n}"""
    FUNCTION_KEYS: Final[str] =['FUNCTION_DEFINITION_NON_PARAM','FUNCTION_DEFINITION','FUNCTION_DEFINITION_PARAM']
    EXCLUDE_LIST: Final[str] =['FUNCTION_DEFINITION_NON_PARAM','FUNCTION_DEFINITION','FUNCTION_DEFINITION_PARAM','FUNCTION_DEFINITION_RECURSIVE','INCLUDES']
    