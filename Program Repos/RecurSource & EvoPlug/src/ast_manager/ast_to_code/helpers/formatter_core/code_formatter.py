import subprocess
import tempfile
import os

from src.common import c_lang_installation_checker



def format_cpp_code_with_clang_format(cpp_code, extension=".cpp"):
    installed, clang_msg = c_lang_installation_checker.is_clang_installed()
    clang_format_installed, format_msg = c_lang_installation_checker.is_clang_format_installed()

    if installed and clang_format_installed:
        try:
            # Create a temporary file with the given extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=extension, mode='w') as temp_file:
                temp_file.write(cpp_code)
                temp_file_path = temp_file.name

            # Run clang-format with style=file to respect project configs
            clang_format_cmd = ["clang-format", "-i", "-style=file", temp_file_path]
            subprocess.run(clang_format_cmd, check=True)

            # Read the formatted code
            with open(temp_file_path, "r") as temp_file:
                formatted_code = temp_file.read()

            # Clean up the temporary file
            os.remove(temp_file_path)

            return formatted_code

        except subprocess.CalledProcessError as e:
            print(f"clang-format failed: {e}")
        except Exception as e:
            print(f"An error occurred while formatting the code: {e}")
        return cpp_code
    else:
        print("clang or clang-format is not available. Please install them and try again.")
        print(f"Clang installation status: {installed} — {clang_msg}")
        print(f"Clang-format installation status: {clang_format_installed} — {format_msg}")
        return cpp_code
