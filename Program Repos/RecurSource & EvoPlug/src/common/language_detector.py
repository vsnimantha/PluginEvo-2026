def detect_language(code_string: str) -> str:
    cpp_keywords = ["class", "namespace", "template", "std::", "new", "delete", "iostream", "vector", "map", "bool"]
    c_keywords = ["stdio.h", "stdlib.h", "string.h", "printf", "scanf", "malloc", "free"]

    if any(keyword in code_string for keyword in cpp_keywords):
        return "cpp"
    elif any(keyword in code_string for keyword in c_keywords):
        return "c"
    else:
        # Default fallback: assume C++ (since most compilers accept C as C++)
        return "cpp"
