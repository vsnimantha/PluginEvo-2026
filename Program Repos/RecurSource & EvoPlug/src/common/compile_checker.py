import subprocess
import tempfile
import os
from src.common import c_lang_installation_checker,language_detector

def check_compile_from_string(code_string):
    """
    This function checks both syntax and compilation of a C/C++ code snippet.
    It first runs a syntax-only check, then attempts full compilation.
    :param code_string: The C/C++ code as a string.
    :return: (success: bool, message: str)
    """
    installed, message = c_lang_installation_checker.is_clang_installed()
    if not installed:
        return False, "clang/clang++ is not available. Install and try again."

    suffix = language_detector.detect_language(code_string)

    with tempfile.NamedTemporaryFile(suffix=f".{suffix}", delete=False) as temp_file:
        temp_file.write(code_string.encode("utf-8"))
        temp_file.flush()
        tmp_path = temp_file.name

    clang = "clang++" if suffix == "cpp" else "clang"

    try:
        # Step 1: Syntax check
        syntax_result = subprocess.run(
            [clang, "-fsyntax-only", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if syntax_result.returncode != 0:
            os.remove(tmp_path)
            return False, f"Syntax error:\n{syntax_result.stderr}"

        # Step 2: Full compilation (to object file)
        out_file = tmp_path + ".out"
        compile_result = subprocess.run(
            [clang, tmp_path, "-o", out_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if compile_result.returncode == 0:
            message = "Compilation succeeded. Code is valid."
            success = True
        else:
            message = f"Compilation failed:\n{compile_result.stderr}"
            success = False

        return success, message

    finally:
        # Clean up temp files
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        out_file = tmp_path + ".out"
        if os.path.exists(out_file):
            os.remove(out_file)
