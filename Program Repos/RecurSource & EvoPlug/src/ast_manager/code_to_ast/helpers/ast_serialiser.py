import json
from .ast_utils import is_system_header

def ast_to_lines(node, indent=0):
    if is_system_header(node):
        return []
    lines = [f"{'  ' * indent}- {node.kind} ({node.spelling})"]
    for child in node.get_children():
        lines.extend(ast_to_lines(child, indent + 1))
    return lines

def ast_to_string(node):
    return "\n".join(ast_to_lines(node))

def ast_to_json(node, source_code_path, pretty=False, indent=2):
    if is_system_header(node):
        return None

    node_dict = {
        "kind": str(node.kind),
        "spelling": str(node.spelling),
    }

    if getattr(node, "type_name", None):
        node_dict["type_name"] = node.type_name
    if getattr(node, "token_value", None):
        node_dict["token_value"] = node.token_value

    children_json = []
    for child in getattr(node, "children", []):
        child_json = ast_to_json(child, source_code_path, pretty=False)
        if child_json is not None:
            children_json.append(child_json)

    node_dict["children"] = children_json

    if pretty:
        return json.dumps(node_dict, indent=indent, ensure_ascii=False)

    return node_dict

def save_ast_json_to_file(node, source_code_path, print_to_console=False, output_file="ast.json"):
    ast_json = ast_to_json(node, source_code_path)
    formatted_json = json.dumps(ast_json, indent=2)
    if print_to_console:
        print("\nAST as JSON:")
        print(formatted_json)

    with open(output_file, "w") as f:
        json.dump(ast_json, f, indent=2)
    print(f"AST saved to {output_file}")
