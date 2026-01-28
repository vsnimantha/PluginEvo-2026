from enum import Enum

class ConstructType(Enum):
    IF = 1
    VAR = 2
    WHILE = 3
    FOR = 4
    FUNCTION = 5
    EXPRESSION = 6
    BLOCK_START = 7
    BLOCK_END = 8
    UNDEFINED = 9