import subprocess
import os
import Code_Formatter.c_lang_installation_checker as clang_installation_checker

def format_cpp_code_with_clang_format(cpp_code):
    installed, message = clang_installation_checker.is_clang_installed()
    if installed:
        try:
            # Save the code to a temporary file
            temp_file_path = "temp_code.cpp"
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
        except Exception:
            print("An error occured while formatting the code")
            return cpp_code
    else:
        print("clang is not available... install and try again")



# if __name__ == "__main__":
#     cpp_code = """
#     int main() {
#     int x=5; if(x>3){ x++; }return 0;
#     }
#     """

#     formatted_code = format_cpp_code_with_clang_format(cpp_code)
#     print("Formatted Code:")
#     print(formatted_code)
