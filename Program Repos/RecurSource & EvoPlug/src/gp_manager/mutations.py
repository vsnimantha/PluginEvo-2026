import random, copy
import src.gp_manager.common.constant as const
from src.ast_manager.common.ast_node import ASTNode
from src.gp_manager.common.gp_utils import collect_nodes
from src.gp_manager.common import utils

# Operator sets
# TODO: Move to constants module
ARITH   = {"+", "-", "*", "/", "%", "<<", ">>"}
REL     = {"<", "<=", "==", "!=", ">=", ">"}
LOGIC   = {"&&", "||"}
ASSIGN  = {"=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="}
UNARY   = {"++", "--", "+", "-", "!", "~"}

# -----------------------------
# Type helpers
# -----------------------------
# TODO: Move to constants or utils module
def is_numeric(node):
    return node and node.type_name in {"int", "float", "double"}

def is_boolean(node):
    return node and node.type_name == "bool"

def is_string(node):
    return node and node.type_name == "string"

def children_types(node):
    return [getattr(c, "type_name", None) for c in node.children]

# -----------------------------
# Core mutations (type-aware)
# -----------------------------
def mutate_flip_arithmetic(node):
    if node.kind == "BINARY_OPERATOR" and node.spelling in ARITH:
        if len(node.children) == 2 and is_numeric(node.children[0]) and is_numeric(node.children[1]):
            node.spelling = random.choice(list(ARITH - {node.spelling}))

def mutate_flip_relational(node):
    if node.kind == "BINARY_OPERATOR" and node.spelling in REL:
        if len(node.children) == 2:
            ltype, rtype = children_types(node)
            if ltype == rtype and ltype in {"int", "float", "double", "bool"}:
                node.spelling = random.choice(list(REL - {node.spelling}))

def mutate_flip_logical(node):
    if node.kind == "BINARY_OPERATOR" and node.spelling in LOGIC:
        if len(node.children) == 2 and is_boolean(node.children[0]) and is_boolean(node.children[1]):
            node.spelling = random.choice(list(LOGIC - {node.spelling}))

def mutate_flip_assignment(node):
    if node.kind == "BINARY_OPERATOR" and node.spelling in ASSIGN:
        # Simple guard: left side must be numeric lvalue; skip complex lvalue checks
        if node.children and is_numeric(node.children[0]):
            node.spelling = random.choice(list(ASSIGN - {node.spelling}))

def mutate_flip_unary(node):
    if node.kind == "UNARY_OPERATOR" and node.spelling in UNARY:
        target = node.children[0] if node.children else None
        # ++/--, +, -, ~ apply to numeric; ! applies to bool
        if node.spelling in {"++", "--", "+", "-", "~"} and is_numeric(target):
            node.spelling = random.choice(list({"++","--","+","-","~"} - {node.spelling}))
        elif node.spelling == "!" and is_boolean(target):
            node.spelling = "!"  # no flip among logical NOT, keep structure

def mutate_literal(node):
    if node.kind == "INTEGER_LITERAL" and node.token_value is not None:
        try:
            val = int(node.token_value)
            node.token_value = str(val + random.choice([-2, -1, 1, 2]))
        except:
            pass

def mutate_string(node):
    if node.kind == "STRING_LITERAL" and node.token_value:
        if "even" in node.token_value:
            node.token_value = node.token_value.replace("even", "odd")
        elif "odd" in node.token_value:
            node.token_value = node.token_value.replace("odd", "even")

def mutate_variable(node, scope_vars):
    if node.kind == "DECL_REF_EXPR" and scope_vars:
        # scope_vars: [{"name": "a", "type_name": "int"}, ...]
        same_type = [v for v in scope_vars if v.get("type_name") == node.type_name]
        if same_type:
            node.spelling = random.choice([v["name"] for v in same_type])

# -----------------------------
# Structural/statement mutations
# -----------------------------
def mutate_operand_swap(node):
    if node.kind == "BINARY_OPERATOR" and len(node.children) == 2:
        node.children[0], node.children[1] = node.children[1], node.children[0]
        node.children[0].parent = node
        node.children[1].parent = node

def mutate_stmt_delete(node):
    if node.kind == "COMPOUND_STMT" and len(node.children) > 1:
        victim = random.choice(node.children)
        node.children.remove(victim)

def mutate_stmt_insert(node):
    if node.kind == "COMPOUND_STMT":
        # Insert a harmless empty statement at the start
        node.children.insert(0, ASTNode("RAW_TOKENS", spelling=";"))

def mutate_stmt_swap(node):
    if node.kind == "COMPOUND_STMT" and len(node.children) >= 2:
        i, j = random.sample(range(len(node.children)), 2)
        node.children[i], node.children[j] = node.children[j], node.children[i]

def mutate_if_branch_swap(node):
    # IF_STMT children convention (typical): [cond, then, else?]
    if node.kind == "IF_STMT" and len(node.children) >= 3:
        node.children[1], node.children[2] = node.children[2], node.children[1]

def mutate_loop_bound(node):
    # FOR_STMT children convention (typical): [init, cond, incr, body]
    if node.kind == "FOR_STMT" and len(node.children) >= 2:
        cond = node.children[1]
        if cond.kind == "BINARY_OPERATOR" and cond.spelling in REL:
            lits = [c for c in collect_nodes(cond) if c.kind == "INTEGER_LITERAL"]
            if lits:
                target = random.choice(lits)
                try:
                    val = int(target.token_value)
                    target.token_value = str(val + random.choice([-1, 1]))
                except:
                    pass

def mutate_loop_increment(node):
    if node.kind == "FOR_STMT" and len(node.children) >= 3:
        incr = node.children[2]
        if incr.kind == "UNARY_OPERATOR" and incr.spelling in {"++", "--"}:
            incr.spelling = "++" if incr.spelling == "--" else "--"

def mutate_wrap_conditional(node):
    # Wrap any statement in if (1) { stmt } to preserve semantics
    if const.category(node) == "stmt":
        wrapper = ASTNode("IF_STMT", children=[
            ASTNode("INTEGER_LITERAL", token_value="1", type_name="bool"),
            node
        ])
        if node.parent:
            i = node.parent.children.index(node)
            node.parent.children[i] = wrapper
            wrapper.parent = node.parent
            node.parent = wrapper

def mutate_duplicate_stmt(node):
    if node.kind == "COMPOUND_STMT" and node.children:
        dup = utils.safe_copy(random.choice(node.children))
        node.children.append(dup)
        dup.parent = node

# -----------------------------
# Context-aware mutation map
# -----------------------------
MUTATION_MAP = {
    "FOR_STMT": [mutate_loop_bound, mutate_loop_increment, mutate_wrap_conditional],
    "IF_STMT": [mutate_if_branch_swap, mutate_wrap_conditional],
    "COMPOUND_STMT": [mutate_stmt_delete, mutate_stmt_insert, mutate_stmt_swap,
                      mutate_duplicate_stmt, mutate_wrap_conditional],
    "BINARY_OPERATOR": [mutate_flip_arithmetic, mutate_flip_relational,
                        mutate_flip_logical, mutate_flip_assignment,
                        mutate_operand_swap],
    "UNARY_OPERATOR": [mutate_flip_unary],
    "INTEGER_LITERAL": [mutate_literal],
    "STRING_LITERAL": [mutate_string],
    "DECL_REF_EXPR": [mutate_variable],
}

# -----------------------------
# Dispatcher
# -----------------------------
def mutate_node(node, scope_vars=None):
    ops = MUTATION_MAP.get(node.kind)
    if not ops:
        cat = const.category(node)
        ops = MUTATION_MAP.get(cat, [])
    if not ops:
        print(f"[DEBUG] No mutation ops available for node kind={node.kind}, category={const.category(node)}")
        return

    # Try a few random operators; bail if no effective change
    for attempt in range(5):
        op = random.choice(ops)
        before = (node.kind, node.spelling, node.token_value, tuple(children_types(node)))
        print(f"[DEBUG] Attempt {attempt+1}: chosen op={op.__name__}, before={before}")

        if op.__code__.co_argcount == 1:
            op(node)
        else:
            op(node, scope_vars or [])

        after = (node.kind, node.spelling, node.token_value, tuple(children_types(node)))
        print(f"[DEBUG] After mutation: {after}")

        if after != before:
            print("[DEBUG] Mutation successful, node changed.")
            break
        else:
            print("[DEBUG] Mutation had no effect, retrying...")

# -----------------------------
# Test harness
# -----------------------------
def build_toy_expr_ast():
    return ASTNode("RETURN_STMT", children=[
        ASTNode("BINARY_OPERATOR", spelling="+", type_name="int", children=[
            ASTNode("DECL_REF_EXPR", spelling="a", type_name="int"),
            ASTNode("INTEGER_LITERAL", token_value="5", type_name="int")
        ])
    ])

def build_toy_loop_ast():
    return ASTNode("FOR_STMT", children=[
        ASTNode("BINARY_OPERATOR", spelling="=", type_name="int", children=[
            ASTNode("DECL_REF_EXPR", spelling="i", type_name="int"),
            ASTNode("INTEGER_LITERAL", token_value="0", type_name="int")
        ]),
        ASTNode("BINARY_OPERATOR", spelling="<", type_name="bool", children=[
            ASTNode("DECL_REF_EXPR", spelling="i", type_name="int"),
            ASTNode("INTEGER_LITERAL", token_value="3", type_name="int")
        ]),
        ASTNode("UNARY_OPERATOR", spelling="++", type_name="int", children=[
            ASTNode("DECL_REF_EXPR", spelling="i", type_name="int")
        ]),
        ASTNode("COMPOUND_STMT", children=[
            ASTNode("DECL_REF_EXPR", spelling="a", type_name="int"),
            ASTNode("DECL_REF_EXPR", spelling="b", type_name="int"),
            ASTNode("DECL_REF_EXPR", spelling="c", type_name="int")
        ])
    ])

def print_ast(node, indent=0):
    pad = "  " * indent
    extras = []
    if node.spelling: extras.append(f"spelling='{node.spelling}'")
    if node.token_value: extras.append(f"token='{node.token_value}'")
    if hasattr(node, "type_name") and node.type_name: extras.append(f"type='{node.type_name}'")
    print(f"{pad}{node.kind} ({', '.join(extras)})")
    for c in node.children:
        print_ast(c, indent+1)

def run_mutation_tests():
    random.seed(42)
    scope_vars = [
        {"name": "a", "type_name": "int"},
        {"name": "b", "type_name": "int"},
        {"name": "c", "type_name": "int"},
        {"name": "flag", "type_name": "bool"}
    ]
    toy_builders = [("expr", build_toy_expr_ast), ("loop", build_toy_loop_ast)]

    for name, builder in toy_builders:
        ast_copy = builder()
        nodes = collect_nodes(ast_copy)
        for _ in range(3):
            target = random.choice(collect_nodes(ast_copy))
            print("="*50)
            print(f"Target node kind: {target.kind} ({getattr(target, 'type_name', None)}) in {name} AST")
            print("Before:")
            print_ast(ast_copy)
            mutate_node(target, scope_vars)
            print("After:")
            print_ast(ast_copy)
            print()

if __name__ == "__main__":
    run_mutation_tests()

# python3 -m src.gp_manager.mutations