
import subprocess
import re

def is_gcc_major_version_greater(gcc_path, required_major_version):
    """
    Checks if the GCC major version is greater than the specified value.

    Args:
        gcc_path (str): Path to the GCC binary.
        required_major_version (int): The required major version.

    Returns:
        bool: True if the GCC major version is greater than required_major_version, False otherwise.
    """
    try:
        # Run the gcc command and capture the output
        gcc_output = subprocess.check_output([gcc_path, '-v'], stderr=subprocess.STDOUT, universal_newlines=True)

        # Extract the major version using regex
        version_match = re.search(r"gcc version (\d+)", gcc_output)

        if version_match:
            # Parse the major version
            major_version = int(version_match.group(1))
            
            # Compare the major version
            return major_version >= required_major_version
        else:
            print("Unable to detect GCC version.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error while running GCC: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False