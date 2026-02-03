from graphviz import Digraph

def parse_clang_ast(lines):
    """
    Parse the indented CursorKind output lines into a tree structure.
    Each node is a dict: {'label': ..., 'children': [...]}
    """
    stack = []
    root = None

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Count leading spaces to determine level / indentation
        indent = len(line) - len(line.lstrip(' '))
        # Assuming 2 spaces per level
        level = indent // 2

        # Parse the line: expected format 'CursorKind.SOMETHING — optional_name_or_value'
        parts = line.strip().split('—')
        label = parts[0].strip()  # CursorKind.XYZ
        if len(parts) > 1:
            extra = parts[1].strip()
            if extra:
                label += " " + extra

        node = {'label': label, 'children': []}

        if level == 0:
            # Root node
            root = node
            stack = [(level, node)]
        else:
            # Pop until we find parent level
            while stack and stack[-1][0] >= level:
                stack.pop()

            # Parent is last item on stack
            if stack:
                parent = stack[-1][1]
                parent['children'].append(node)
            stack.append((level, node))

    return root

def add_nodes(graph, node, node_id="0"):
    """
    Recursively add nodes and edges to the graph.
    node: parsed node dict {'label':..., 'children':[...]}
    node_id: string id for Graphviz node
    """
    graph.node(node_id, node['label'])
    for i, child in enumerate(node['children']):
        child_id = f"{node_id}_{i}"
        graph.edge(node_id, child_id)
        add_nodes(graph, child, child_id)

def visualize_clang_ast(clang_output_text, output_file='clang_ast'):
    lines = clang_output_text.splitlines()
    tree = parse_clang_ast(lines)

    dot = Digraph(comment="Clang AST")
    add_nodes(dot, tree)
    dot.render(output_file, format='png', view=True)
    print(f"AST visualization saved to {output_file}.png")

if __name__ == "__main__":
    # Paste your entire clang output here as a multiline string
    clang_output = '''
CursorKind.VAR_DECL — maze
  CursorKind.INTEGER_LITERAL — 
  CursorKind.INTEGER_LITERAL — 
  CursorKind.INIT_LIST_EXPR — 
    CursorKind.INIT_LIST_EXPR — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
    CursorKind.INIT_LIST_EXPR — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
    CursorKind.INIT_LIST_EXPR — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
    CursorKind.INIT_LIST_EXPR — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
    CursorKind.INIT_LIST_EXPR — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
      CursorKind.INTEGER_LITERAL — 
CursorKind.VAR_DECL — solution
  CursorKind.INTEGER_LITERAL — 
  CursorKind.INTEGER_LITERAL — 
CursorKind.FUNCTION_DECL — solveMaze
  CursorKind.PARM_DECL — x
  CursorKind.PARM_DECL — y
  CursorKind.COMPOUND_STMT — 
    CursorKind.IF_STMT — 
      CursorKind.BINARY_OPERATOR — &&
        CursorKind.BINARY_OPERATOR — ==
          CursorKind.UNEXPOSED_EXPR — x
            CursorKind.DECL_REF_EXPR — x
          CursorKind.BINARY_OPERATOR — -
            CursorKind.INTEGER_LITERAL — 
            CursorKind.INTEGER_LITERAL — 
        CursorKind.BINARY_OPERATOR — ==
          CursorKind.UNEXPOSED_EXPR — y
            CursorKind.DECL_REF_EXPR — y
          CursorKind.BINARY_OPERATOR — -
            CursorKind.INTEGER_LITERAL — 
            CursorKind.INTEGER_LITERAL — 
      CursorKind.COMPOUND_STMT — 
        CursorKind.BINARY_OPERATOR — =
          CursorKind.ARRAY_SUBSCRIPT_EXPR — 
            CursorKind.UNEXPOSED_EXPR — 
              CursorKind.ARRAY_SUBSCRIPT_EXPR — 
                CursorKind.UNEXPOSED_EXPR — solution
                  CursorKind.DECL_REF_EXPR — solution
                CursorKind.UNEXPOSED_EXPR — x
                  CursorKind.DECL_REF_EXPR — x
            CursorKind.UNEXPOSED_EXPR — y
              CursorKind.DECL_REF_EXPR — y
          CursorKind.INTEGER_LITERAL — 
        CursorKind.RETURN_STMT — 
          CursorKind.INTEGER_LITERAL — 
    # (truncated for brevity)
'''

    visualize_clang_ast(clang_output, 'clang_ast_output')
