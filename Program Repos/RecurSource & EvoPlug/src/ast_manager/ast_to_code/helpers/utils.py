from clang.cindex import CursorKind

def collect_type_args(n, emit_expr):
    if not hasattr(n, "children") or n.children is None:
        print(f"[DEBUG] collect_type_args: node {n} has no children")
        return []
    args = []
    stack = list(n.children)  # start from children, not the node itself
    while stack:
        cur = stack.pop()
        if cur.kind == CursorKind.TYPE_REF.name:
            args.append(emit_expr(cur, 0))
        elif cur.kind == CursorKind.TEMPLATE_REF.name:
            # Collect its args without calling emit_expr on the template node itself
            nested = collect_type_args(cur, emit_expr)
            args.append(f"{cur.spelling}<{', '.join(nested)}>")
        stack.extend(cur.children)
    return args



def _find_index(parent, node):
    for i, ch in enumerate(getattr(parent, "children", []) or []):
        if ch is node:
            return i
    return -1

def _emit_template_id_from(parent, start_idx, emit_expr):
    """
    Parse a template-id starting at either:
      - TEMPLATE_REF at start_idx, or
      - NAMESPACE_REF at start_idx followed by TEMPLATE_REF.
    Returns (text, next_index_after_consumed).
    """
    children = parent.children
    i = start_idx
    n = len(children)

    # Optional leading namespace
    ns = None
    if i < n and children[i].kind == CursorKind.NAMESPACE_REF.name:
        ns = children[i].spelling or ""
        i += 1

    # Must have TEMPLATE_REF now
    if i >= n or children[i].kind != CursorKind.TEMPLATE_REF.name:
        # Fallback: just return whatever we have at start_idx to avoid crashes
        txt = (children[start_idx].spelling or "")
        return txt, start_idx + 1

    tmpl_name = children[i].spelling or ""
    i += 1

    # Collect consecutive type-ish nodes as template arguments
    args = []
    while i < n:
        k = children[i].kind
        if k == CursorKind.TYPE_REF.name:
            # Simple type arg: T, U, Foo
            args.append(children[i].spelling or "")
            i += 1
        elif k == CursorKind.NAMESPACE_REF.name and (i + 1) < n and \
             children[i + 1].kind == CursorKind.TEMPLATE_REF.name:
            # Nested template: std::vector<T>, std::map<...>
            nested_txt, i = _emit_template_id_from(parent, i, emit_expr)
            args.append(nested_txt)
        else:
            break

    head = f"{tmpl_name}<{', '.join(args)}>"
    if ns:
        head = f"{ns}::{head}"
    return head, i

def emit_template_id_from_siblings(parent, start_idx, emit_expr):
    """
    Parse a template-id starting at index start_idx in parent's children.
    Returns (text, next_index_after_consumed).
    """
    ch = parent.children
    n = len(ch)
    i = start_idx

    ns = ""
    if i < n and ch[i].kind == CursorKind.NAMESPACE_REF.name:
        ns = ch[i].spelling or ""
        i += 1

    if not (i < n and ch[i].kind == CursorKind.TEMPLATE_REF.name):
        return None, start_idx

    tmpl = ch[i].spelling or ""
    i += 1

    args = []
    while i < n:
        kind = ch[i].kind
        if kind == CursorKind.TYPE_REF.name:
            args.append(ch[i].spelling or "")
            i += 1
        elif kind == CursorKind.NAMESPACE_REF.name and (i + 1) < n \
             and ch[i + 1].kind == CursorKind.TEMPLATE_REF.name:
            nested_txt, new_i = emit_template_id_from_siblings(parent, i, emit_expr)
            args.append(nested_txt)
            i = new_i
        else:
            break

    head = f"{tmpl}<{', '.join(args)}>"
    if ns:
        head = f"{ns}::{head}"
    return head, i
