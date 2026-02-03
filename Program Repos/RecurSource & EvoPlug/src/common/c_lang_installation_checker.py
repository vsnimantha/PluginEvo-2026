import subprocess

def is_clang_installed():
    try:
        # Attempt to run the clang command and check its version
        result = subprocess.run(
            ["clang", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout  # Clang is installed, return its version info
        else:
            return False, "Clang is not installed or unavailable."
    except FileNotFoundError:
        return False, "Clang is not installed or not found in PATH."
    

def is_clang_format_installed():
    try:
        # Attempt to run the clang-format command and check its version
        result = subprocess.run(
            ["clang-format", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout  # Clang-format is installed, return its version info
        else:
            return False, "Clang-format is not installed or unavailable."
    except FileNotFoundError:
        return False, "Clang-format is not installed or not found in PATH."


# # Example usage
# installed, message = is_clang_installed()
# if installed:
#     print(f"Clang is installed:\n{message}")
# else:
#     print(message)
