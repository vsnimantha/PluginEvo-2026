import random
import clang.cindex
from ast_parser import ASTParser  # Your existing parser with working parse()

# === Mutable AST node class ===
class ASTNode:
    def __init__(self, kind, spelling, children=None, type_spelling=None, return_type_spelling=None):
        self.kind = kind
        self.spelling = spelling
        self.children = children if children is not None else []
        self.parent = None
        self.type_spelling = type_spelling
        self.return_type_spelling = return_type_spelling
        for child in self.children:
            child.parent = self

    def __repr__(self):
        type_info = f", type='{self.type_spelling}'" if self.type_spelling else ""
        ret_info = f", return_type='{self.return_type_spelling}'" if self.return_type_spelling else ""
        kind_name = self.kind.name if hasattr(self.kind, 'name') else str(self.kind)
        return f"ASTNode({kind_name}, '{self.spelling}'{type_info}{ret_info})"

# Container cursor kinds that have empty spelling by design (do not include FUNCTION_DECL here)
CONTAINER_KINDS = {
    clang.cindex.CursorKind.TRANSLATION_UNIT,
    clang.cindex.CursorKind.COMPOUND_STMT,
    clang.cindex.CursorKind.IF_STMT,
    clang.cindex.CursorKind.FOR_STMT,
    clang.cindex.CursorKind.WHILE_STMT,
    clang.cindex.CursorKind.DO_STMT,
    clang.cindex.CursorKind.SWITCH_STMT,
    clang.cindex.CursorKind.CASE_STMT,
    clang.cindex.CursorKind.DEFAULT_STMT,
    clang.cindex.CursorKind.DECL_STMT,
}

def tokens_to_spelling(tokens):
    parts = []
    for t in tokens:
        if parts and parts[-1][-1].isalnum() and t.spelling and t.spelling[0].isalnum():
            parts.append(" " + t.spelling)
        else:
            parts.append(t.spelling)
    return "".join(parts)

def cursor_to_astnode(cursor):
    if cursor.kind in CONTAINER_KINDS:
        spelling = ""
    elif cursor.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
        spelling = cursor.spelling or cursor.displayname or ""
    elif cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        spelling = cursor.spelling or ""
    elif cursor.kind == clang.cindex.CursorKind.VAR_DECL:
        # Base variable name
        spelling = cursor.spelling or ""
        # Append initializer tokens if any
        children = list(cursor.get_children())
        if children:
            init_tokens = []
            for child in children:
                init_tokens.extend(t.spelling for t in child.get_tokens())
            if init_tokens:
                init_str = "".join(init_tokens).strip()
                if not init_str.startswith('='):
                    init_str = "= " + init_str
                spelling += " " + init_str
    elif cursor.kind == clang.cindex.CursorKind.INTEGER_LITERAL:
        tokens = list(cursor.get_tokens())
        spelling = tokens[0].spelling if tokens else ""
    elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
        spelling = cursor.spelling or ""
        if not spelling:
            children = list(cursor.get_children())
            if children:
                spelling = children[0].spelling or ""
    else:
        spelling = cursor.spelling or tokens_to_spelling(list(cursor.get_tokens())) or ""

    type_spelling = getattr(cursor.type, "spelling", None) if hasattr(cursor, "type") else None
    return_type_spelling = None
    if hasattr(cursor, "result_type") and cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        return_type_spelling = getattr(cursor.result_type, "spelling", None)

    node = ASTNode(cursor.kind, spelling, type_spelling=type_spelling, return_type_spelling=return_type_spelling)
    for child in cursor.get_children():
        child_node = cursor_to_astnode(child)
        child_node.parent = node
        node.children.append(child_node)
    return node

def clone_node(node, parent=None):
    new_node = ASTNode(
        node.kind,
        node.spelling,
        children=[],
        type_spelling=getattr(node, 'type_spelling', None),
        return_type_spelling=getattr(node, 'return_type_spelling', None),
    )
    new_node.parent = parent
    for child in node.children:
        cloned_child = clone_node(child, parent=new_node)
        new_node.children.append(cloned_child)
    return new_node

def get_all_nodes(node):
    nodes = [node]
    for child in node.children:
        nodes.extend(get_all_nodes(child))
    return nodes

def replace_child(parent, old_child, new_child):
    for idx, c in enumerate(parent.children):
        if c is old_child:
            parent.children[idx] = new_child
            new_child.parent = parent
            return True
    return False

def subtree_crossover(root1, root2):
    offspring1 = clone_node(root1)
    offspring2 = clone_node(root2)

    nodes1 = get_all_nodes(offspring1)
    nodes2 = get_all_nodes(offspring2)

    cross_point1 = random.choice(nodes1)
    cross_point2 = random.choice(nodes2)

    if cross_point1.parent is None:
        offspring1 = clone_node(cross_point2)
    else:
        replace_child(cross_point1.parent, cross_point1, clone_node(cross_point2, parent=cross_point1.parent))

    if cross_point2.parent is None:
        offspring2 = clone_node(cross_point1)
    else:
        replace_child(cross_point2.parent, cross_point2, clone_node(cross_point1, parent=cross_point2.parent))

    return offspring1, offspring2

def parse_source_to_astnodes_with_parser(source_path):
    parser = ASTParser(source_path)
    root_cursor = parser.parse()
    if root_cursor is None:
        raise RuntimeError(f"Failed to parse source file: {source_path}")
    return cursor_to_astnode(root_cursor)

def print_ast(node, depth=0):
    indent = "  " * depth
    kind_name = node.kind.name if hasattr(node.kind, 'name') else str(node.kind)
    type_info = f" : {node.type_spelling}" if node.type_spelling else ""
    ret_info = f" -> {node.return_type_spelling}" if node.return_type_spelling else ""

    # VAR_DECL: print variable name with initializer inline; skip children whose spelling duplicates initializer
    if node.kind == clang.cindex.CursorKind.VAR_DECL:
        var_name = node.spelling.split('=')[0].strip()
        initializer = node.spelling[len(var_name):].strip()
        print(f"{indent}{kind_name} — {var_name} {initializer}{type_info}{ret_info}")
        for child in node.children:
            if child.spelling and initializer and child.spelling in initializer:
                continue
            print_ast(child, depth + 1)
        return

    # RETURN_STMT: print "return <expr>" inline, and skip first child printing
    if node.kind == clang.cindex.CursorKind.RETURN_STMT and node.children:
        expr_spelling = node.children[0].spelling
        print(f"{indent}{kind_name} — return {expr_spelling}{type_info}{ret_info}")
        for i, child in enumerate(node.children):
            if i == 0:
                continue
            print_ast(child, depth + 1)
        return

    # Default print
    print(f"{indent}{kind_name} — '{node.spelling}'{type_info}{ret_info}")
    for child in node.children:
        print_ast(child, depth + 1)

# === Example usage ===
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ast_editable.py <source_file.c>")
        sys.exit(1)

    source_file = sys.argv[1]

    root = parse_source_to_astnodes_with_parser(source_file)
    print("Original AST:")
    print_ast(root)

    offspring1, offspring2 = subtree_crossover(root, root)
    print("\nOffspring 1 after crossover:")
    print_ast(offspring1)
    print("\nOffspring 2 after crossover:")
    print_ast(offspring2)
