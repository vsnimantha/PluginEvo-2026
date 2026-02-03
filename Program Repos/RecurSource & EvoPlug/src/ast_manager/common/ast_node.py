class ASTNode:
    def __init__(self, kind, spelling="", children=None, token_value=None, type_name=None):
        self.kind = kind                   # e.g., "BINARY_OPERATOR", etc.
        self.spelling = spelling           # for names, or operator symbol
        self.children = children or []
        self.token_value = token_value     # literal values
        self.type_name = type_name         # for VAR_DECL, PARAMs, etc.
        for child in self.children:
            child.parent = self

    def __repr__(self):
        return f"ASTNode({self.kind}, spelling={repr(self.spelling)}, children={len(self.children)})"