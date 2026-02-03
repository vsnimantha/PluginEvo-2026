def collect_nodes(root, filter_fn=lambda n: True):
    nodes = []
    def _walk(n):
        if filter_fn(n):
            # print(f"[DEBUG] Collected node: {n.kind} (spell={getattr(n,'spelling','')})")
            nodes.append(n)
        for c in n.children:
            _walk(c)
    _walk(root)
    return nodes

def replace_in_parent(parent, old_child, new_child):
    if not parent:
        return
    i = parent.children.index(old_child)
    parent.children[i] = new_child
    new_child.parent = parent

def count_nodes(ast):
    return len(collect_nodes(ast))

def tree_depth(node):
    if not node or not getattr(node, "children", None):
        return 1

    max_depth = 0
    stack = [(node, 1)]  # (current_node, current_depth)

    while stack:
        current, depth = stack.pop()
        max_depth = max(max_depth, depth)
        for child in getattr(current, "children", []):
            stack.append((child, depth + 1))

    return max_depth


def count_branches(ast):
    branch_kinds = {"IF_STMT", "FOR_STMT", "WHILE_STMT", "SWITCH_STMT"}
    return len(collect_nodes(ast, filter_fn=lambda n: n.kind in branch_kinds))


def print_ast(node, indent=0):
    pad = "  " * indent
    tv = f", token_value={node.token_value}" if node.token_value is not None else ""
    tn = f", type_name={node.type_name}" if node.type_name is not None else ""
    sp = f", spelling='{node.spelling}'" if node.spelling != "" else ""
    print(f"{pad}{node.kind}{sp}{tv}{tn}")
    for child in node.children:
        print_ast(child, indent + 1)


def count_unique_node_types(ast):
    """
    Count the number of unique node kinds in an AST.
    Uses collect_nodes to traverse the tree.
    """
    if ast is None:
        return 0
    nodes = collect_nodes(ast)
    kinds = {n.kind for n in nodes if hasattr(n, "kind")}
    return len(kinds)

