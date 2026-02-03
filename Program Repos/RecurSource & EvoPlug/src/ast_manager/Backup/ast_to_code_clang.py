import sys
import clang.cindex
from clang.cindex import CursorKind, TypeKind

def token_eq(a, b):
    return (a.spelling == b.spelling and
            getattr(a.location, 'file', None) == getattr(b.location, 'file', None) and
            getattr(a.location, 'line', None) == getattr(b.location, 'line', None) and
            getattr(a.location, 'column', None) == getattr(b.location, 'column', None))

def find_token_index(tokenlist, token):
    for i, t in enumerate(tokenlist):
        if token_eq(t, token):
            return i
    raise ValueError("Token not found in tokenlist")

def extract_binary_operator(node):
    tokens = list(node.get_tokens())
    children = list(node.get_children())
    if len(children) != 2:
        return "?"

    left_tokens = list(children[0].get_tokens())
    right_tokens = list(children[1].get_tokens())

    def token_key(t):
        loc = t.location
        return (loc.file.name if loc.file else None, loc.line, loc.column, t.spelling)

    node_token_keys = set(token_key(t) for t in tokens)
    left_token_keys = set(token_key(t) for t in left_tokens)
    right_token_keys = set(token_key(t) for t in right_tokens)

    operator_keys = node_token_keys - left_token_keys - right_token_keys

    # List of common C binary operators, sorted descending length for neatness (sorting optional)
    common_ops = [
        "==", "!=", ">=", "<=", "&&", "||",        # comparisons and logical
        "+", "-", "*", "/", "%",                   # arithmetic
        "=", "+=", "-=", "*=", "/=", "%=",         # assignment and compound assignment
        "&", "|", "^",                            # bitwise
        "&=", "|=", "^=",                         # bitwise compound assignment
        "<<", ">>",                              # bitwise shift
        "<<=", ">>=",                            # shift compound assignment
        "<", ">",                               # relational
        ",",                                    # comma operator
    ]

    for t in tokens:
        if token_key(t) in operator_keys and t.kind.name == 'PUNCTUATION' and t.spelling not in '()[]':
            # Match operator only if exact equality with token spelling
            for op in common_ops:
                if t.spelling == op:
                    return op
            return t.spelling  # fallback token spelling if no match found

    # Final fallback: scan tokens for known operators exactly
    token_spellings = [t.spelling for t in tokens if t.kind.name == 'PUNCTUATION' and t.spelling not in '()[]']
    for op in common_ops:
        if op in token_spellings:
            return op

    return "?"



def extract_unary_operator(node, child):
    tokens = list(node.get_tokens())
    child_tokens_spellings = set(t.spelling for t in child.get_tokens())
    ops = [t.spelling for t in tokens
           if t.spelling not in child_tokens_spellings and
           t.kind.name == 'PUNCTUATION' and t.spelling not in '()']
    if ops:
        return ops[0]
    return '?'


# Operator precedences in C (lower number = lower prec)
precedence = {
    "=": 2, "+=": 2, "-=": 2, "*=": 2, "/=": 2, "%=": 2,
    "<<=": 2, ">>=": 2, "&=": 2, "^=": 2, "|=": 2,
    "||": 3,
    "&&": 4,
    "|": 5,
    "^": 6,
    "&": 7,
    "==": 8, "!=": 8,
    "<": 9, ">": 9, "<=": 9, ">=": 9,
    "<<": 10, ">>": 10,
    "+": 11, "-": 11,
    "*": 12, "/": 12, "%": 12,
    ",": 1,
}

def get_precedence(op):
    # Higher number means higher precedence, default low precedence for unknown operators
    return precedence.get(op, 0)

def emit_expr(node, parent_prec=0):
    k = node.kind

    if k == CursorKind.BINARY_OPERATOR:
        children = list(node.get_children())
        if len(children) != 2:
            return '?'
        lhs, rhs = children
        op = extract_binary_operator(node)
        lhs_code = emit_expr(lhs, get_precedence(op))
        # For right-associative operators, rhs should have strictly greater parent precedence
        rhs_code = emit_expr(rhs, get_precedence(op) + 1)

        expr = f"{lhs_code} {op} {rhs_code}"
        if get_precedence(op) < parent_prec:
            return f"({expr})"
        else:
            return expr

    elif k == CursorKind.UNEXPOSED_EXPR:
        children = list(node.get_children())
        if children:
            return emit_expr(children[0], parent_prec)
        return ""

    elif k == CursorKind.UNARY_OPERATOR:
        children = list(node.get_children())
        if not children:
            return ''
        op = extract_unary_operator(node, children[0])
        tokens = list(node.get_tokens())
        operand = emit_expr(children[0], 1000)  # unary ops have high precedence
        if tokens and tokens[0].spelling == op:
            return f"{op}{operand}"
        else:
            return f"{operand}{op}"

    elif k in (CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL,
               CursorKind.STRING_LITERAL, CursorKind.CHARACTER_LITERAL):
        for tok in node.get_tokens():
            return tok.spelling
        return '?'

    elif k == CursorKind.DECL_REF_EXPR:
        return node.spelling or ''

    elif k == CursorKind.ARRAY_SUBSCRIPT_EXPR:
        children = list(node.get_children())
        if len(children) == 2:
            return f"{emit_expr(children[0], 1000)}[{emit_expr(children[1], 0)}]"
        return ''

    elif k == CursorKind.CALL_EXPR:
        children = list(node.get_children())
        if children and children[0].kind in (CursorKind.UNEXPOSED_EXPR, CursorKind.DECL_REF_EXPR):
            func = emit_expr(children[0], 1000)
            args = [emit_expr(c, 0) for c in children[1:]]
        else:
            func = node.spelling or ''
            args = [emit_expr(c, 0) for c in children]
        return f"{func}({', '.join(args)})"

    elif k == CursorKind.PAREN_EXPR:
        children = list(node.get_children())
        if children:
            return f"({emit_expr(children[0], 0)})"
        return "()"

    elif k == CursorKind.MEMBER_REF_EXPR:
        children = list(node.get_children())
        if children:
            base = emit_expr(children[0], 1000)
            member = node.spelling or ''
            return f"{base}.{member}"

    return node.spelling or ''


def extract_initializer(node):
    if node.kind == CursorKind.INIT_LIST_EXPR:
        items = [extract_initializer(c) for c in node.get_children()]
        return '{' + ', '.join(items) + '}'
    elif node.kind == CursorKind.INTEGER_LITERAL:
        for tok in node.get_tokens():
            return tok.spelling
        return '?'
    elif node.kind == CursorKind.FLOATING_LITERAL:
        for tok in node.get_tokens():
            return tok.spelling
        return '?'
    elif node.kind == CursorKind.CHARACTER_LITERAL:
        for tok in node.get_tokens():
            return tok.spelling
        return '?'
    elif node.kind == CursorKind.STRING_LITERAL:
        for tok in node.get_tokens():
            return tok.spelling
        return '?'
    else:
        return emit_expr(node)

def decl_to_string(decl, elide_type=False):
    name = decl.spelling or ''
    t = decl.type
    base_type = ""
    dims = []

    def token_key(t):
        loc = t.location
        return (loc.file.name if loc.file else None, loc.line, loc.column, t.spelling)

    current_type = t
    dimension_tokens = set()

    while True:
        if current_type.kind == TypeKind.CONSTANTARRAY:
            dims.append(str(current_type.element_count))
            for child in decl.get_children():
                if child.kind == CursorKind.INTEGER_LITERAL:
                    for tok in child.get_tokens():
                        dimension_tokens.add(token_key(tok))
            current_type = current_type.element_type
        elif current_type.kind == TypeKind.INCOMPLETEARRAY:
            dims.append('')
            current_type = current_type.element_type
        elif current_type.kind == TypeKind.VARIABLEARRAY:
            dims.append('n')
            current_type = current_type.element_type
        else:
            base_type = current_type.spelling
            break
    base_type = base_type.split('[')[0].strip()

    dims_str = ''.join(f'[{d}]' for d in dims)

    init = ""
    init_exprs = [c for c in decl.get_children() if c.kind == CursorKind.INIT_LIST_EXPR]
    if init_exprs:
        init = f" = {extract_initializer(init_exprs[0])}"
    else:
        for c in decl.get_children():
            if c.kind == CursorKind.INTEGER_LITERAL:
                child_token_keys = set(token_key(tok) for tok in c.get_tokens())
                if child_token_keys & dimension_tokens:
                    continue
                val = None
                for tok in c.get_tokens():
                    val = tok.spelling
                    break
                if val is not None:
                    init = f" = {val}"
                    break

    if elide_type:
        return f"{name}{dims_str}{init}"
    else:
        return f"{base_type} {name}{dims_str}{init}"

def emit_decl_stmt(node, indent):
    decls = []
    base_type = None
    for child in node.get_children():
        if child.kind == CursorKind.VAR_DECL:
            t = child.type.spelling.split('[')[0]
            if base_type is None:
                base_type = t
            decls.append(decl_to_string(child, elide_type=True))
    if base_type and decls:
        return f"{indent}{base_type} {', '.join(decls)};"
    else:
        return ''.join(emit_stmt(c, indent) for c in node.get_children())


def emit_stmt(node, indent=""):
    k = node.kind
    nl = "\n"
    IND = indent

    if k == CursorKind.COMPOUND_STMT:
        body = "".join(emit_stmt(c, IND + "    ") for c in node.get_children())
        return f"{IND}{{{nl}{body}{IND}}}{nl}"

    elif k == CursorKind.DECL_STMT:
        return emit_decl_stmt(node, IND) + nl

    elif k == CursorKind.VAR_DECL:
        return IND + decl_to_string(node) + ';' + nl

    elif k == CursorKind.IF_STMT:
        children = list(node.get_children())
        cond = emit_expr(children[0])
        then_part = emit_stmt(children[1], IND + "    ")
        res = f"{IND}if ({cond})"
        res += f"{nl}{then_part}"
        if len(children) > 2:
            else_part = emit_stmt(children[2], IND + "    ")
            res += f"{IND}else{nl}{else_part}"
        return res

    elif k == CursorKind.FOR_STMT:
        children = list(node.get_children())
        init = emit_stmt(children[0], '').rstrip('\n').rstrip(';').strip() if children else ''
        cond = emit_expr(children[1]) if len(children) > 1 else ''
        inc = emit_expr(children[2]) if len(children) > 2 else ''
        body = emit_stmt(children[3], IND + "    ") if len(children) > 3 else ''
        return f"{IND}for ({init}; {cond}; {inc})\n{body}"

    elif k == CursorKind.WHILE_STMT:
        children = list(node.get_children())
        cond = emit_expr(children[0])
        body = emit_stmt(children[1], IND + "    ")
        return f"{IND}while ({cond})\n{body}"

    elif k == CursorKind.DO_STMT:
        children = list(node.get_children())
        body = emit_stmt(children[0], IND + "    ")
        cond = emit_expr(children[1]) if len(children) > 1 else ''
        return f"{IND}do\n{body}{IND}while ({cond});{nl}"

    elif k == CursorKind.RETURN_STMT:
        children = list(node.get_children())
        ex = emit_expr(children[0]) if children else ""
        return f"{IND}return {ex};{nl}"

    elif k == CursorKind.CALL_EXPR:
        return IND + emit_expr(node) + ";" + nl

    elif k in (CursorKind.BINARY_OPERATOR, CursorKind.UNARY_OPERATOR):
        return IND + emit_expr(node) + ";" + nl

    elif k == CursorKind.BREAK_STMT:
        return IND + "break;" + nl

    elif k == CursorKind.CONTINUE_STMT:
        return IND + "continue;" + nl

    elif k == CursorKind.LABEL_STMT:
        body = "".join(emit_stmt(c, IND + "    ") for c in node.get_children())
        return f"{IND}{node.spelling}:{nl}{body}"

    return ''.join(emit_stmt(c, IND) for c in node.get_children())

def emit_function(node):
    ret_type = node.result_type.spelling
    name = node.spelling
    params = []
    for p in node.get_arguments():
        typ = p.type.spelling
        pname = p.spelling
        params.append(f"{typ} {pname}")
    sig = f"{ret_type} {name}({', '.join(params)})\n"
    stmts = [emit_stmt(c) for c in node.get_children() if c.kind == CursorKind.COMPOUND_STMT]
    return sig + ''.join(stmts)

def emit_translation_unit(root):
    code = ""
    for c in root.get_children():
        if c.kind == CursorKind.FUNCTION_DECL:
            code += emit_function(c)
        elif c.kind == CursorKind.VAR_DECL:
            code += emit_stmt(c)
        else:
            code += emit_stmt(c)
    return code
