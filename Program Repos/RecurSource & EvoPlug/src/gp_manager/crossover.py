import copy
import random
from src.gp_manager.common import constant, gp_utils,crossover_helpers,utils

# -------------------------------------------------------------------
# Safety filter for crossover nodes
# -------------------------------------------------------------------
# We exclude generic CALL_EXPR because it frequently includes I/O like operator<<,
# which breaks semantics when swapped into control flow or return sites.
# Reference:
# - Koza (1992): subtree crossover; warns about unconstrained swaps producing nonsense.
# - Montana (1995), Whigham (1995): typed/grammar-based GP to enforce semantic validity.

    # Bias toward meaningful constructs
# SAFE_NODE_KINDS = {
#     "IF_STMT", "FOR_STMT", "WHILE_STMT",
#     "BINARY_OPERATOR", "UNARY_OPERATOR",
#     "DECL_STMT", "VAR_DECL",
#     "INTEGER_LITERAL", "STRING_LITERAL",
#     "RETURN_STMT", "COMPOUND_STMT"
# }

SAFE_NODE_KINDS = {
        "FUNCTION_DECL", "COMPOUND_STMT", "IF_STMT", "FOR_STMT",
        "DECL_STMT", "VAR_DECL", "RETURN_STMT",
        "BINARY_OPERATOR", "UNARY_OPERATOR", "CALL_EXPR",
        "ARRAY_SUBSCRIPT_EXPR", "ASSIGNMENT_EXPR", "FLOATING_LITERAL",
        "INTEGER_LITERAL", "STRING_LITERAL"
    }

# def is_safe_node(node):
#     return node.kind in {
#         "FUNCTION_DECL", "COMPOUND_STMT", "IF_STMT",
#         "FOR_STMT", "DECL_STMT", "BINARY_OPERATOR"
#     }

def is_safe_node(node):
    return node.kind in SAFE_NODE_KINDS




def same_category(a, b):
    """Match by syntactic category (expr/stmt/decl)."""
    return constant.category(a) == constant.category(b)


# -------------------------------------------------------------------
# Subtree crossover (Koza, 1992)
# -------------------------------------------------------------------

def subtree_crossover(ast1, ast2, strategy="deep"):
    a1, a2 = utils.safe_copy(ast1), utils.safe_copy(ast2)

    # collect candidates from parent1
    nodes1 = gp_utils.collect_nodes(a1, is_safe_node)
    if not nodes1:
        return a1, a2

    # probabilistic mix: 80% strategy, 20% random
    if random.random() < 0.8:
        if strategy == "deep":
            n1 = crossover_helpers.pick_node_by_depth(nodes1, prefer="deep")
        elif strategy == "shallow":
            n1 = crossover_helpers.pick_node_by_depth(nodes1, prefer="shallow")
        elif strategy == "large":
            n1 = crossover_helpers.pick_node_by_size(nodes1, prefer="large")
        elif strategy == "small":
            n1 = crossover_helpers.pick_node_by_size(nodes1, prefer="small")
        else:
            n1 = random.choice(nodes1)
    else:
        n1 = random.choice(nodes1)

    if not n1 or not n1.parent:
        return a1, a2
    p1 = n1.parent

    # collect compatible candidates from parent2
    nodes2 = gp_utils.collect_nodes(
        a2,
        lambda n: is_safe_node(n) and same_category(n, n1) and getattr(n, "type", None) == getattr(n1, "type", None)
    )
    if not nodes2:
        return a1, a2
    # choose node from parent2 with same strategy
    if random.random() < 0.8:
        if strategy in ("deep", "shallow"):
            n2 = crossover_helpers.pick_node_by_depth(nodes2, prefer=strategy)
        elif strategy in ("large", "small"):
            n2 = crossover_helpers.pick_node_by_size(nodes2, prefer=strategy)
        else:
            n2 = random.choice(nodes2)
    else:
        n2 = random.choice(nodes2)

    if not n2 or not n2.parent:
        return a1, a2
    p2 = n2.parent

    # avoid swapping identical nodes
    if n1.kind == n2.kind and getattr(n1, "spelling", None) == getattr(n2, "spelling", None):
        return a1, a2

    try:
        i1 = p1.children.index(n1)
        i2 = p2.children.index(n2)
    except ValueError:
        return a1, a2
    
    print(f"[CROSSOVER] Subtree swap: {n1.kind} (spell={getattr(n1,'spelling','')}) "
          f"<-> {n2.kind} (spell={getattr(n2,'spelling','')})")

    # perform swap
    p1.children[i1], p2.children[i2] = n2, n1
    n1.parent, n2.parent = p2, p1

    return a1, a2

# -------------------------------------------------------------------
# Size-fair crossover (Langdon, 1995)
# -------------------------------------------------------------------
def size_fair_crossover(ast1, ast2, max_diff=5):
    a1, a2 = utils.safe_copy(ast1), utils.safe_copy(ast2)

    nodes1 = gp_utils.collect_nodes(a1, is_safe_node)
    if not nodes1:
        return a1, a2
    n1 = random.choice(nodes1)
    size1 = gp_utils.count_nodes(n1)

    nodes2 = gp_utils.collect_nodes(
        a2, lambda n: is_safe_node(n) and same_category(n, n1)
                      and abs(gp_utils.count_nodes(n) - size1) <= max_diff
    )
    if not nodes2:
        return a1, a2
    n2 = random.choice(nodes2)

    if not n1.parent or not n2.parent:
        return a1, a2

    p1, p2 = n1.parent, n2.parent
    try:
        i1 = next(i for i, c in enumerate(p1.children) if c is n1)
        i2 = next(i for i, c in enumerate(p2.children) if c is n2)
    except StopIteration:
        return a1, a2

    print(f"[CROSSOVER] Size-fair swap: {n1.kind} (~{size1} nodes) "
          f"<-> {n2.kind} (~{gp_utils.count_nodes(n2)} nodes)")

    p1.children[i1], p2.children[i2] = n2, n1
    n1.parent, n2.parent = p2, p1

    return a1, a2


# -------------------------------------------------------------------
# Uniform crossover (Syswerda, 1989)
# -------------------------------------------------------------------
def uniform_crossover(ast1, ast2, swap_prob=0.1):
    a1, a2 = utils.safe_copy(ast1), utils.safe_copy(ast2)

    def recurse(n1, n2):
        if is_safe_node(n1) and is_safe_node(n2) and same_category(n1, n2):
            if random.random() < swap_prob:
                return n2, n1
        if len(n1.children) == len(n2.children):
            for i in range(len(n1.children)):
                c1, c2 = recurse(n1.children[i], n2.children[i])
                n1.children[i], n2.children[i] = c1, c2
        return n1, n2

    recurse(a1, a2)
    return a1, a2


# -------------------------------------------------------------------
# One-point crossover (Holland, 1975; adapted in GP)
# -------------------------------------------------------------------
def one_point_crossover(ast1, ast2):
    a1, a2 = utils.safe_copy(ast1), utils.safe_copy(ast2)

    nodes1 = gp_utils.collect_nodes(a1, is_safe_node)
    nodes2 = gp_utils.collect_nodes(a2, is_safe_node)
    if not nodes1 or not nodes2:
        return a1, a2

    n1 = random.choice(nodes1)
    n2 = random.choice(nodes2)
    if not n1.parent or not n2.parent:
        return a1, a2

    p1, p2 = n1.parent, n2.parent
    try:
        i1 = next(i for i, c in enumerate(p1.children) if c is n1)
        i2 = next(i for i, c in enumerate(p2.children) if c is n2)
    except StopIteration:
        return a1, a2

    print(f"[CROSSOVER] One-point swap: {n1.kind} <-> {n2.kind}")

    p1.children[i1], p2.children[i2] = n2, n1
    n1.parent, n2.parent = p2, p1

    return a1, a2
