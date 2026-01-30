import subprocess
import os
import Code_Formatter.c_lang_installation_checker as clang_installation_checker
import Utilities.program_generator_utils as program_generator_utils


def format_cpp_code_with_clang_format(cpp_code):
    installed, message = clang_installation_checker.is_clang_installed()
    clang_format_installed,message=clang_installation_checker.is_clang_format_installed()
    if installed and clang_format_installed:
        try:
            # Save the code to a temporary file
            temp_file_path = f"temp_code{program_generator_utils.get_the_generated_program_exstension()}"
            with open(temp_file_path, "w") as temp_file:
                temp_file.write(cpp_code)

            # Run clang-format on the temporary file
            clang_format_cmd = ["clang-format", "-i", temp_file_path]
            subprocess.run(clang_format_cmd)

            # Read the formatted code back
            with open(temp_file_path, "r") as temp_file:
                formatted_code = temp_file.read()

            # Clean up the temporary file
            os.remove(temp_file_path)

            return formatted_code
        except Exception as e:
            print(f"An error occured while formatting the code {e}")
            return cpp_code
    else:
        print("clang or clang format is not available... install and try again")
        print(f"clang installation status {installed} ")
        print(f"clang format installation status {clang_format_installed} ")



# if __name__ == "__main__":
#     cpp_code = """
#     int main() {
#     int x=5; if(x>3){ x++; }return 0;
#     }
#     """

#     formatted_code = format_cpp_code_with_clang_format(cpp_code)
#     print("Formatted Code:")
#     print(formatted_code)
