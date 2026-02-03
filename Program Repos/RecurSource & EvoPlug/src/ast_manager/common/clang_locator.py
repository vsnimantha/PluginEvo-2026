import os
import platform
import glob
import clang.cindex

def find_valid_clang_library(possible_paths):
    for path in possible_paths:
        # Ignore incompatible libclang-cpp variant
        if "libclang-cpp" in path:
            continue
        if os.path.exists(path):
            try:
                clang.cindex.Config.set_library_file(path)
                # Try creating an Index to verify compatibility
                clang.cindex.Index.create()
                print(f" libclang configured: {path}")
                print("Using:", clang.cindex.Config.library_file)  # Verify
                return path
            except Exception as e:
                print(f"Failed to use {path}: {e}")
                continue
    return None

def auto_configure_libclang():
    system = platform.system()
    candidates = []

    if system == "Darwin":  # macOS
        candidates += glob.glob("/opt/homebrew/opt/llvm/lib/libclang*.dylib")
        candidates += glob.glob("/usr/local/opt/llvm/lib/libclang*.dylib")
    elif system == "Linux":
        candidates += glob.glob("/usr/lib/llvm-*/lib/libclang*.so*")
        candidates += glob.glob("/usr/lib/x86_64-linux-gnu/libclang*.so*")
        candidates += glob.glob("/usr/local/lib/libclang*.so*")
        candidates += glob.glob("/usr/lib64/libclang*.so*")
    else:
        print(f" Unsupported OS: {system}")
        return

    path = find_valid_clang_library(candidates)
    if not path:
        print(" Could not automatically configure libclang.")
        print(" Install Clang or specify the correct path manually.")
