import os
import platform
import glob
import subprocess
import clang.cindex
from clang_locator import auto_configure_libclang
from clang.cindex import CursorKind

# Automatically configure libclang across macOS/Linux
auto_configure_libclang()

class ASTParser:
    def __init__(self, source_code_path, language="c", std="c11"):
        self.source_code_path = source_code_path
        self.language = language
        self.std = std
        self.index = clang.cindex.Index.create()
        self.args = self._build_clang_args()
        self.args_macros = self._build_clang_args_macros()

    def _build_clang_args(self):
        """Build arguments that strictly limit system header inclusion"""
        args = [
            '-x', self.language,
            f'-std={self.std}',
            '-nostdinc',          # Don't search standard system directories
            '-nostdlibinc',       # Don't search standard library directories
            '-nobuiltininc',      # Don't include clang builtin headers
            '-Wno-everything'     # Suppress all warnings
        ]
        
        # Only add minimal necessary includes
        if platform.system() == "Darwin":
            args.extend([
                '-I/Library/Developer/CommandLineTools/usr/include/c++/v1'
            ])
        elif platform.system() == "Linux":
            args.extend([
                '-I/usr/include/c++/11'  # Adjust version as needed
            ])
        
        return args
    
    def _build_clang_args_macros(self):
        """Build arguments that allow system and builtin headers for full macro collection."""
        args = [
            '-x', self.language,
            f'-std={self.std}',
            '-Wno-everything',
        ]

        if platform.system() == "Darwin":
            # Add libc++ includes and macOS SDK sysroot include path
            sdk_path = subprocess.check_output(['xcrun', '--show-sdk-path']).decode().strip()
            args.extend([
                '-isysroot', sdk_path,
                '-I' + os.path.join(sdk_path, 'usr/include'),
                '-I/Library/Developer/CommandLineTools/usr/include/c++/v1',
            ])
        elif platform.system() == "Linux":
            # Add standard system include paths
            args.extend([
                '-I/usr/include',
                '-I/usr/include/x86_64-linux-gnu',
                '-I/usr/include/c++/11',  # Adjust for your GCC/libstdc++ version
            ])

        return args


    

    # def parse(self):
    #     """Parse C/C++ source code and return root AST node."""
    #     if not os.path.exists(self.source_code_path):
    #         raise FileNotFoundError(f"❌ Source file not found: {self.source_code_path}")
        
    #     try:
    #         tu = self.index.parse(self.source_code_path, args=self.args)
    #     except clang.cindex.TranslationUnitLoadError:
    #         print("❌ Clang failed to parse the source file. Check syntax or compiler args.")
    #         return None

    #     # Print diagnostics if any
    #     if tu.diagnostics:
    #         print("\n🧪 Clang Diagnostics:")
    #         for diag in tu.diagnostics:
    #             print(f"  - {diag}")
        
    #     return tu.cursor

    def parse(self,macros=False):
        """Parse C/C++ source code and return root AST node."""
        if not os.path.exists(self.source_code_path):
            raise FileNotFoundError(f"❌ Source file not found: {self.source_code_path}")
        
        if macros:
            print("🔍 Parsing with macros enabled...")
            try:
                tu = self.index.parse(self.source_code_path, args=self.args_macros)
            except clang.cindex.TranslationUnitLoadError:
                print("❌ Clang failed to parse the source file. Check syntax or compiler args.")
                return None
        else:
            try:
                tu = self.index.parse(self.source_code_path, args=self.args)
            except clang.cindex.TranslationUnitLoadError:
                print("❌ Clang failed to parse the source file with macros. Check syntax or compiler args.")
                return None

        # Print diagnostics if any
        if tu.diagnostics:
            print("\n🧪 Clang Diagnostics:")
            for diag in tu.diagnostics:
                print(f"  - {diag}")
        
        return tu.cursor

    def dump_ast(self, node=None, depth=0):
        if node is None:
            print("🔍 No AST node provided. Parsing source code...")
            node = self.parse()
            if node is None:
                print("⚠️ Could not parse AST. No output.")
                return

        # Base info with potential literal value
        info = f"{node.kind} — {node.spelling}"
        if node.kind in (CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL, CursorKind.STRING_LITERAL):
            tokens = list(node.get_tokens())
            if tokens:
                # Usually one token for literal node
                info += f" = {tokens[0].spelling}"
        print("  " * depth + info)

        for child in node.get_children():
            self.dump_ast(child, depth + 1)

    def ast_to_lines(self, node, indent=0):
        lines = [f"{'  ' * indent}- {node.kind} ({node.spelling})"]
        for child in node.get_children():
            lines.extend(self.ast_to_lines(child, indent + 1))
        return lines  # return list of lines, not a joined string
    
    def ast_to_string(self, node):
        """
        Convert the AST node to a string representation.
        """
        lines = self.ast_to_lines(node)
        return "\n".join(lines)

    def ast_to_json(self, node):
        """
        Recursively convert the AST node to a JSON-serializable dictionary.
        """
        return {
            "kind": node.kind,
            "spelling": node.spelling,
            "children": [self.ast_to_json(child) for child in node.get_children()]
        }

