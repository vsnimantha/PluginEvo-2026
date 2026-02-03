import subprocess
import tempfile
from Config.global_config import config
from src.common import c_lang_installation_checker,language_detector

def check_syntax_from_string(code_string):
    """
    This function checks the syntax of a C++ code snippet provided as a string.
    :param code_string: The C++ code as a string.
    :return: Boolean indicating whether the syntax is correct, and the output message.
    """
    installed, message = c_lang_installation_checker.is_clang_installed()

    if installed:
        try:
            suffix = language_detector.detect_language(code_string)

            # Create a temporary file to store the C++ code
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as temp_file:
                temp_file.write(code_string.encode('utf-8'))  # Write the code to the file
                temp_file.flush()  # Ensure the content is written
                
                clang="clang++"
                if suffix=="c":
                    clang = "clang"
                elif suffix=="cpp":
                    clang = "clang++"
                
                
                result = subprocess.run(
                    [clang, "-fsyntax-only", temp_file.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Check the result
                if result.returncode == 0:
                    return True, "Syntax is correct. No errors found!"
                else:
                    return False, result.stderr

        except FileNotFoundError:
            return False, "clang++ is not installed or not in PATH."
    else:
        print("clang is not available... install and try again")

# # Example usage
# code_string = """
#  // main_template.tmpl
# #include <iostream>
# // Additional includes
# #include<string>


# using namespace std;

# // Function definitions
# bool muFunc ()
# {
#     string chi [ 7 ] ;
#  return true;
# }

# void betaFunc (double epsilonParam , bool zetaParam , string chiParam )
# {
    
#     while (false )
#     {
#         double kappa = 15 / 16 ;
#     }
#  std::cout<<zetaParam<<std::endl;
#  std::cout<<chiParam<<std::endl;
#  std::cout<<epsilonParam<<std::endl;
# }


# int main() {
#     // Function calls
#     muFunc();
#     double epsilonParam = 29.772594872783664; 
# bool zetaParam = false; 
# string chiParam = "KYP7N3INIT"; 

# betaFunc(epsilonParam,zetaParam,chiParam);
#     std::cout<< "5OPRDVOXXQTN1BEA0JPH" <<std::endl;


#     return 0;
# }

# """
# is_correct, message = check_syntax_from_string(code_string)
# print(message)
