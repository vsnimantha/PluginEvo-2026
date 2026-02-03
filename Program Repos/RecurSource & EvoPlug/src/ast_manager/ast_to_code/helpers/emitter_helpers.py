from clang.cindex import CursorKind

def emit_stream_chain(node,emit_expr):
    # node is CALL_EXPR for operator<< or >>
    op_node = node.children[1].children[0]  # OVERLOADED_DECL_REF
    op = "<<" if op_node.spelling == "operator<<" else ">>"

    # Left-hand side may itself be part of a chain
    lhs = emit_stream_chain(node.children[0]) if node.children[0].kind == CursorKind.CALL_EXPR.name else emit_expr(node.children[0])
    rhs = emit_expr(node.children[2])
    return f"{lhs} {op} {rhs}"

def emit_raw_tokens(node, indent=""):
    """
    Emit RAW_TOKENS captured from a COMPOUND_STMT, stripping braces and
    filtering out 'return ...;' so it doesn't duplicate RETURN_STMT output.
    """
    s = (node.spelling or "").strip()
    # Remove surrounding braces if present
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()

    if not s:
        return ""

    # Split by semicolon; keep order; filter empties
    stmts = [p.strip() for p in s.split(";") if p.strip()]
    # Avoid duplicating returns (RETURN_STMT will handle them)
    stmts = [p for p in stmts if not p.startswith("return ")]

    if not stmts:
        return ""

    return "".join(f"{indent}{p};\n" for p in stmts)