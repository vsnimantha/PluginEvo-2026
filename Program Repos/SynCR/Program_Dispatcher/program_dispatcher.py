from fastapi import FastAPI, HTTPException
import requests
import uvicorn
import threading
import Program_Generator.program_generator_tmpl as program_generator_tmpl
from Config.global_config import config


APP_B_URL = config.FEEDBACK_MANAGER.destination_url

def generate_cpp_code():
    """
    Generates C++ code using a BNF grammar (placeholder implementation).
    """
    # cpp_code = """
    # #include <iostream>
    # int main() {
    #     std::cout << "Hello, World!" << std::endl;
    #     return 0;
    # }
    # """

    program_generator = program_generator_tmpl.ProgramGeneratorFull()
    cpp_code=program_generator.generate_program()
    return cpp_code

def send_code_to_app_b(code):
    """
    Sends the generated C++ code to App B for compilation and coverage analysis.
    """
    try:
        response = requests.post(APP_B_URL, json={"code": code})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with App B: {e}")
        return None

def main():
    """
    Main loop for App A.
    """

    for iteration in range(1):  # Run for 5 iterations
        print(f"\nIteration {iteration + 1}")
        # Step 1: Generate C++ code
        cpp_code = generate_cpp_code()
        print("Generated C++ Code:\n", cpp_code)

        # Step 2: Send code to App B
        print("Sending code to App B...")
        send_code_to_app_b(cpp_code)

if __name__ == "__main__":
    main()
    # pass
# python3 -m Program_Dispatcher.program_dispatcher 