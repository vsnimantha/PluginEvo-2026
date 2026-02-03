import json
import random
from clang.cindex import CursorKind
from src.ast_manager.code_to_ast.ast_parser import ASTNode

# class ASTNode:
#     def __init__(self, kind, spelling="", children=None, token_value=None, type_name=None):
#         self.kind = kind                   # e.g., "BINARY_OPERATOR", etc.
#         self.spelling = spelling           # for names, or operator symbol
#         self.children = children or []
#         self.token_value = token_value     # literal values
#         self.type_name = type_name         # for VAR_DECL, PARAMs, etc.
#         for child in self.children:
#             child.parent = self

#     def __repr__(self):
#         return f"ASTNode({self.kind}, spelling={repr(self.spelling)}, children={len(self.children)})"

# def json_to_astnode(node_json, parent=None):
#     kind_str = node_json.get('kind', '')
#     kind_name = kind_str.split('.')[-1] if '.' in kind_str else kind_str
#     kind = getattr(CursorKind, kind_name, kind_str)

#     token_value = node_json.get('token_value')
#     print(f"Loading node: kind={kind_name}, spelling={node_json.get('spelling','')!r}, token_value={token_value!r}")

#     node = ASTNode(
#         kind=kind,
#         spelling=node_json.get('spelling', ''),
#         children=[],
#         parent=parent,
#         token_value=token_value
#     )
#     for child_json in node_json.get('children', []):
#         child_node = json_to_astnode(child_json, parent=node)
#         node.children.append(child_node)
#     return node
def json_to_astnode(node_json, parent=None):
    kind_str = node_json.get('kind', '')
    kind_name = kind_str.split('.')[-1] if '.' in kind_str else kind_str
    # Use string kind name, not enum member
    kind = kind_name

    token_value = node_json.get('token_value')
    spelling = node_json.get('spelling', '')

    node = ASTNode(
        kind=kind,
        spelling=spelling,
        children=[],
        token_value=token_value
    )
    node.parent = parent  # assign parent manually

    for child_json in node_json.get('children', []):
        child_node = json_to_astnode(child_json, parent=node)
        node.children.append(child_node)

    return node



def clone_node(node, parent=None):
    cloned = ASTNode(
        node.kind,
        node.spelling,
        children=[],
        parent=parent,
        token_value=node.token_value
    )
    for child in node.children:
        cloned_child = clone_node(child, parent=cloned)
        cloned.children.append(cloned_child)
    return cloned

def get_all_nodes(node):
    nodes = [node]
    for child in node.children:
        nodes.extend(get_all_nodes(child))
    return nodes

def replace_child(parent, old_child, new_child):
    for i, c in enumerate(parent.children):
        if c is old_child:
            parent.children[i] = new_child
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
        replace_child(cross_point1.parent, cross_point1, clone_node(cross_point2, cross_point1.parent))

    if cross_point2.parent is None:
        offspring2 = clone_node(cross_point1)
    else:
        replace_child(cross_point2.parent, cross_point2, clone_node(cross_point1, cross_point2.parent))

    return offspring1, offspring2

def print_ast(node, depth=0):
    indent = "  " * depth
    kind_name = getattr(node.kind, "name", str(node.kind))
    
    # Prefer token_value if spelling is empty or whitespace
    if node.token_value is not None and (not node.spelling or node.spelling.strip() == ""):
        info = f"{kind_name} —  = {node.token_value}"
    else:
        info = f"{kind_name} — {node.spelling}"
    
    print(indent + info)
    
    for child in node.children:
        print_ast(child, depth + 1)



# === Example Usage ===
def example():
    # Example JSON with token_value fields for literals
    ast_json_str = '''
    {
      "kind": "CursorKind.TRANSLATION_UNIT",
      "spelling": "Genetic_Programming_Module/Test/C_Programs/example_1.c",
      "children": [
        {
          "kind": "CursorKind.FUNCTION_DECL",
          "spelling": "main",
          "children": [
            {
              "kind": "CursorKind.COMPOUND_STMT",
              "spelling": "",
              "children": [
                {
                  "kind": "CursorKind.DECL_STMT",
                  "spelling": "",
                  "children": [
                    {
                      "kind": "CursorKind.VAR_DECL",
                      "spelling": "N",
                      "children": [
                        {
                          "kind": "CursorKind.INTEGER_LITERAL",
                          "spelling": "",
                          "token_value": "10",
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "kind": "CursorKind.CALL_EXPR",
                  "spelling": "checkNum",
                  "children": [
                    {
                      "kind": "CursorKind.UNEXPOSED_EXPR",
                      "spelling": "checkNum",
                      "children": [
                        {
                          "kind": "CursorKind.DECL_REF_EXPR",
                          "spelling": "checkNum",
                          "children": []
                        }
                      ]
                    },
                    {
                      "kind": "CursorKind.UNEXPOSED_EXPR",
                      "spelling": "N",
                      "children": [
                        {
                          "kind": "CursorKind.DECL_REF_EXPR",
                          "spelling": "N",
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "kind": "CursorKind.RETURN_STMT",
                  "spelling": "",
                  "children": [
                    {
                      "kind": "CursorKind.INTEGER_LITERAL",
                      "spelling": "",
                      "token_value": "0",
                      "children": []
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    '''
    ast_json = json.loads(ast_json_str)

    root = json_to_astnode(ast_json)

    print("Original AST:")
    print_ast(root)

    offspring1, offspring2 = subtree_crossover(root, root)

    print("\nOffspring 1:")
    print_ast(offspring1)

    print("\nOffspring 2:")
    print_ast(offspring2)

if __name__ == "__main__":
    example()
