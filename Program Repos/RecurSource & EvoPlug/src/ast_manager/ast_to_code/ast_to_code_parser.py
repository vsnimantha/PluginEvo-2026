from clang.cindex import CursorKind
import re
from .helpers import constants,utils,emitter_helpers
from .helpers.formatter_core import code_formatter



def get_precedence(op):
    return constants.precedence.get(op, 0)

def emit_expr(node, parent_prec=0):
    k = node.kind
    # print(f"emit_expr: {k}, spelling={node.spelling}, token_value={node.token_value} , children_count={len(node.children)}") # Debugging line

    if k == CursorKind.UNEXPOSED_EXPR.name:
        if not node.children:
            return ""      
            
        if len(node.children) == 1:
            return emit_expr(node.children[0], parent_prec)
        elif len(node.children) == 2:
            left_child = node.children[0]
            right_child = node.children[1]
            left_expr = emit_expr(left_child, parent_prec)
            right_expr = emit_expr(right_child, parent_prec)
            if left_child.kind == CursorKind.DECL_REF_EXPR.name and left_child.spelling in ("cout", "cin"):
                op = "<<" if left_child.spelling == "cout" else ">>"

                return f"{left_expr} {op} {right_expr}"
            else:
                return f"{left_expr} {right_expr}"
        else:
            return "(" + ", ".join(emit_expr(c, 0) for c in node.children) + ")"


    elif k == CursorKind.BINARY_OPERATOR.name:
        if node.token_value:
            return node.token_value
        
        op = node.spelling
        if op in ("<<", ">>"):
            return f"{emit_expr(node.children[0])} {op} {emit_expr(node.children[1])}"
        
        lhs, rhs = node.children
        lhs_code = emit_expr(lhs, get_precedence(op))
        rhs_code = emit_expr(rhs, get_precedence(op) + 1)
        expr = f"{lhs_code} {op} {rhs_code}"
        if get_precedence(op) < parent_prec:
            return f"({expr})"
        else:
            return expr

    elif k == CursorKind.UNARY_OPERATOR.name:
        operand = emit_expr(node.children[0], 1000)
        op = node.spelling
        if op in ("++", "--") and node.token_value == "postfix":
            return f"{operand}{op}"
        else:
            return f"{op}{operand}"

    elif k ==CursorKind.INTEGER_LITERAL.name:
        return str(node.token_value)
    elif k == CursorKind.FLOATING_LITERAL.name:
        return str(node.token_value)
    elif k == CursorKind.CHARACTER_LITERAL.name:
        return node.token_value 
    elif k == CursorKind.STRING_LITERAL.name:
        return node.token_value 
    
    elif k == CursorKind.DECL_REF_EXPR.name:
        ns = None
        for ch in node.children:
            if ch.kind == CursorKind.NAMESPACE_REF.name:
                ns = ch.spelling
                break
        if ns:
            # Qualify with namespace
            return f"{ns}::{node.spelling}"
        else:
            # No namespace qualifier — just the identifier
            return node.spelling or ""

    elif k == CursorKind.ARRAY_SUBSCRIPT_EXPR.name:
        if len(node.children) >= 2:
            base, index = node.children
            return f"{emit_expr(base, 1000)}[{emit_expr(index, 0)}]"
        elif len(node.children) == 1:
            return f"{emit_expr(node.children[0], 1000)}[]"
        else:
            return "[]"
        


    elif k == CursorKind.CALL_EXPR.name:
        # Detect stream << or >>
        if 'operator<<' in (node.spelling or '') or 'operator>>' in (node.spelling or ''):
            lhs = emit_expr(node.children[0])
            rhs = emit_expr(node.children[-1])
            op = '<<' if '<<' in node.spelling else '>>'
            return f"{lhs} {op} {rhs}"
        # Or: unwrap if child[0] is another CALL_EXPR for operator<< and chain
        if (node.children and node.children[0].kind == CursorKind.CALL_EXPR.name
            and 'operator<<' in (node.children[0].spelling or '')):
            lhs = emit_expr(node.children[0])
            rhs = emit_expr(node.children[-1])
            return f"{lhs} << {rhs}"
        
        if 'operator->' in (node.spelling or ''):
            lhs = emit_expr(node.children[0])
            return f"{lhs}->"
        
        if 'operator!' in (node.spelling or ''):
            operand = emit_expr(node.children[0])
            return f"!{operand}"
        
        for op_name, symbol in constants.binary_operators.items():
            if op_name in (node.spelling or ""):
                lhs = emit_expr(node.children[0])
                rhs = emit_expr(node.children[-1])
                return f"{lhs} {symbol} {rhs}"


        children = node.children
        callee_node = children[0] if children else None

        if callee_node and callee_node.spelling == "basic_string":
            # Look for a STRING_LITERAL child
            for ch in node.children:
                if ch.kind == CursorKind.STRING_LITERAL.name:
                    return ch.token_value
            # Or unwrap UNEXPOSED_EXPR containing a literal
            for ch in node.children:
                if ch.kind == CursorKind.UNEXPOSED_EXPR.name and ch.children and ch.children[0].kind == CursorKind.STRING_LITERAL.name:
                    return ch.children[0].token_value

            # Guarded binary operator detection
        if callee_node and callee_node.kind == CursorKind.DECL_REF_EXPR.name:
            callee_name = callee_node.spelling or ""
            for op_name, symbol in constants.binary_operators.items():
                if callee_name == op_name:
                    lhs = emit_expr(children[1]) if len(children) > 1 else ""
                    rhs = emit_expr(children[-1]) if len(children) > 2 else ""
                    return f"{lhs} {symbol} {rhs}"

        # TYPE_REF value-init guard
        callee_type_args = utils.collect_type_args(callee_node, emit_expr)
        if callee_node.kind == CursorKind.TYPE_REF.name and (
            not callee_type_args or
            (len(callee_type_args) == 1 and (callee_node.spelling or "") == callee_type_args[0])
        ):
            func = emit_expr(callee_node, 1000)
            call_args = [emit_expr(c, 0) for c in children[1:]]
            return f"{func}({', '.join(call_args)})"

        # Namespace + template-id
        if callee_node.kind == CursorKind.NAMESPACE_REF.name and len(children) > 1 and \
        children[1].kind == CursorKind.TEMPLATE_REF.name:
            callee_txt, next_idx = utils.emit_template_id_from_siblings(node, 0, emit_expr)
            call_args = [emit_expr(c, 0) for c in children[next_idx:]]
            return f"{callee_txt}({', '.join(call_args)})"

        # Bare template-id
        if callee_node.kind == CursorKind.TEMPLATE_REF.name:
            callee_txt, next_idx = utils.emit_template_id_from_siblings(node, 0, emit_expr)
            call_args = [emit_expr(c, 0) for c in children[next_idx:]]
            return f"{callee_txt}({', '.join(call_args)})"

         # Case 1: direct literal callee
        if callee_node and callee_node.kind in (
            CursorKind.STRING_LITERAL.name,
            CursorKind.INTEGER_LITERAL.name,
            CursorKind.CHARACTER_LITERAL.name,
            CursorKind.FLOATING_LITERAL.name
        ):
            # print("[DEBUG] CALL_EXPR → direct literal callee:", callee_node.kind, callee_node.token_value)
            return emit_expr(callee_node, 1000)

        # Case 2: UNEXPOSED_EXPR wrapping a literal
        if callee_node and callee_node.kind == CursorKind.UNEXPOSED_EXPR.name and callee_node.children:
            inner = callee_node.children[0]
            if inner.kind in (
                CursorKind.STRING_LITERAL.name,
                CursorKind.INTEGER_LITERAL.name,
                CursorKind.CHARACTER_LITERAL.name,
                CursorKind.FLOATING_LITERAL.name
            ):
                # print("[DEBUG] CALL_EXPR → UNEXPOSED_EXPR wrapping literal:", inner.kind, inner.token_value)
                return emit_expr(inner, 1000)

        # print("DEBUG CALL_EXPR fallback:",
        #   "callee kind:", callee_node.kind if callee_node else None,
        #   "callee spelling:", callee_node.spelling if callee_node else None,
        #   "children kinds:", [ch.kind for ch in callee_node.children] if callee_node else [])

        # Fallback
        func = emit_expr(callee_node, 1000)
        if func.endswith(")"):
            return func
        
        if callee_type_args:
            func += "<" + ", ".join(callee_type_args) + ">"
        call_args = [emit_expr(c, 0) for c in children[1:]]
        return f"{func}({', '.join(call_args)})"
    
    
    elif k == CursorKind.TEMPLATE_REF.name:
        parent = getattr(node, "parent", None)
        if parent is not None:
            # Include preceding namespace if present by starting from it
            # Find our index in parent
            children = parent.children
            idx = next((i for i, ch in enumerate(children) if ch is node), -1)
            if idx >= 0:
                start_idx = idx - 1 if idx - 1 >= 0 and \
                    children[idx - 1].kind == CursorKind.NAMESPACE_REF.name else idx
                txt, _next_idx = utils._emit_template_id_from(parent, start_idx, emit_expr)
                return txt

        # Fallback (no parent/idx): just the name with any args directly under node (rare)
        tmpl_name = node.spelling or ""
        type_args = []  # no safe sibling scan available here
        return f"{tmpl_name}<{', '.join(type_args)}>" if type_args else tmpl_name

    elif k == CursorKind.PAREN_EXPR.name:
        return f"({emit_expr(node.children[0], 0)})"
    
    elif k == CursorKind.MEMBER_REF_EXPR.name:
        member = (node.spelling or "").strip()

        # If this is an implicit conversion, skip it entirely
        if member in constants.implicit_ops:
            return emit_expr(node.children[0], 1000) if node.children else ""
        

        base = emit_expr(node.children[0], 1000) if node.children else ""
        if base:
            sep = "" if base.endswith("->") else "."
            return f"{base}{sep}{member}"
        return member

    elif k == CursorKind.INIT_LIST_EXPR.name:
        return '{' + ', '.join(emit_expr(child, 0) for child in node.children) + '}'
    
    elif k == CursorKind.OVERLOADED_DECL_REF.name:
        # print(f"Overloaded decl ref: {node.spelling}, token_value={node.token_value}") # Debugging line
        if node.spelling in ("operator<<", "operator>>"):
            op = "<<" if node.spelling == "operator<<" else ">>"
            return op
        else:
            # Handle other overloaded decl refs
            return node.spelling or ""
    elif k == CursorKind.CXX_BOOL_LITERAL_EXPR.name:
        return node.token_value
    

    else:
        return node.spelling or ""
    

def extract_initializer(node, indent=""):
    if node.kind == CursorKind.INIT_LIST_EXPR.name:
        items = [extract_initializer(child, indent + "    ") for child in node.children]
        if any(c.kind == CursorKind.INIT_LIST_EXPR.name for c in node.children):
            inner = (",\n" + indent + "    ").join(items)
            return "{\n" + indent + "    " + inner + "\n" + indent + "}"
        else:
            return "{" + ", ".join(items) + "}"
    elif node.kind in (CursorKind.INTEGER_LITERAL.name, CursorKind.FLOATING_LITERAL.name, CursorKind.CHARACTER_LITERAL.name, CursorKind.STRING_LITERAL.name):
        return emit_expr(node)
    else:
        return emit_expr(node)


def decl_to_string(decl, elide_type=False):
    name = decl.spelling
    t = getattr(decl, 'type_name', None) or "int"
    init = ""
    dims = []



    # Check if 't' contains array dimensions like ""
    is_array = '[' in t and ']' in t

    if is_array:
        # Extract base type and dims from type_name
        m = re.match(r'([a-zA-Z_][\w\s\*]*)(\[.*\])?', t)
        base_type = m.group(1).strip() if m else t
        dims = re.findall(r'\[([0-9]*)\]', t)
    else:
        base_type = t

    for c in decl.children:
        if c.kind == CursorKind.INTEGER_LITERAL.name:
            val = str(c.token_value)
            if is_array:
                if val not in dims:
                    dims.append(val)
            else:
                init = f" = {val}"
        elif c.kind == CursorKind.INIT_LIST_EXPR.name:
            init = f" = {extract_initializer(c)}"

        elif c.kind == CursorKind.UNEXPOSED_EXPR.name and c.children:
            # If all children are calls/exprs, treat as a comma‑separated argument list
            if all(ch.kind == CursorKind.CALL_EXPR.name for ch in c.children):
                arg_texts = [emit_expr(ch) for ch in c.children]
                init = f"({', '.join(arg_texts)})"
            else:
                # Fallback to old single/other behaviour
                inner = c.children[0]
                if inner.kind == CursorKind.CALL_EXPR.name:
                    callee = emit_expr(inner.children[0])
                    args = [emit_expr(arg) for arg in inner.children[1:]]
                    if base_type.strip().endswith("std::thread") and callee != base_type:
                        init = f"({callee}, {', '.join(a for a in args if a)})"
                    else:
                        init = f"({', '.join([callee] + [a for a in args if a])})"
                else:
                    expr = emit_expr(inner)
                    if expr:
                        init = f" = {expr}"


        elif c.kind == CursorKind.CALL_EXPR.name:
            callee_name = (c.spelling or "").strip()
            args = [emit_expr(arg) for arg in c.children]
            type_short = strip_templates(base_type.split("::")[-1])
            callee_short = strip_templates(callee_name.split("::")[-1])

            callee_short_basic_type=""
            parts = callee_short.split("_", 1)
            if len(parts) > 1:
                callee_short_basic_type = strip_templates(parts[1])
            else:
                callee_short_basic_type = strip_templates(parts[0])

            skip_init = not args and (
                callee_short == type_short or
                callee_short_basic_type == type_short
            )
            init = "" if skip_init else f"({', '.join(a for a in args if a)})"


        elif c.kind == CursorKind.UNEXPOSED_EXPR.name and c.children:
            inner = c.children[0]
            if inner.kind == CursorKind.CALL_EXPR.name:
                callee = emit_expr(inner.children[0])
                args = [emit_expr(a) for a in inner.children[1:]]
                if base_type.strip().endswith("std::thread") and callee != base_type:
                    init = f"({callee}, {', '.join(a for a in args if a)})"
                else:
                    init = f"({', '.join([callee] + [a for a in args if a])})"
                    

        elif c.kind not in (
            CursorKind.NAMESPACE_REF.name,
            CursorKind.TYPE_REF.name,
            CursorKind.TEMPLATE_REF.name
        ):
            # Fallback: some other expression as an initializer
            expr = emit_expr(c)
            if expr:
                init = f" = {expr}"



    dims_str = ''.join(f'[{d}]' for d in dims)
    if elide_type:
        return f"{name}{dims_str}{init}".strip()
    else:
        return f"{base_type} {name}{dims_str}{init}".strip()



def emit_decl_stmt(node, indent):
    decls = []
    base_type = None
    for child in node.children:
        if child.kind == CursorKind.VAR_DECL.name:
            # print(f"Processing VAR_DECL: {child.spelling}, type={getattr(child, 'type_name', None)}")  # Debugging line
            t = getattr(child, 'type_name', None)
            if base_type is None:
                    m = re.match(r'^\s*([^\[]+)\s*((?:\[[^\]]*\])*)\s*$', t)
                    if m:
                        base_type = m.group(1).strip()   # "bool"
                    else:
                        base_type = t.strip()
                # base_type = t
            decls.append(decl_to_string(child, elide_type=True))
            
    # print(f"Emitting decl_stmt with base_type={base_type} and decls={decls}")  # Debugging line
    if base_type and decls:
        return f"{indent}{base_type} {', '.join(decls)};"
    else:
        return ''.join(emit_stmt(c, indent) for c in node.children)
    
def emit_single_decl(node):
    type_name = getattr(node, 'type_name', 'auto')
    name = node.spelling or ''
    return f"{type_name} {name}"


def emit_stmt(node, indent=""):
    # print(f"emit_stmt: {node.kind}, spelling={node.spelling}, token_value={getattr(node, 'token_value', '')}")  # Debugging line
    k = node.kind
    nl = "\n"
    IND = indent

    if k == CursorKind.COMPOUND_STMT.name:
        children = node.children
        raw_nodes = [c for c in children if c.kind == "RAW_TOKENS"]
        raw_emitted = set()

        out = [IND + "{\n"]
        for ch in children:
            if ch.kind == CursorKind.RETURN_STMT.name:
                # Emit any pending RAW_TOKENS just before the return
                for rn in raw_nodes:
                    if rn not in raw_emitted:
                        out.append(emitter_helpers.emit_raw_tokens(rn, IND + "    "))
                        raw_emitted.add(rn)
                out.append(emit_stmt(ch, IND + "    "))
            elif ch.kind == "RAW_TOKENS":
                continue  # Defer RAW_TOKENS emission until placement time
            else:
                out.append(emit_stmt(ch, IND + "    "))

        # If RAW_TOKENS remain and no return was encountered
        for rn in raw_nodes:
            if rn not in raw_emitted:
                out.append(emitter_helpers.emit_raw_tokens(rn, IND + "    "))

        out.append(IND + "}\n")
        return "".join(out)


    elif k == CursorKind.DECL_STMT.name:
        return emit_decl_stmt(node, IND) + nl
    elif k == CursorKind.VAR_DECL.name:
        return IND + decl_to_string(node) + ';' + nl
    elif k == CursorKind.IF_STMT.name:
        cond = emit_expr(node.children[0])

        then_node = node.children[1]
        if then_node.kind == CursorKind.COMPOUND_STMT.name:
            then_part = emit_stmt(then_node, IND + "    ")
            res = f"{IND}if ({cond}) {then_part}"
        else:
            # either emit as a single stmt or wrap in braces
            stmt = emit_stmt(then_node, IND + "    ")
            # res = f"{IND}if ({cond})\n{stmt}"
            res = f"{IND}if ({cond}) {{\n{stmt}{IND}}}\n"

        if len(node.children) > 2:
            else_node = node.children[2]
            if else_node.kind == CursorKind.COMPOUND_STMT.name:
                else_part = emit_stmt(else_node, IND + "    ")
                res += f"{IND}else {else_part}"
            else:
                stmt = emit_stmt(else_node, IND + "    ")
                res += f"{IND}else {{\n{stmt}{IND}}}\n"

        return res


    elif k == CursorKind.FOR_STMT.name:
        children = node.children
        init = emit_stmt(children[0], '').rstrip().rstrip(';').strip() if len(children) > 0 else ''
        cond = emit_expr(children[1]) if len(children) > 1 else ''
        inc = emit_expr(children[2]) if len(children) > 2 else ''
        body = emit_stmt(children[3], IND + "    ") if len(children) > 3 else ''
        return f"{IND}for ({init}; {cond}; {inc})\n{body}"
    elif k == CursorKind.WHILE_STMT.name:
        cond = emit_expr(node.children[0])
        body = emit_stmt(node.children[1], IND + "    ")
        return f"{IND}while ({cond})\n{body}"
    elif k ==CursorKind.DO_STMT.name:
        body = emit_stmt(node.children[0], IND + "    ")
        cond = emit_expr(node.children[1]) if len(node.children) > 1 else ''
        return f"{IND}do\n{body}{IND}while ({cond});{nl}"
    elif k == CursorKind.RETURN_STMT.name:
        # 1) Prefer explicit child expression
        if node.children:
            ex = emit_expr(node.children[0]).strip()
            return f"{IND}return {ex};{nl}" if ex else f"{IND}return;{nl}"

        # 2) Fallback to this node’s own token_value
        tv = getattr(node, "token_value", None)
        if tv:
            tv = tv.strip()
            if not tv.startswith("return"):
                tv = f"return {tv}"
            if not tv.endswith(";"):
                tv += ";"
            return IND + tv + nl
        
        # 3) Absolute last resort
        return f"{IND}return;{nl}"

    elif k == CursorKind.CALL_EXPR.name:
        # print(f"Processing CALL_EXPR: {node.spelling}")  # Debugging line
        tv = getattr(node, 'token_value', None)
        if tv:
            tv = tv.strip()
            if not tv.endswith(";"):
                tv += ";"
            return IND + tv + nl
        return IND + emit_expr(node) + ";" + nl
        # return IND + emit_expr(node) + ";" + nl
    elif k == CursorKind.BINARY_OPERATOR.name:
        # binary operator: two children
        lhs = emit_expr(node.children[0])
        rhs = emit_expr(node.children[1])
        op = node.token_value or node.spelling or ""
        return IND + f"{lhs} {op} {rhs};{nl}"

    elif k == CursorKind.UNARY_OPERATOR.name:
        target = emit_expr(node.children[0])
        tv = getattr(node, 'token_value', "")
        if tv == "postfix":
            return IND + f"{target}++;{nl}"
        elif tv == "prefix":
            return IND + f"++{target};{nl}"
        else:
            # generic unary operator like "-" or "!"
            op = node.spelling or tv
            return IND + f"{op}{target};{nl}"

    elif k == CursorKind.BREAK_STMT.name:
        return IND + "break;" + nl
    elif k == CursorKind.CONTINUE_STMT.name:
        return IND + "continue;" + nl
    elif k == CursorKind.LABEL_STMT.name:
        body = "".join(emit_stmt(c, IND + "    ") for c in node.children)
        return f"{IND}{node.spelling}:{nl}{body}"
    elif k == CursorKind.SWITCH_STMT.name:
        cond = emit_expr(node.children[0]) if node.children else ""
        body = emit_stmt(node.children[1], IND) if len(node.children) > 1 else ""
        return f"{IND}switch ({cond})\n{body}"
    elif k == CursorKind.CASE_STMT.name:
        label_expr = emit_expr(node.children[0]) if node.children else ""
        stmts = "".join(emit_stmt(c, IND + "    ") for c in node.children[1:])
        return f"{IND}case {label_expr}:\n{stmts}"
    elif k == CursorKind.DEFAULT_STMT.name:
        stmts = "".join(emit_stmt(c, IND + "    ") for c in node.children)
        return f"{IND}default:\n{stmts}"
    elif k == CursorKind.UNEXPOSED_EXPR.name:
        tv = getattr(node, 'token_value', None)
        if tv:
            tv = tv.strip()
            if not tv.endswith(";"):
                tv += ";"
            return IND + tv + nl
        
    # Could be a top-level stream chain
        if (len(node.children) >= 2
            and node.children[1].kind == CursorKind.DECL_REF_EXPR.name
            and node.children[1].children
            and node.children[1].children[0].kind == CursorKind.OVERLOADED_DECL_REF.name
            and node.children[1].children[0].spelling in ("operator<<", "operator>>")):
            return indent + emitter_helpers.emit_stream_chain(node,emit_expr) + ";\n"
        else:
            return indent + emit_expr(node) + ";\n"

    elif k == CursorKind.CXX_FOR_RANGE_STMT.name:
        if len(node.children) >= 3:
            loop_var_decl = emit_single_decl(node.children[0])
            range_expr = emit_expr(node.children[1])
            body_stmt = emit_stmt(node.children[2],IND + "    ")
            return f"for ({loop_var_decl} : {range_expr}) {body_stmt}"

    else:
        return ''.join(emit_stmt(c, IND) for c in node.children)


def emit_class_decl(node, indent=""):
    name = node.spelling
    members = []
    current_access = ""

    for child in node.children:
        kind = child.kind

        if kind == CursorKind.CXX_ACCESS_SPEC_DECL.name:
            access = (child.spelling or "").strip()
            if access and access != current_access:
                members.append(f"{indent}{access}:\n")
                current_access = access
            continue

        if kind == CursorKind.FIELD_DECL.name:
            t = getattr(child, 'type_name', "") or ""
            members.append(f"{indent}    {t} {child.spelling};\n")
            continue

        if kind in (CursorKind.CXX_METHOD.name,
                    CursorKind.CONSTRUCTOR.name,
                    CursorKind.DESTRUCTOR.name):

            is_method = (kind == CursorKind.CXX_METHOD.name)
            ret_type = (child.type_name or "void").split('(')[0].strip() if is_method else ""

            # Name (strip <T> for in-class ctor/dtor)
            sig_name = child.spelling if is_method else ctor_name_in_class(child, name)

            # Params (preserve defaults)
            params = []
            for p in child.children:
                if p.kind == CursorKind.PARM_DECL.name:
                    params.append(emit_param_with_default(p))

            # Member initializer list (e.g., data(rows, std::vector<T>(cols, init)))
            init_list = ""
            if is_ctor(child):
                inits = collect_member_inits(child)
                if inits:
                    init_list = " : " + ", ".join(inits)

            # Body
            body_node = next((c for c in child.children
                              if c.kind == CursorKind.COMPOUND_STMT.name), None)
            body_code = emit_stmt(body_node, indent + "    ") if body_node else "{}\n"

            prefix = f"{ret_type} " if ret_type else ""
            members.append(f"{indent}    {prefix}{sig_name}({', '.join(params)}){init_list} {body_code}")
            continue

        # Fallback
        members.append(emit_stmt(child, indent + "    "))

    return f"{indent}class {name} {{\n{''.join(members)}{indent}}};\n"



def emit_function(node):
    # Determine return type correctly for functions/methods
    if node.kind in (
        CursorKind.FUNCTION_DECL.name,
        CursorKind.CXX_METHOD.name,
        CursorKind.CONSTRUCTOR.name,
        CursorKind.DESTRUCTOR.name,
    ):
        # Prefer result_type for accurate return type
        full_type = getattr(node, "result_type", None) or node.type_name or "void"
    else:
        full_type = node.type_name or "void"

    # Keep the full type string
    ret_type = str(full_type)

    name = node.spelling
    params = []

    for c in node.children:
        if c.kind == CursorKind.PARM_DECL.name:
            ptype = c.type_name or "int"
            pname = c.spelling
            params.append(f"{ptype} {pname}".strip())

    body_node = next(
        (c for c in node.children if c.kind == CursorKind.COMPOUND_STMT.name),
        None
    )
    body_code = emit_stmt(body_node) if body_node else ""

    sig = f"{ret_type} {name}({', '.join(params)})\n"
    
    return sig + body_code


def emit_class_template_decl(node):
    code = ""

    # collect template parameters
    params = []
    for child in node.children:
        if child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER.name:
            params.append(f"typename {child.spelling}")
        elif child.kind == "NON_TYPE_TEMPLATE_PARAMETER":
            type_ref = None
            for grandchild in child.children:
                if grandchild.kind == CursorKind.TYPE_REF.name:
                    type_ref = grandchild.spelling
                    break
            if type_ref:
                params.append(f"{type_ref} {child.spelling}")
        elif child.kind == CursorKind.TEMPLATE_TEMPLATE_PARAMETER.name:
            params.append(f"template<typename> class {child.spelling}")

    # emit template line
    code += f"template<{', '.join(params)}>\n" if params else "template<>\n"

    # delegate to your existing class printer
    code += emit_class_decl(node)

    return code



def emit_translation_unit(root,language_extension=".cpp",format_code=True):
    code = ""
    if root is not None:
        for c in root.children:
            if c is None:
                continue

            if c.kind == CursorKind.INCLUSION_DIRECTIVE.name:
                name = c.spelling
                if not (name.startswith("<") or name.startswith('"')):
                    name = f"<{name}>"
                code += f"#include {name}\n"
            elif c.kind == CursorKind.USING_DIRECTIVE.name:
                code += f"using namespace {c.children[0].spelling};\n"
            elif c.kind == CursorKind.CLASS_DECL.name:
                code += emit_class_decl(c) + "\n"
            elif c.kind == CursorKind.FUNCTION_DECL.name:
                code += emit_function(c)
            elif c.kind == CursorKind.CLASS_TEMPLATE.name:
                code+= emit_class_template_decl(c)

            else:
                code += emit_stmt(c)

    # formatted_code = code_formatter.format_cpp_code_with_clang_format(code,language_extension)
    # print("Formatted code:\n", formatted_code)  # Debugging line

    return code if not format_code else code_formatter.format_cpp_code_with_clang_format(code,language_extension)






def strip_templates(name: str) -> str:
    return re.sub(r"<.*>", "", name).strip()

def is_ctor(n): return n.kind == CursorKind.CONSTRUCTOR.name
def is_dtor(n): return n.kind == CursorKind.DESTRUCTOR.name

def ctor_name_in_class(node, class_name):
    # node.spelling is "Matrix<T>" — strip template args
    base = strip_templates(node.spelling) if node.spelling else class_name
    return base or class_name

def emit_param_with_default(p):
    t = getattr(p, "type_name", "") or ""
    n = p.spelling or ""
    # Pick the first non-type child as default expr (e.g., CALL_EXPR for T())
    default_child = next(
        (c for c in p.children
         if c.kind not in (CursorKind.TYPE_REF.name,
                           CursorKind.TEMPLATE_REF.name,
                           CursorKind.NAMESPACE_REF.name)),
        None
    )
    if default_child is not None:
        return f"{t} {n} = {emit_expr(default_child)}".strip()
    return f"{t} {n}".strip()

def render_init_args(n):
    # The init args in your AST appear as UNEXPOSED_EXPR with two children:
    # rows, and CALL_EXPR std::vector<T>(cols, init). Join with ", ".
    if n.kind == CursorKind.UNEXPOSED_EXPR.name:
        parts = [emit_expr(ch) for ch in n.children]
        parts = [p for p in parts if p]  # drop empties
        return ", ".join(parts)
    return emit_expr(n)

def collect_member_inits(ctor_node):
    inits = []
    children = ctor_node.children
    i = 0
    while i < len(children):
        c = children[i]
        if c.kind == CursorKind.COMPOUND_STMT.name:
            break
        # Pair MEMBER_REF <name> with the next node as its arg list
        if c.kind == CursorKind.MEMBER_REF.name:
            name = c.spelling
            # next non-PARM node as args
            j = i + 1
            while j < len(children) and children[j].kind == CursorKind.PARM_DECL.name:
                j += 1
            if j < len(children) and children[j].kind != CursorKind.COMPOUND_STMT.name:
                args = render_init_args(children[j])
                inits.append(f"{name}({args})")
                i = j + 1
                continue
        i += 1
    return inits
