import random
from src.gp_manager.common import  gp_utils

# --- Node selection strategies ---

def pick_node_by_depth(nodes, prefer="deep"):
    """Pick node based on depth (deepest or shallowest)."""
    if not nodes:
        return None
    depths = [gp_utils.tree_depth(n) for n in nodes]
    if prefer == "deep":
        return nodes[depths.index(max(depths))]
    elif prefer == "shallow":
        return nodes[depths.index(min(depths))]
    return random.choice(nodes)

def pick_node_by_size(nodes, prefer="large"):
    """Pick node based on subtree size (largest or smallest)."""
    if not nodes:
        return None
    sizes = [gp_utils.count_nodes(n) for n in nodes]
    if prefer == "large":
        return nodes[sizes.index(max(sizes))]
    elif prefer == "small":
        return nodes[sizes.index(min(sizes))]
    return random.choice(nodes)

def weighted_choice(nodes, weight_fn):
    """Pick node with weighted probability."""
    if not nodes:
        return None
    weights = [weight_fn(n) for n in nodes]
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for node, w in zip(nodes, weights):
        upto += w
        if upto >= r:
            return node
    return nodes[-1]



# --- AST VALIDATION ---
# TO BE USED IF NEEDED
# NOT TESTED

def collect_symbols(root):
    """
    Collect all declared identifiers (variables, functions, parameters, etc.)
    from the AST.
    """
    decl_kinds = {"VAR_DECL", "FUNCTION_DECL", "PARAM_DECL",
                  "STRUCT_DECL", "CLASS_DECL", "ENUM_DECL", "FIELD_DECL"}
    nodes = gp_utils.collect_nodes(root, filter_fn=lambda n: n.kind in decl_kinds and n.spelling)
    return {n.spelling for n in nodes}

def extract_identifiers(root):
    """
    Collect all identifiers referenced in expressions, calls, member refs, etc.
    """
    ref_kinds = {"DECL_REF_EXPR", "CALL_EXPR", "MEMBER_REF_EXPR", "TYPE_REF"}
    nodes = gp_utils.collect_nodes(root, filter_fn=lambda n: n.kind in ref_kinds and n.spelling)
    return {n.spelling for n in nodes}

def has_invalid_literal_calls(root):
    bad_kinds = {"STRING_LITERAL", "INTEGER_LITERAL", "CHARACTER_LITERAL", "FLOATING_LITERAL"}
    nodes = gp_utils.collect_nodes(root, filter_fn=lambda n: n.kind == "CALL_EXPR")
    for n in nodes:
        if n.children and n.children[0].kind in bad_kinds:
            return True
    return False


def validate_ast(child_ast, parent1_ast=None, parent2_ast=None):
    declared = collect_symbols(child_ast)
    if parent1_ast and parent2_ast:
        declared |= collect_symbols(parent1_ast) | collect_symbols(parent2_ast)

    used = extract_identifiers(child_ast)
    undeclared = used - declared
    if undeclared:
        print("[DEBUG] Undeclared identifiers:", undeclared)
        return False

    # Ensure main() exists
    mains = gp_utils.collect_nodes(child_ast, filter_fn=lambda n: n.kind == "FUNCTION_DECL" and n.spelling == "main")
    if not mains:
        print("[DEBUG] No valid main() found.")
        return False

    # Guard against invalid literal calls
    if has_invalid_literal_calls(child_ast):
        print("[DEBUG] Invalid literal call detected.")
        return False

    # Check for empty unexposed expressions
    empties = gp_utils.collect_nodes(child_ast, filter_fn=lambda n: n.kind == "UNEXPOSED_EXPR" and not n.children)
    if empties:
        print("[DEBUG] Empty unexposed expression found.")
        return False

    # Ensure VAR_DECL has TYPE_REF
    var_decls = gp_utils.collect_nodes(child_ast, filter_fn=lambda n: n.kind == "VAR_DECL")
    for v in var_decls:
        if not any(ch.kind == "TYPE_REF" for ch in v.children):
            print(f"[DEBUG] VAR_DECL {v.spelling} missing TYPE_REF.")
            return False

    return True

