import os
import platform
import glob
import subprocess
import clang.cindex
from clang_locator import auto_configure_libclang

# Automatically configure libclang across macOS/Linux
auto_configure_libclang()

class ASTParser:
    def __init__(self, source_code_path, language="c", std="c11"):
        self.source_code_path = source_code_path
        self.language = language
        self.std = std
        self.index = clang.cindex.Index.create()
        self.args = self._build_clang_args()

    # def _build_clang_args(self):
    #     """Construct compiler arguments for Clang based on system."""
    #     args = ['-x', self.language, f'-std={self.std}']

    #     system = platform.system()
    #     include_paths = []

    #     if system == "Darwin":  # macOS
    #         include_paths += [
    #             "/Library/Developer/CommandLineTools/usr/include",
    #             "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include",
    #             "/opt/homebrew/include"
    #         ]
    #     elif system == "Linux":
    #         include_paths += [
    #             "/usr/include",
    #             "/usr/local/include",
    #             "/usr/lib/llvm-14/include",
    #             "/usr/lib/x86_64-linux-gnu/include"
    #         ]
    #     elif system == "Windows":
    #         include_paths += [
    #             "C:\\Program Files\\LLVM\\include",
    #             "C:\\MinGW\\include"
    #         ]


    #     for path in include_paths:
    #         if os.path.exists(path):
    #             args.append(f"-I{path}")

    #     return args

    # def _build_clang_args(self):
    #     """Construct compiler arguments for Clang with dynamic system paths."""
    #     # args = ['-x', self.language, f'-std={self.std}']
    #     args = ['-x', self.language, f'-std={self.std}', '-nostdinc']
    #     system = platform.system()
    #     include_paths = []

    #     # 🛠️ Static base paths per platform
    #     if system == "Darwin":  # macOS
    #         include_paths += [
    #             "/Library/Developer/CommandLineTools/usr/include",
    #             "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include",
    #             "/opt/homebrew/include"
    #         ]
    #         # 🔍 Auto-detect Clang builtin headers
    #         clang_builtin_headers = glob.glob("/opt/homebrew/opt/llvm/lib/clang/*/include")
    #         include_paths += clang_builtin_headers

    #     elif system == "Linux":
    #         include_paths += [
    #             "/usr/include",
    #             "/usr/local/include",
    #             "/usr/lib/x86_64-linux-gnu/include"
    #         ]
    #         # 🔍 Try detecting Clang builtin headers
    #         clang_builtin_headers = glob.glob("/usr/lib/llvm-*/lib/clang/*/include")
    #         include_paths += clang_builtin_headers

    #     elif system == "Windows":
    #         include_paths += [
    #             "C:\\Program Files\\LLVM\\include",
    #             "C:\\MinGW\\include"
    #         ]

    #     # 🔎 Discover headers from Clang itself
    #     try:
    #         output = subprocess.check_output(['clang', '-E', '-x', 'c', '-', '-v'],
    #                                         input=b'', stderr=subprocess.STDOUT).decode()
    #         for line in output.splitlines():
    #             if line.strip().startswith('/'):
    #                 include_paths.append(line.strip())
    #     except Exception as e:
    #         print("Couldn't fetch Clang include paths dynamically:", e)

    #     # Validate and add existing paths
    #     for path in include_paths:
    #         if os.path.exists(path):
    #             args.append(f"-isystem{path}")

    #     return args

    def _build_clang_args(self):
        """Construct compiler arguments for Clang with controlled system header inclusion."""
        import platform, subprocess, os, glob

        # 🧹 Block default system includes for a cleaner AST
        args = ['-x', self.language, f'-std={self.std}', '-nostdinc', '-fsyntax-only']

        system = platform.system()
        include_paths = []

        # 🛠️ Add only minimal paths — Clang's own headers preferred
        if system == "Darwin":  # macOS
            include_paths += glob.glob("/opt/homebrew/opt/llvm/lib/clang/*/include")
        elif system == "Linux":
            include_paths += glob.glob("/usr/lib/llvm-*/lib/clang/*/include")
        elif system == "Windows":
            include_paths += [
                "C:\\Program Files\\LLVM\\lib\\clang\\*\\include",
                "C:\\MinGW\\include"
            ]

        # 🔍 Dynamically detect Clang's own include paths
        try:
            output = subprocess.check_output(
                ['clang', '-E', '-x', 'c', '-', '-v'],
                input=b'', stderr=subprocess.STDOUT
            ).decode()

            for line in output.splitlines():
                line = line.strip()
                # Only add paths containing "clang", not general system includes
                if line.startswith('/') and 'clang' in line.lower():
                    include_paths.append(line)
        except Exception as e:
            print("⚠️ Couldn't fetch Clang include paths dynamically:", e)

        # 📦 Include paths carefully, filtering out noisy system headers
        for path in include_paths:
            if os.path.exists(path):
                args.append(f"-isystem{path}")
                print(f"✔️ Included filtered header path: {path}")

        return args


    def parse(self):
        """Parse C/C++ source code and return root AST node."""
        if not os.path.exists(self.source_code_path):
            raise FileNotFoundError(f"❌ Source file not found: {self.source_code_path}")
        
        try:
            tu = self.index.parse(self.source_code_path, args=self.args)
        except clang.cindex.TranslationUnitLoadError:
            print("❌ Clang failed to parse the source file. Check syntax or compiler args.")
            return None

        # Print diagnostics if any
        if tu.diagnostics:
            print("\n🧪 Clang Diagnostics:")
            for diag in tu.diagnostics:
                print(f"  - {diag}")
        
        return tu.cursor

    # def dump_ast(self, node=None, depth=0):
    #     """Recursively print AST structure."""
    #     if node is None:
    #         node = self.parse()
    #         if node is None:
    #             print("⚠️ Could not parse AST. No output.")
    #             return

    #     print("  " * depth + f"{node.kind} — {node.spelling}")
    #     for child in node.get_children():
    #         self.dump_ast(child, depth + 1)



    def dump_ast(self, node=None, depth=0):
        """Recursively print AST for user's source code only."""
        if node is None:
            node = self.parse()
            if node is None:
                print("⚠️ Could not parse AST. No output.")
                return

        # Filter: Only show nodes from the original source file
        # if node.location.file and os.path.abspath(str(node.location.file)) != os.path.abspath(self.source_code_path):
        #     return

        print("  " * depth + f"{node.kind} — {node.spelling}")
        for child in node.get_children():
            self.dump_ast(child, depth + 1)


