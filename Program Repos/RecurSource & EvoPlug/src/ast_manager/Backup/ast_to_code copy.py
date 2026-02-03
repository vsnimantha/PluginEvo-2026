class ASTReconstructor:
    def __init__(self, root_node=None):
        self.root = root_node

    def reconstruct(self):
        if not self.root:
            raise ValueError("Root node is not set.")
        return "\n".join(self._process_node(self.root))

    def _process_node(self, node, indent=0):
        tab = "    " * indent
        lines = []

        kind = node.kind.name

        if kind == "TRANSLATION_UNIT":
            for child in node.get_children():
                lines += self._process_node(child, indent)

        elif kind == "FUNCTION_DECL":
            ret_type = node.result_type.spelling
            name = node.spelling
            args = [f"{arg.type.spelling} {arg.spelling or 'arg'}" for arg in node.get_arguments()]
            lines.append(f"{ret_type} {name}({', '.join(args)}) {{")
            for child in node.get_children():
                lines += self._process_node(child, indent + 1)
            lines.append(f"{tab}}}")

        elif kind == "COMPOUND_STMT":
            for child in node.get_children():
                lines += self._process_node(child, indent)

        elif kind == "RETURN_STMT":
            expr = next(node.get_children(), None)
            expr_code = self._reconstruct_expr(expr) if expr else ""
            lines.append(f"{tab}return {expr_code};")

        elif kind == "CALL_EXPR":
            tokens = list(node.get_tokens())
            code = " ".join(t.spelling for t in tokens)
            lines.append(f"{tab}{code};")

        elif kind == "VAR_DECL":
            var_type = node.type.spelling
            var_name = node.spelling
            init = next(node.get_children(), None)
            if init:
                init_code = self._reconstruct_expr(init)
                lines.append(f"{tab}{var_type} {var_name} = {init_code};")
            else:
                lines.append(f"{tab}{var_type} {var_name};")

        elif kind == "DECL_STMT":
            for child in node.get_children():
                lines += self._process_node(child, indent)

        elif kind == "IF_STMT":
            children = list(node.get_children())
            if children:
                cond = self._reconstruct_expr(children[0])
                lines.append(f"{tab}if ({cond}) {{")
                lines += self._process_node(children[1], indent + 1)
                lines.append(f"{tab}}}")
                
                if len(children) > 2:
                    else_child = children[2]
                    if else_child.kind.name == "IF_STMT":
                        else_lines = self._process_node(else_child, indent)
                        else_lines[0] = else_lines[0].replace(tab + "if", "else if")
                        lines += else_lines
                    else:
                        lines.append(f"{tab}else {{")
                        lines += self._process_node(else_child, indent + 1)
                        lines.append(f"{tab}}}")

        elif kind == "SWITCH_STMT":
            children = list(node.get_children())
            if children:
                cond = self._reconstruct_expr(children[0])
                lines.append(f"{tab}switch ({cond}) {{")
                for child in children[1:]:
                    lines += self._process_node(child, indent + 1)
                lines.append(f"{tab}}}")

        elif kind == "CASE_STMT":
            children = list(node.get_children())
            if children:
                case_expr = self._reconstruct_expr(children[0])
                lines.append(f"{tab}case {case_expr}:")
                for child in children[1:]:
                    lines += self._process_node(child, indent + 1)

        elif kind == "DEFAULT_STMT":
            lines.append(f"{tab}default:")
            for child in node.get_children():
                lines += self._process_node(child, indent + 1)

        elif kind == "BREAK_STMT":
            lines.append(f"{tab}break;")

        elif kind == "PARM_DECL":
            param_type = node.type.spelling
            param_name = node.spelling or "<param>"
            lines.append(f"{tab}// param: {param_type} {param_name}")

        else:
            # For debugging unhandled nodes
            # print(f"Unhandled node kind: {kind} → {node.spelling}")
            for child in node.get_children():
                lines += self._process_node(child, indent)

        return lines

    def _reconstruct_expr(self, node):
        kind = node.kind.name

        if kind in ["INTEGER_LITERAL", "FLOATING_LITERAL", "STRING_LITERAL", "CHARACTER_LITERAL"]:
            tokens = list(node.get_tokens())
            return tokens[0].spelling if tokens else "<lit>"

        elif kind == "DECL_REF_EXPR":
            return node.spelling

        elif kind == "UNEXPOSED_EXPR":
            children = list(node.get_children())
            if children:
                # Handle operator expressions
                if node.spelling == "operator":
                    op = self._extract_operator(node)
                    children_exprs = [self._reconstruct_expr(c) for c in children]
                    return f" {op} ".join(children_exprs)
                return self._reconstruct_expr(children[0])
            return "<unexposed>"

        elif kind == "BINARY_OPERATOR":
            children = list(node.get_children())
            if len(children) == 2:
                left = self._reconstruct_expr(children[0])
                right = self._reconstruct_expr(children[1])
                op = self._extract_operator(node)
                return f"{left} {op} {right}"
            return "<binary_expr>"

        else:
            return node.spelling or "<expr>"

    def _extract_operator(self, node):
        tokens = list(node.get_tokens())
        for t in tokens:
            if t.kind.name == "PUNCTUATION":
                return t.spelling
        return "?"