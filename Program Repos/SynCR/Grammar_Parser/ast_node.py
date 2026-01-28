class ASTNode:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value})"
