from Config.global_config import config

def get_the_generated_program_exstension():
    """
    This function returns the file extension of the generated program based on the programming language specified in the configuration.
    """
    programming_language = config.PROGRAM_GENERATION.programming_language.lower()

    if programming_language == 'c':
        return '.c'
    elif programming_language == 'c++':
        return '.cpp'
    # elif programming_language == 'python':
    #     return '.py'
    # elif programming_language == 'java':
    #     return '.java'
    # elif programming_language == 'javascript':
    #     return '.js'
    # elif programming_language == 'c#':
    #     return '.cs'
    else:
        raise ValueError("Unsupported programming language specified in the configuration.")