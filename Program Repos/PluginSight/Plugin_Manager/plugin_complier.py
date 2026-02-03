#!/usr/bin/env python3
import os
import subprocess
import argparse
import Utilities.gcc_utils as gcc_utils
from pathlib import Path
from Config.global_config import config


def find_source_files(source_dir, extensions=('.c', '.cc', '.cpp'), exclude_dirs=None):
    """Recursively find all source files in directory with given extensions, excluding specified folders."""

    if exclude_dirs is None:
        exclude_dirs = []
    
    source_files = []
    for ext in extensions:
        for file in Path(source_dir).rglob(f'*{ext}'):
            if not any(excluded in file.parts for excluded in exclude_dirs):
                source_files.append(file)

    return sorted(source_files)


def compile_gcc_plugin(source_dir, output_plugin, gcc_path='gcc', cxx_path='g++'):
    """
    Compile all source files in a directory into a GCC plugin with coverage support
    
    Args:
        source_dir: Root directory containing plugin source files
        output_plugin: Output .so file path
        gcc_path: Path to GCC compiler
        cxx_path: Path to G++ compiler
    """
    # changing the compiler configuration based on the config
    if config.PLUGIN_COMPILATION_GCC_CONFIGURATION.gcc_version and config.PLUGIN_COMPILATION_GCC_CONFIGURATION.gcc_version!='default':
        gcc_path=config.PLUGIN_COMPILATION_GCC_CONFIGURATION.gcc_version

    if config.PLUGIN_COMPILATION_GCC_CONFIGURATION.cxx_version and config.PLUGIN_COMPILATION_GCC_CONFIGURATION.cxx_version!='default':
        cxx_path=config.PLUGIN_COMPILATION_GCC_CONFIGURATION.cxx_version

    source_dir = Path(source_dir)
    output_plugin = Path(output_plugin)
    plugin_specific_compile_flags=[]
    try:
        if config.COVERAGE_ANALYSER.use_plugin_specific_additional_includes:
            if config.COVERAGE_ANALYSER.use_specific_plugin_headers:
                plugin_dir = Path(f'{source_dir}/{config.PATHS.specific_plugin_headers_inclue_path}')
                include_path = plugin_dir
            else:
                plugin_dir = Path(subprocess.check_output([gcc_path, '-print-file-name=plugin'], universal_newlines=True).strip())
                include_path = plugin_dir / 'include'

            if config.PLUGIN_SPECIFIC_ADDITIONAL_INCLUDES:
                plugin_flags = config._config['PLUGIN_SPECIFIC_ADDITIONAL_INCLUDES'].items()
                for key, value in plugin_flags:
                    if 'include' in key.lower():
                        plugin_specific_compile_flags.append(f"-I{source_dir}/{value}"
)
          
        else:  
            plugin_dir = Path(subprocess.check_output([gcc_path, '-print-file-name=plugin'],universal_newlines=True).strip())
            include_path = plugin_dir / 'include'


    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to find GCC plugin directory: {e}")

    exclude_dirs=[]
    if config.PLUGIN_FOLDER_EXCLUDES:
        excluded_items = config._config['PLUGIN_FOLDER_EXCLUDES'].items()
        for key,value in excluded_items:
                exclude_dirs.append(value)
                
    # Find all source files recursively
    source_files = find_source_files(source_dir,exclude_dirs=exclude_dirs)
    if not source_files:
        raise FileNotFoundError(f"No source files found in {source_dir} and its subdirectories")
    
    print("Found source files:")
    for src in source_files:
        print(f"  - {src}")

    additional_compiler_flags=[]
    if config.COVERAGE_ANALYSER.use_additional_plugin_compiler_flags:
        if config.ADDITIONAL_PLUGIN_COMPILER_FLAGS:
            compiler_flags = config._config['ADDITIONAL_PLUGIN_COMPILER_FLAGS'].items()
            for key,value in compiler_flags:
                additional_compiler_flags.append(value)


    if config.PLUGIN_COMPILATION_GCC_CONFIGURATION.use_condition_coverage and gcc_utils.is_gcc_major_version_greater(gcc_path,14):
        additional_compiler_flags.append('-fcondition-coverage')

    
    # compile_flags = [
    #     '-fPIC',
    #     '-shared',
    #     '-g',
    #     '-fno-rtti',
    #     '-fprofile-arcs',
    #     '-ftest-coverage',
    #     '--coverage',
    #     '-lgcov',
    #     '-O2',
    #     f'-I{include_path}',
    #     *plugin_specific_compile_flags,
    #     *additional_compiler_flags
    # ]

    compile_flags = [
        '-fPIC',
        '-shared',
        '-g',
        '-fno-rtti',
        '-ftest-coverage',
        '--coverage',
        '-O0',
        '-lgcov',
        f'-I{include_path}',
        *plugin_specific_compile_flags,
        *additional_compiler_flags
    ]
    
    
    # Compile each source file
    obj_files = []
    for src in source_files:
        obj_file = src.with_suffix('.o')
        src_dir = src.parent
        
        cmd = [
            cxx_path,
            *compile_flags,
            f'-I{src_dir}',  # Add each file's directory to include path
            '-c',
            str(src),
            '-o',
            str(obj_file)
        ]
        
        print(f"\nCompiling {src.relative_to(source_dir)}")
        print(' '.join(cmd))
        
        try:
            subprocess.run(cmd, check=True)
            obj_files.append(obj_file)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to compile {src}: {e}")
    
    # Link all object files
    print(f"\nLinking {output_plugin}...")
    # link_cmd = [
    #     cxx_path,
    #     '-shared', 
    #     '-fPIC',
    #     '-fno-rtti',
    #     '-g',
    #     '-ftest-coverage',
    #     '--coverage',
    #     '-lgcov',
    #     f'-I{include_path}',
    #     f'-I{source_dir}',  # Add root source directory to include path
    #     *additional_compiler_flags,
    #     '-o',
    #     str(output_plugin),
    #     *[str(obj) for obj in obj_files]
    # ]

    link_cmd = [
        cxx_path,
        '-shared', 
        '-fPIC',
        '-fno-rtti',
        '-ftest-coverage',
        '-lgcov',
        '--coverage',
        '-O0',
        '-g',
        f'-I{include_path}',
        f'-I{source_dir}',  # Add root source directory to include path
        *additional_compiler_flags,
        '-o',
        str(output_plugin),
        *[str(obj) for obj in obj_files]
    ]

    print(' '.join(link_cmd))

    try:
        subprocess.run(link_cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to link plugin: {e}")
    
    # Clean up object files
    for obj in obj_files:
        try:
            obj.unlink()
        except OSError as e:
            print(f"Warning: Could not delete {obj}: {e}")
    
    print(f"\nSuccessfully built GCC plugin with coverage: {output_plugin}")
    print(f"File size: {output_plugin.stat().st_size/1024:.1f} KB")

    # return output_plugin

if __name__ == '__main__':
    try:
        compile_gcc_plugin(
            source_dir=config.PATHS.gcc_plugin_path,
            output_plugin=f"{config.PATHS.plugin_output_path}{config.PATHS.plugin_output_name}"
        )
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)


# Example usage:
# python3 -m Plugin_Manager.plugin_complier 
# python3 -m Plugin_Manager.plugin_complier /path/to/plugin/source -o output_plugin.so