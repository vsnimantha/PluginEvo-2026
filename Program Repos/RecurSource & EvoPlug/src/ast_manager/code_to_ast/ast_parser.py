import os
import platform
import subprocess
import clang.cindex
import re

from clang.cindex import CursorKind,TokenKind
from clang.cindex import AccessSpecifier

from src.ast_manager.common.clang_locator import auto_configure_libclang
from src.ast_manager.common.ast_node import ASTNode

from src.ast_manager.code_to_ast.helpers import ast_utils
from src.ast_manager.code_to_ast.helpers import ast_debug
from src.ast_manager.code_to_ast.helpers import ast_serialiser

auto_configure_libclang()

class ASTParser:
    def __init__(self, source_code_path, language="c", std="c11"):
        self.source_code_path = source_code_path
        self.language = language
        self.std = std
        self.index = clang.cindex.Index.create()
        self.args = self._build_clang_args()
        self.args_macros = self._build_clang_args_macros()

    # -----------------------------
    def _build_clang_args(self):
        args = []

        if self.language == "c++":
            if platform.system() == "Darwin":
                sdk_path = subprocess.check_output(["xcrun", "--show-sdk-path"]).decode().strip()

                # args = [
                #     "-x", "c++",
                #     "-std=c++17",
                #     "-isysroot", sdk_path,
                #     "-I" + os.path.join(sdk_path, "usr/include"),
                #     "-I/Library/Developer/CommandLineTools/usr/include",
                #     "-I/Library/Developer/CommandLineTools/usr/include/c++/v1",
                #     "-stdlib=libc++"
                # ]
                args = [
                    "-x", "c++",
                    "-std=c++17",
                    "-isysroot", sdk_path,
                    "-I" + os.path.join(sdk_path, "usr/include/c++/v1"),
                    "-I" + os.path.join(sdk_path, "usr/include"),
                    "-stdlib=libc++",
                    "-resource-dir", "/Library/Developer/CommandLineTools/usr/lib/clang/17",
                ]

            #Might be useful later to block the headerfiles #TODO::CHECK WITH MULTIPLE MACHINES BEFORE AN ACTUAL RELEASE
             #   "-nostdinc++",                   #  Block ALL C++ stdlib (GCC/Clang)
             # "-nostdinc",                     #  Block ALL system headers  
            elif platform.system() == "Linux":
                args = [
                    "-x", "c++",
                    f"-std={self.std}",
                    "-Wno-everything",
                    "-I/usr/include",
                    "-I/usr/include/x86_64-linux-gnu",
                    "-I/usr/include/c++/11",
                    "-I/usr/include/x86_64-linux-gnu/c++/11",
                ]
        else:
            args = [
                "-x", self.language,
                f"-std={self.std}",
                "-nostdinc",
                "-nostdlibinc",
                "-nobuiltininc",
                "-Wno-everything",
            ]
            if platform.system() == "Darwin":
                args.append("-I/Library/Developer/CommandLineTools/usr/include/c++/v1")
            elif platform.system() == "Linux":
                args.append("-I/usr/include/c++/11")

        return args

    # -----------------------------
    def _build_clang_args_macros(self):
        args = ["-x", self.language, f"-std={self.std}", "-Wno-everything"]

        if self.language == "c++":
            if platform.system() == "Darwin":
                sdk_path = subprocess.check_output(
                    ["xcrun", "--show-sdk-path"]
                ).decode().strip()
                args.extend([
                    "-isysroot", sdk_path,
                    "-I" + os.path.join(sdk_path, "usr/include"),
                    "-I/Library/Developer/CommandLineTools/usr/include/c++/v1",
                ])

            elif platform.system() == "Linux":
                args.extend([
                    "-I/usr/include",
                    "-I/usr/include/x86_64-linux-gnu",
                    "-I/usr/include/c++/11",
                    "-I/usr/include/x86_64-linux-gnu/c++/11",
                ])
        else:
            if platform.system() == "Darwin":
                sdk_path = subprocess.check_output(
                    ["xcrun", "--show-sdk-path"]
                ).decode().strip()
                args.extend([
                    "-isysroot", sdk_path,
                    "-I" + os.path.join(sdk_path, "usr/include"),
                ])
            elif platform.system() == "Linux":
                args.extend([
                    "-I/usr/include",
                    "-I/usr/include/x86_64-linux-gnu",
                ])

        return args

    # -----------------------------
    def parse(self, macros=False):
        # print("Library file:", clang.cindex.Config.library_file)  # Should now show the path
        # print("Library path:", clang.cindex.Config.library_path)   # Directory containing it
        if not os.path.exists(self.source_code_path):
            raise FileNotFoundError(f"Source file not found: {self.source_code_path}")

        parse_args = self.args_macros if macros else self.args

        try:
            # tu = self.index.parse(self.source_code_path, args=parse_args) # This won't dump all the macro information
            tu = self.index.parse(self.source_code_path, args=parse_args,options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

            #Debugging: Print the AST structure
            # self.check_cursor_presence(tu)

        except clang.cindex.TranslationUnitLoadError as e:
            print("Clang failed to parse the source file. Check syntax or compiler args.")
            print(e)
            return None
        except Exception as e:
            print("Clang failed to parse the source file. Check syntax or compiler args.")
            print(e)
            return None
        
        if tu.diagnostics:
            print("\nClang Diagnostics:")
            for diag in tu.diagnostics:
                print(f"  - {diag}")
        
        return tu.cursor
    
  
    def dump_ast(self, node=None, depth=0):
        ast_debug.dump_ast(self, node, depth, source_code_path=self.source_code_path)

    def clang_cursor_to_astnode(self, cursor):
        # Skip unwanted cursors
        if cursor is None:
            return None

        if ast_utils.is_system_header(cursor) or ast_utils.is_unwanted_macro(cursor, self.source_code_path):
            return None

        kind_name = cursor.kind.name
        type_name = None
        token_value = None
        spelling = cursor.spelling or ""

        # Derive type_name for declarations and functions
        if cursor.kind in (
            CursorKind.VAR_DECL,
            CursorKind.PARM_DECL,
            CursorKind.FIELD_DECL,
        ):
            try:
                type_name = cursor.type.spelling
            except Exception:
                type_name = None

        elif cursor.kind in (
            CursorKind.FUNCTION_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.CONSTRUCTOR,
            CursorKind.DESTRUCTOR,
        ):
            try:
                type_name = cursor.result_type.spelling
            except Exception:
                type_name = None

        # Literal token values
        if cursor.kind in (
            CursorKind.INTEGER_LITERAL,
            CursorKind.FLOATING_LITERAL,
            CursorKind.STRING_LITERAL,
            CursorKind.CHARACTER_LITERAL,
            CursorKind.CXX_BOOL_LITERAL_EXPR,
        ):
            try:
                tokens = list(cursor.get_tokens())
                if tokens:
                    token_value = tokens[0].spelling
            except Exception:
                pass

        # Unary operator: detect ++/-- prefix/postfix and set operator spelling
        if cursor.kind == CursorKind.UNARY_OPERATOR:
            try:
                tokens = list(cursor.get_tokens())
            except Exception:
                tokens = []
            op_token = None
            for t in tokens:
                if t.spelling in ("++", "--"):
                    op_token = t.spelling
                    break
            token_value = None
            if len(tokens) == 2:
                if tokens[0].spelling in ("++", "--"):
                    token_value = "prefix"
                elif tokens[1].spelling in ("++", "--"):
                    token_value = "postfix"
            if op_token:
                spelling = op_token

        # Capture raw tokens for tricky expressions (moved out of UNARY_OPERATOR)
        if cursor.kind in (
            CursorKind.BINARY_OPERATOR,
            CursorKind.CALL_EXPR,
            CursorKind.UNEXPOSED_EXPR,
        ):
            try:
                toks = [t.spelling for t in cursor.get_tokens()]
                if toks:
                    token_value = " ".join(toks)
            except Exception:
                pass

        # Build children (always keep COMPOUND_STMT if present)
        children = []
        for c in cursor.get_children():
            if c.kind == CursorKind.COMPOUND_STMT:
                child_node = self.clang_cursor_to_astnode(c)
                if child_node:
                    children.append(child_node)
                continue

            child_node = self.clang_cursor_to_astnode(c)
            if child_node:
                children.append(child_node)

        # For COMPOUND_STMT, reinsert RAW_TOKENS gap fillers
        if cursor.kind == CursorKind.COMPOUND_STMT:
            children = []
            for c in cursor.get_children():
                child_node = self.clang_cursor_to_astnode(c)
                if child_node:
                    children.append(child_node)
            children = self.__insert_gap_filler_raw_tokens(cursor, children)

        # Map access specifiers
        if cursor.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
            if cursor.access_specifier == AccessSpecifier.PRIVATE:
                spelling = "private"
            elif cursor.access_specifier == AccessSpecifier.PUBLIC:
                spelling = "public"
            elif cursor.access_specifier == AccessSpecifier.PROTECTED:
                spelling = "protected"

        # Detect = delete / = default on special members and functions
        if cursor.kind in (
            CursorKind.CONSTRUCTOR,
            CursorKind.CXX_METHOD,
            CursorKind.FUNCTION_DECL,
            CursorKind.FUNCTION_TEMPLATE,
        ):
            try:
                toks = list(cursor.get_tokens())
                token_spelling = " ".join(t.spelling for t in toks)
                if "= delete" in token_spelling:
                    token_value = "= delete"
                elif "= default" in token_spelling:
                    token_value = "= default"
            except Exception:
                pass

        # Populate member names reliably for MEMBER_REF_EXPR
        member_name = None
# Populate member names reliably for MEMBER_REF_EXPR
        if cursor.kind == CursorKind.MEMBER_REF_EXPR:
            member_name = (cursor.spelling or "").strip()

            if not member_name:
                try:
                    ref = cursor.referenced
                except Exception:
                    ref = None
                if ref is not None:
                    member_name = (
                        getattr(ref, "spelling", "")
                        or getattr(ref, "displayname", "")
                        or ""
                    ).strip()

            if not member_name:
                # Fallback to tokens: pick the last identifier before '('
                tok_str = self._join_tokens(cursor) or ""
                # e.g. "data . size ( )" → head="data.size" → "size"
                head = tok_str.split("(", 1)[0]
                for sep in ("->", ".", "::"):
                    if sep in head:
                        head = head.split(sep)[-1]

                m = re.search(r"[A-Za-z_]\w*$", head)
                if m:
                    member_name = m.group(0)

            # Strip trailing () if somehow still present
            if "(" in member_name:
                member_name = member_name.split("(", 1)[0].strip()


            spelling = member_name or spelling



        # Final spelling normalization
        if cursor.kind == CursorKind.TYPE_REF:
            s = cursor.spelling or ""
            for prefix in ("class ", "struct ", "enum "):
                if s.startswith(prefix):
                    s = s[len(prefix):]
            spelling = s
        elif cursor.kind == CursorKind.MEMBER_REF_EXPR and member_name:
            spelling = member_name
        else:
            spelling = cursor.spelling or spelling or ""

        return ASTNode(
            kind=kind_name,
            spelling=spelling,
            children=children,
            token_value=token_value,
            type_name=type_name,
        )
    
    def _join_tokens(self,cur):
        try:
            toks = [t.spelling for t in cur.get_tokens()]
            return " ".join(toks) if toks else None
        except Exception:
            return None



    def __insert_gap_filler_raw_tokens(self,cursor, children):
        """
        Filters `cursor`'s tokens to only those not covered by child extents,
        then inserts a RAW_TOKENS node before the first RETURN_STMT (or appends if none).
        
        Args:
            cursor: The clang Cursor for a COMPOUND_STMT.
            children: List of ASTNode children already built for this statement.

        Returns:
            Updated `children` list (modified in place and also returned).
        """
        # Record extents of existing children
        seen_extents = []
        for c in cursor.get_children():
            try:
                seen_extents.append((c.extent.start.offset, c.extent.end.offset))
            except:
                pass

        # Collect only tokens not inside any child extent
        raw_tokens = []
        for tok in cursor.get_tokens():
            off = tok.location.offset
            if tok.kind != TokenKind.COMMENT and not any(start <= off < end for start, end in seen_extents):
                raw_tokens.append(tok.spelling)

        # If no leftover tokens, nothing to insert
        if not raw_tokens:
            return children

        token_str = " ".join(raw_tokens)

        # Insert before RETURN_STMT if present
        for i, ch in enumerate(children):
            if ch.kind == "RETURN_STMT":
                children.insert(i, ASTNode(
                    kind="RAW_TOKENS",
                    spelling=token_str,
                    children=[],
                    token_value=None,
                    type_name=None
                ))
                break
        else:
            # No RETURN_STMT found: append
            children.append(ASTNode(
                kind="RAW_TOKENS",
                spelling=token_str,
                children=[],
                token_value=None,
                type_name=None
            ))

        return children

    def check_cursor_presence(self, tu):
        ast_debug.check_cursor_presence(tu)

    def print_astnode(self,node, indent=""):
        if node is None:
            print(f"{indent}<No AST node>")
            return
        ast_debug.print_astnode(node, indent)

  # -----------------------------
  #AST to JSON

    def ast_to_string(self, node):
        return ast_serialiser.ast_to_string(node)

    def ast_to_json(self, node, pretty=False):
        return ast_serialiser.ast_to_json(node, self.source_code_path, pretty=pretty)

    def save_ast_json_to_file(self, node, print_to_console=False, output_file="ast.json"):
        ast_serialiser.save_ast_json_to_file(node, self.source_code_path, print_to_console, output_file)

 


 