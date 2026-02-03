#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
from Config.global_config import config

class CompilationError(Exception):
    pass

def compile_with_gcc_plugin(cpp_file, output_name, plugin_path, plugin_args=None, extra_flags=None):
    """
    Compile a C++ program with a GCC plugin
    
    Args:
        cpp_file: Path to the C++ source file
        output_name: Name of the output executable
        plugin_path: Path to the GCC plugin (.so file)
        plugin_args: Optional dictionary of plugin arguments
        extra_flags: Optional list of additional compiler flags
    """
    if not Path(cpp_file).exists():
        raise FileNotFoundError(f"C++ source file not found: {cpp_file}")
    
    if not Path(plugin_path).exists():
        raise FileNotFoundError(f"GCC plugin not found: {plugin_path}")
    

    # Add plugin arguments if specified
    args=[]
    if plugin_args:
        for key, value in plugin_args.items():
            args.append(f"-fplugin-arg-{config.PATHS.plugin_output_name[:-3]}-{key}={value}")


    program_additional_flags=[]
    if config.COVERAGE_ANALYSER.use_additional_program_compiler_flags:
        if config.PROGRAM_COMPILATION_ADDITIONAL_FLAGS_CONFIGURATION:
            porg_flags = config._config['PROGRAM_COMPILATION_ADDITIONAL_FLAGS_CONFIGURATION'].items()
        for key,value in porg_flags:
                program_additional_flags.append(value)

    # cxx_path='g++'
    cxx_path='g++'
    if config.PROGRAM_COMPILATION_GCC_CONFIGURATION.cxx_version and config.PROGRAM_COMPILATION_GCC_CONFIGURATION.cxx_version!='default':
        cxx_path=config.PROGRAM_COMPILATION_GCC_CONFIGURATION.cxx_version

    # cxx_path="gcc-10" #TODO:: FIX FOR C SPECIFIC PLUGINS. REFTRACK,gcc_assert_introspect, randomized layout Plugin specifically needs this to run/
    cmd = [cxx_path,
            *program_additional_flags,
            f"-fplugin={plugin_path}",
            *args,
            "-g",
            cpp_file,
            "-o",
            output_name
    ]

    # Add extra flags if specified
    if extra_flags:
        cmd.extend(extra_flags)
    
    # Print the command for debugging
    print("Compile command:", " ".join(cmd))
    # Run the compilation
    try:
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(f"Successfully compiled {cpp_file} to {output_name} with plugin {plugin_path}")
        
        return result
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        print("Compilation failed:")
        print(e.stderr.decode())
        # sys.exit(1)
        raise CompilationError(
            f"Compilation failed for {cpp_file}: {e.stderr.decode(errors='ignore')}"
        )

if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     print(f"Usage: {sys.argv[0]} <cpp_file> <output_name> <plugin_path> [plugin_args...]")
    #     print("Example: ./compile_with_plugin.py test.cpp test_app plugin.so arg1=value1 arg2=value2")
    #     sys.exit(1)
    
    cpp_file = "Plugin_Manager/test.cpp"
    output_name = "output.so"
    plugin_path = f"{config.PATHS.plugin_output_path}{config.PATHS.plugin_output_name}"
    
    # Parse optional plugin arguments
    plugin_args = {}
    for arg in sys.argv[4:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            plugin_args[key] = value
    
    compile_with_gcc_plugin(cpp_file, output_name, plugin_path, plugin_args)

    # python3 -m Plugin_Manager.program_complier_with_plugin 
    # python3 -m Plugin_Manager.program_complier_with_plugin Plugin_Manager/test.cpp test_app Plugin_Manager/test.so arg1=value1 arg2=value2