from typing import Final

precedence : Final = {
    "=": 2, "+=": 2, "-=": 2, "*=": 2, "/=": 2, "%=": 2,
    "<<=": 2, ">>=": 2, "&=": 2, "^=": 2, "|=": 2,
    "||": 3,
    "&&": 4,
    "|": 5,
    "^": 6,
    "&": 7,
    "==": 8, "!=": 8,
    "<": 9, ">": 9, "<=": 9, ">=": 9,
    "<<": 10, ">>": 10,
    "+": 11, "-": 11,
    "*": 12, "/": 12, "%": 12,
    ",": 1,
}


binary_operators: Final = {
    "operator+": "+",
    "operator-": "-",
    "operator*": "*",
    "operator/": "/",
    "operator%": "%",       # <-- missing modulo
    "operator==": "==",
    "operator!=": "!=",
    "operator<": "<",
    "operator>": ">",
    "operator<=": "<=",
    "operator>=": ">=",
}


implicit_ops: Final = {'operator bool', 'operator int', 'operator double'}




