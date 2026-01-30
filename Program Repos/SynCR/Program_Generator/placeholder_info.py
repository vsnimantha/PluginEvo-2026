class PlaceholderInfo:
    def __init__(self, placeholder_block,placeholder, unique_id, grammar_rule, generated_code, ast_tree=None,parameters=[],is_parameterised=False,is_recursive_function=False,name=None):
        self.placeholder_block = placeholder_block
        self.placeholder = placeholder
        self.unique_id = unique_id
        self.name = name
        self.grammar_rule = grammar_rule
        self.generated_code = generated_code
        self.ast_tree = ast_tree
        self.parameters = parameters
        self.is_parameterised=is_parameterised
        self.recursive_function=is_recursive_function

    def __repr__(self):
        return f"PlaceholderInfo(placeholder={self.placeholder}, unique_id={self.unique_id}, grammar_rule={self.grammar_rule}, is_recursive={self.recursive_function})"