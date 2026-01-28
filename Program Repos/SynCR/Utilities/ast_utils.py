from datetime import datetime
from graphviz import Digraph
from anytree import Node, RenderTree
import json
from Config.global_config import config
import os

def save_ast_as_json(ast, filename):
    def convert_to_json_serializable(node):
        if isinstance(node, list) and len(node) >= 2:
            return {
                "type": node[0],
                "value": node[1],
                "children": [convert_to_json_serializable(child) for child in node[2:]]
            }
        else:
            return {"type": "leaf", "value": str(node)}

    json_ast = convert_to_json_serializable(ast)
    
    with open(filename, 'w') as f:
        json.dump(json_ast, f, indent=2)
    
    print(f"AST saved as JSON to {filename}")

# Usage example:
# save_ast_as_json(ast, 'Data/AST/ast.json')

def print_ast_tree(ast, prefix="", is_last=True):
    if isinstance(ast, list) and len(ast) >= 2:
        print(prefix + ("└── " if is_last else "├── ") + f"{ast[0]} {ast[1]}")
        for i, child in enumerate(ast[2:]):
            print_ast_tree(child, prefix + ("    " if is_last else "│   "), i == len(ast[2:]) - 1)
    else:
        print(prefix + ("└── " if is_last else "├── ") + str(ast))

def create_ast_graph(ast):
    dot = Digraph(comment='AST')
    dot.attr(rankdir='TB')  # Top to bottom layout

    def add_node(node, parent=None):
        node_id = str(id(node))
        if isinstance(node, list) and len(node) >= 2:
            label = f"{node[0]}: {node[1]}"
            dot.node(node_id, label)
            if parent:
                dot.edge(parent, node_id)
            for child in node[2:]:
                add_node(child, node_id)
        else:
            dot.node(node_id, str(node))
            if parent:
                dot.edge(parent, node_id)

    add_node(ast)
    return dot

def create_ast_tree(ast, parent=None):
    if isinstance(ast, list) and len(ast) >= 2:
        node = Node(f"{ast[0]} {ast[1]}", parent=parent)
        for child in ast[2:]:
            create_ast_tree(child, node)
    else:
        Node(str(ast), parent=parent)
    return node

def save_ast(ast, rule_name):
    ast_graph = create_ast_graph(ast)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.exists(config.PATHS.ast_diagrams_output):
        os.makedirs(config.PATHS.ast_diagrams_output)
    file_name = f'{config.PATHS.ast_diagrams_output}/ast_graph_{rule_name}_{current_time}' #todo change the save path to output directory with all the files
    ast_graph.render(file_name, format='png', view=config.PROGRAM_GENERATION.open_saved_ast_images)

def save_ast_as_json(ast, rule_name):
    def convert_to_json_serializable(node):
        if isinstance(node, list) and len(node) >= 2:
            return {
                "type": node[0],
                "value": node[1],
                "children": [convert_to_json_serializable(child) for child in node[2:]]
            }
        else:
            return {"type": "leaf", "value": str(node)}

    json_ast = convert_to_json_serializable(ast)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.exists(config.PATHS.ast_json_output):
        os.makedirs(config.PATHS.ast_json_output)
    file_name = f'{config.PATHS.ast_json_output}/ast_json_{rule_name}_{current_time}.json' #todo change the save path to output directory with all the files
    with open(file_name, 'w') as f:
        json.dump(json_ast, f, indent=2)
    
    print(f"AST saved as JSON to {file_name}")

def get_function_info_from_ast(ast):
    return_type = None
    function_name = None

    def traverse(node):
        nonlocal return_type, function_name
        if isinstance(node, list):
            if node[0] == 'rule' and node[1] == '<return_type>':
                return_type = node[2][1]
            elif node[0] == 'rule' and node[1] == '<function_name>':
                function_name = node[2][1]
            else:
                for child in node[2:]:
                    traverse(child)

    traverse(ast)
    return function_name,return_type 

# Usage example:
# save_ast_as_json(ast, 'Data/AST/ast.json')
