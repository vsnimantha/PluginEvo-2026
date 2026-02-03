from clang.cindex import CursorKind
from .ast_utils import is_system_header,is_unwanted_macro

def print_astnode(node, indent=""):
    print(f"{indent}{node.kind}: spelling={repr(node.spelling)}, token_value={repr(node.token_value)}, type_name={repr(getattr(node, 'type_name', None))}")
    for child in node.children:
        print_astnode(child, indent + "  ")

def check_cursor_presence(tu, target_class="Car", target_method="display", dump_tokens=False):
    for cursor in tu.cursor.get_children():
        if cursor.kind == CursorKind.CLASS_DECL and cursor.spelling == target_class:
            for child in cursor.get_children():
                if child.kind == CursorKind.CXX_METHOD and child.spelling == target_method:
                    if dump_tokens:
                        dump_tokens_in_method(child)
                    print(f"\n Found method '{target_method}'")
                    for stmt in child.get_children():
                        print(f"  🔍 {stmt.kind} — {stmt.spelling}")

def dump_tokens_in_method(method_cursor):
    print("\n🔍 Tokens in method:")
    for token in method_cursor.get_tokens():
        print(f"{token.kind} — {token.spelling}")

def dump_ast(self, node=None, depth=0,source_code_path=None):
        if node is None:
            node = self.parse()
            if node is None:
                return

        # Only skip system headers/macros if NOT inside a method/function
        if not (
            node.kind == CursorKind.COMPOUND_STMT
            or (node.semantic_parent 
                and node.semantic_parent.kind in (CursorKind.CXX_METHOD, CursorKind.FUNCTION_DECL))
        ):
            if is_system_header(node) or is_unwanted_macro(node,source_code_path=source_code_path):
                return

        # Build display info
        info = f"{node.kind} — {node.spelling}"

        if node.kind in (
            CursorKind.INTEGER_LITERAL,
            CursorKind.FLOATING_LITERAL,
            CursorKind.STRING_LITERAL,
            CursorKind.CHARACTER_LITERAL,
        ):

            if node.kind.name in ("CALL_EXPR", "CXX_OPERATOR_CALL_EXPR"):
                tokens = list(node.get_tokens())
                if tokens:
                    expr = " ".join(t.spelling for t in tokens)
                    info += f"\n{'  ' * depth}🖋️ Reconstructed Expression: {expr}"

        print("  " * depth + info)

        # Always recurse in CompoundStmt so we see all inner statements
        for child in node.get_children():
            self.dump_ast(child, depth + 1)