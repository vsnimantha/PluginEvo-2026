import uuid

class CodeElement:
    def __init__(self, element, grammar_rule=None, variable_name=None, value=None, parent=None):
        self.id = uuid.uuid4()  # Unique identifier for the element
        self.element = element  # The actual code element (e.g., "float beta = 1;")
        self.grammar_rule = grammar_rule  # The grammar rule it belongs to (e.g., "<var_declaration>")
        self.variable_name = variable_name  # The variable name (e.g., "beta")
        self.value = value  # The value assigned to the variable (e.g., "1")
        self.parent = parent  # The parent element (e.g., a function or block)
        self.children = []  # List to store child elements
        self.local_visited = set()  # Set to track visited elements

    def __str__(self):
        return self.element

    def add_child(self, child_element):
        """
        Adds a child element to this element.
        """
        child_element.parent = self
        self.children.append(child_element)

    def belongs_to(self, parent_element):
        """
        Checks if this element belongs to the given parent element.
        """
        current_element = self
        while current_element:
            if current_element == parent_element:
                return True
            current_element = current_element.parent
        return False