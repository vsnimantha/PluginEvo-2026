import subprocess
import sys
import Utilities.file_management_utils as file_utils
import json
import re

from Utilities.constants import Constants
from Program_Generator.program_generator_tmpl import ProgramGeneratorFull
from pathlib import Path
from Config.global_config import config
from collections import Counter


def generate_programs_and_compile():   
    program_generator = ProgramGeneratorFull()
    programs,time_stamp=program_generator.generate_program()
    compile_programs(programs,time_stamp)

def compile_programs(programs,timestamp):

    if programs:
        if config.PROGRAM_GENERATION.smart_generation:
            print("Smart random generation........................")
            for rendered_template, file_name in programs:
                
                if file_name:
                    path=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/{file_name}"
                    path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}"
                    folder_path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled"
                    folder_path_data=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{file_name}"
                    file_utils.create_folder(folder_path_compile)
                    file_utils.create_folder(folder_path_data)
                    compile_program(path,path_compile,folder_path_data)
                else:
                    print("File name error, file name not found, please check whether it exists")

        else:
            print("Single random generation.........")

            if programs[1]:
                path=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/{programs[1]}"
                path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{programs[1]}"
                folder_path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled"
                folder_path_data=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{programs[1]}"

                file_utils.create_folder(folder_path_compile)
                file_utils.create_folder(folder_path_data)
                compile_program(path,path_compile,folder_path_data)

            else:
                print("File name error, file name not found, please check whether it exists")

def compile_program(program_file, compile_output, folder_path_data):
    error_log_file = f"{folder_path_data}/error_log.json"
    ice_error_log_file = f"{folder_path_data}/ice_error_log.json"
    success_log_file = f"{folder_path_data}/success_log.json"
    compilation_summary_log_file = f"{folder_path_data}/summary_log.txt"
    language = config.PROGRAM_GENERATION.programming_language.lower()

    print("Compiling C/C++ file:", program_file)

    if not Path(program_file).exists():
        error_info = {
            "filename": program_file,
            "language": language,
            "command": None,
            "error": "Source file not found",
            "crash_reason": "File does not exist",
            "readable_error": {
                "summary": "Source file missing",
                "details": f"The specified source file '{program_file}' was not found",
                "solution": "Check the file path and ensure the file exists",
                "severity": "Critical"
            }
        }
        with open(error_log_file, "w") as f:
            json.dump(error_info, f, indent=4)
        print(f"Error logged to {error_log_file}")
        return
    
    

    compilers_c = ["gcc", "gcc-13", "gcc-12", "gcc-11", "gcc-10","clang","clang-17","clang-16","clang-15"]
    compilers_cpp = ["g++", "g++-13", "g++-12", "g++-11", "g++-10","clang++","clang++-17","clang++-16","clang++-15"]
    # compilers_c = ["clang"]
    # compilers_cpp = ["g++-10","clang++","clang++-17","clang++-16","clang++-15"]

    compiler_running=compilers_c if language == 'c' else compilers_cpp

    for item in compiler_running:
        compiler=item
        error_log_file = f"{folder_path_data}/error_log_{compiler}.json"
        ice_error_log_file = f"{folder_path_data}/ice_error_log_{compiler}.json"
        success_log_file = f"{folder_path_data}/success_log_{compiler}.json"
        compilation_summary_log_file = f"{folder_path_data}/summary_log_{compiler}.txt"

        # Comprehensive list of compiler flags to test (700+ combinations)
        base_flags = {
            # Standard warning flags
            'warnings': [
                '-Wall', '-Wextra', '-pedantic',
                '-Wconversion', '-Wshadow',
                '-Wcast-qual', '-Wwrite-strings',
                '-Wformat=2', '-Wformat-overflow=2',
                '-Wformat-truncation=2', '-Wformat-security',
                '-Wnull-dereference', '-Wstack-protector',
                '-Wtrampolines', '-Wfloat-equal',
                '-Wtraditional-conversion', '-Wdeclaration-after-statement',
                '-Wundef', '-Wuninitialized',
                '-Wstrict-overflow=5', '-Warray-bounds=2',
                '-Wshift-overflow=2', '-Wduplicated-cond',
                '-Wduplicated-branches', '-Wlogical-op',
                '-Wrestrict',
                '-Wdouble-promotion', '-Wimplicit-fallthrough=5',
                # '-Wnull-pointer-subtraction',  -Werror
            ],
            # If warnings needed to be treated as errors add  -Werror
            
            # Optimization flags
            'optimizations': [
                '-O0', '-O1', '-O2', '-O3', '-Os', '-Ofast', '-Og',
                '-fno-strict-aliasing', '-fstrict-aliasing',
                '-fstrict-overflow', '-fno-strict-overflow',
                '-ffast-math', '-fno-fast-math',
                '-funsafe-math-optimizations', '-fno-unsafe-math-optimizations',
                '-ffinite-math-only', '-fno-finite-math-only',
                '-fexcess-precision=fast', '-fexcess-precision=standard',
                '-frounding-math', '-fno-rounding-math',
                '-fsignaling-nans', '-fno-signaling-nans',
                '-fcx-limited-range', '-fno-cx-limited-range',
                '-fipa-pta', '-fno-ipa-pta',
                '-fipa-ra', '-fno-ipa-ra',
                '-fipa-cp', '-fno-ipa-cp',
                '-flto', '-fno-lto',
                '-fwhole-program', '-fno-whole-program',
            ],
            
            # Sanitizers (great for finding bugs)
            'sanitizers': [
                '-fsanitize=address',
                '-fsanitize=undefined',
                '-fsanitize=leak',
                '-fsanitize=thread',
                '-fsanitize=memory',
                '-fsanitize=bool',
                '-fsanitize=bounds',
                '-fsanitize=enum',
                '-fsanitize=float-cast-overflow',
                '-fsanitize=float-divide-by-zero',
                '-fsanitize=nonnull-attribute',
                '-fsanitize=null',
                '-fsanitize=object-size',
                '-fsanitize=return',
                '-fsanitize=returns-nonnull-attribute',
                '-fsanitize=shift',
                '-fsanitize=signed-integer-overflow',
                '-fsanitize=unreachable',
                '-fsanitize=vla-bound',
                '-fsanitize=vptr',
                '-fsanitize=alignment',
            ],
            
            # Language standard versions
            'standards': {
                'c': [
                    '-std=c89', '-std=gnu89',
                    '-std=c99', '-std=gnu99',
                    '-std=c11', '-std=gnu11',
                    '-std=c17', '-std=gnu17',
                    '-std=c2x', '-std=gnu2x',
                ],
                'c++': [
                    '-std=c++98', '-std=gnu++98',
                    '-std=c++11', '-std=gnu++11',
                    '-std=c++14', '-std=gnu++14',
                    '-std=c++17', '-std=gnu++17',
                    '-std=c++20', '-std=gnu++20',
                    '-std=c++23', '-std=gnu++23',
                ]
            },
            
            # Architecture and ABI flags
            'architecture': [
                '-m32', '-m64',
                '-mx32', '-march=native',
                '-mtune=native', '-mavx',
                '-mavx2', '-msse4.2',
                '-mfpmath=sse', '-mfpmath=387',
                '-msoft-float', '-mhard-float',
                '-mabi=sysv', '-mabi=ms',
            ],
            
            # Code generation flags
            'codegen': [
                '-fpic', '-fPIC',
                '-fpie', '-fPIE',
                '-fno-common', '-fcommon',
                '-fshort-wchar', '-fno-short-wchar',
                '-fshort-enums', '-fno-short-enums',
                '-fpack-struct', '-fno-pack-struct',
                '-fleading-underscore', '-fno-leading-underscore',
                '-fmerge-all-constants', '-fno-merge-all-constants',
                '-fstack-check', '-fno-stack-check',
                '-fstack-protector', '-fstack-protector-strong',
                '-fstack-protector-all', '-fno-stack-protector',
                '-fno-omit-frame-pointer', '-fomit-frame-pointer',
                '-fno-asynchronous-unwind-tables', '-fasynchronous-unwind-tables',
                '-fno-exceptions', '-fexceptions',
                '-fno-rtti', '-frtti',
                '-fno-threadsafe-statics', '-fthreadsafe-statics',
            ],
            
            # Debugging flags
            'debug': [
                '-g', '-g0', '-g1', '-g2', '-g3',
                '-ggdb', '-gstabs', '-gstabs+',
                '-gcoff', '-gxcoff', '-gxcoff+',
                '-gdwarf', '-gdwarf-2', '-gdwarf-3', '-gdwarf-4', '-gdwarf-5',
                '-fvar-tracking', '-fvar-tracking-assignments',
                '-fdebug-types-section', '-fno-debug-types-section',
            ],
        }

        # Select compiler based on language
        # compiler = "gcc" if language == 'c' else "g++"
        standards = base_flags['standards'].get(language, [])
        
        # Systematic testing approach (700+ combinations)
        test_combinations = [
            # Base test with all warnings
            base_flags['warnings'],
            
            # Test each optimization level with basic warnings
            *[[opt] + base_flags['warnings'][:5] for opt in base_flags['optimizations']],
            
            # Add sanitizer tests
            *[[sanitizer] + base_flags['warnings'][:5] for sanitizer in base_flags['sanitizers']],
            
            # Add architecture tests
            *[[arch] + base_flags['warnings'][:5] for arch in base_flags['architecture']],
            
            # Test standards with basic warnings
            *[base_flags['warnings'][:3] + [std] for std in standards],
            
            # Test debug flags
            *[[debug] + base_flags['warnings'][:3] for debug in base_flags['debug']],
            
            # Test code generation flags
            *[[codegen] + base_flags['warnings'][:3] for codegen in base_flags['codegen']],
        ]
        
        results = []     
        # Test all combinations
        for std in standards:
            for test_flags in test_combinations:
                output_suffix = f"_{std[5:]}_{hash(tuple(test_flags)) % 1000:04d}"
                output_file = f"{compile_output}{output_suffix}.o"
                
                cmd = [compiler, std] + test_flags + [program_file, "-o", output_file]
                print("Compile command:", " ".join(cmd))
                
                try:
                    result = subprocess.run(
                        cmd,
                        check=True,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        timeout=30
                    )
                    
                    result_info = {
                        "filename": program_file,
                        "language": language,
                        "standard": std,
                        "flags": test_flags,
                        "command": " ".join(cmd),
                        "status": "Success",
                        "output_file": output_file,
                        "warnings": result.stderr.decode(),
                        "compiler":compiler,
                        "readable_summary": {
                            "status": "Compilation successful",
                            "warnings": extract_warnings(result.stderr.decode()),
                            "optimization_level": get_optimization_level(test_flags),
                            "standard_used": std,
                            "flag_count": len(test_flags),
                            "flags_used": test_flags
                        }
                    }
                    results.append(result_info)
                    print(f"Successfully compiled with {std} and flags")
                except subprocess.CalledProcessError as e:
                    error_message = e.stderr.decode()
                    print(f"Compilation failed:", error_message)

                    crash_reason, readable_error = classify_error(error_message, std, test_flags,compiler)
                    
                    result_info = {
                        "filename": program_file,
                        "language": language,
                        "standard": std,
                        "flags": test_flags,
                        "command": " ".join(cmd),
                        "status": "Failed",
                        "error": error_message,
                        "crash_reason": crash_reason,
                        "compiler":compiler,
                        "readable_error": readable_error,
                        "debugging_tips": generate_debugging_tips(crash_reason, std),
                        "flags_used": test_flags
                    }
                    results.append(result_info)

                except subprocess.TimeoutExpired:
                    result_info = {
                        "filename": program_file,
                        "language": language,
                        "standard": std,
                        "flags": test_flags,
                        "command": " ".join(cmd),
                        "status": "Failed",
                        "error": "Compilation timed out",
                        "crash_reason": "Timeout",
                        "compiler":compiler,
                        "readable_error": {
                            "summary": "Compilation timed out",
                            "details": "Compiler took more than 30 seconds to process",
                            "solution": "Try with fewer optimization flags or check for complex templates/includes",
                            "severity": "High",
                            "possible_causes": [
                                "Excessive template instantiation",
                                "Compiler bug with specific flag combination",
                                "System resource constraints"
                            ]
                        },
                        "flags_used": test_flags
                    }
                    results.append(result_info)

        # Save results
        # TODO:: Implement breaking the files between multiple files
        # To address the large files.
        with open(success_log_file, "w") as f:
            json.dump([r for r in results if r["status"] == "Success"], f, indent=4)
        
        with open(error_log_file, "w") as f:
            json.dump([r for r in results if r["status"] == "Failed"], f, indent=4)

        with open(ice_error_log_file, "w") as f:
            json.dump([r for r in results if r["status"] == "Failed" and r["crash_reason"] == "Compiler Internal Error (ICE)"], f, indent=4)


        print_compilation_summary(results, error_log_file, success_log_file,ice_error_log_file,compilation_summary_log_file)


def classify_error(error_message, standard, flags,compiler="gcc"):
    """Enhanced error classification with broader ICE detection and fixes"""
    error = error_message.lower()
    crash_reason = "Unknown error"
    readable_error = {
        "summary": "Unknown compilation error",
        "details": error_message.strip(),
        "solution": "Check compiler documentation and verify code syntax",
        "severity": "Medium"
    }

    try:

        ice_patterns = [
            # General ICE Errors
            r"internal compiler error[:,-]?\s*(.+)",
            r"unexpected internal compiler error",
            r"compiler crashed unexpectedly",
            r"compiler encountered an unrecoverable error",
            r"compilation aborted due to unknown issue",
            r"ICE detected in pass (.+)",
            r"internal error: backend compiler failure",
            r"compiler exited with nonzero status",

            # GCC-Specific ICE Errors
            r"gcc internal error",
            r"received signal SIGSEGV",  # Segmentation Fault
            r"received signal SIGABRT",  # Aborted process
            r"fatal signal 6",  # SIGABRT (Abnormal termination)
            r"fatal signal 11",  # SIGSEGV (Invalid memory access)
            r"unrecoverable stack overflow",
            r"process killed due to memory exhaustion",
            r"gcov: internal error",
            r"compiler received fatal signal",
            r"GCC assertion failed at (.+)",
            r"error: unsupported instruction detected",

            # Clang-Specific ICE Errors
            r"clang failed assertion",
            r"clang encountered an unknown error",
            r"fatal error: LLVM assertion failure",
            r"LLVM fatal error",
            r"failed to materialize",
            r"unexpected error in clang",
            r"clang segmentation fault",
            r"clang crash detected",
            r"fatal error: error in backend",
            r"LLVM ERROR: malformed module",
            r"unexpected instruction lowering failure",
            r"Segmentation fault \(core dumped\)",
            r"clang[:,-]?\s*segmentation fault",
            r"fatal signal \d+",




            # MSVC-Specific ICE Errors (Windows)
            r"internal error in msvc",
            r"fatal error C9999",  # MSVC crash condition
            r"compiler encountered an unexpected condition",
            r"msvc compilation aborted unexpectedly",
            r"fatal error LNK1327",  # MSVC linker crash
            r"unexpected compiler failure",
            r"compiler stack overflow detected",
            r"fatal error C1900: internal compiler error",
            r"internal consistency check failed",

            # General ICE & Compiler Crash Patterns
            r"compilation failed due to unexpected error",
            r"illegal instruction detected during compilation",
            r"internal assertion failed",
            r"debugging information corrupted"
        ]



        
        for pattern in ice_patterns:
            if re.search(pattern, error, re.IGNORECASE):
                # print("CRASHED THE COMPILER")
                # input()
                crash_reason = "Compiler Internal Error (ICE)"
                ice_details = re.search(r"internal compiler error: (.+)", error_message, re.DOTALL)
                           
                readable_error = {
                    "summary": "Compiler Internal Failure",
                    "details": ice_details.group(1).strip() if ice_details else error_message.strip(),
                    "solution": "Report to maintainers with minimal reproducer",
                    "severity": "Critical",
                    "gcc_version": get_gcc_version(compiler),
                    "compiler_flags": flags,
                    "bug_pattern": f"ICE - {str(pattern)}"
                }
                return crash_reason, readable_error

        # 2. Standard Compliance Checks (Expanded for C89/C90)
        c89_patterns = {
            r"loop initial declarations are only allowed in c99 or c11 mode": {
                "summary": "C89 Variable Declaration Violation",
                "solution": f"Use {standard.replace('89','99')} or declare variables before loops",
                "severity": "High"
            },
            r"iso c90 forbids mixed declarations and code": {
                "summary": "C89 Declaration Order Issue",
                "solution": "Move all declarations before any code statements",
                "severity": "High"
            },
            r"c++ style comments are not allowed": {
                "summary": "Invalid Comment Style for C89",
                "solution": "Replace // comments with /* */",
                "severity": "Medium"
            },
            r"does not support the ['‘]z['’] gnu_printf": {
                "summary": "C89 Format Specifier Issue",
                "solution": "Use %lu instead of %zu",
                "severity": "Medium"
            }
        }

        for pattern, info in c89_patterns.items():
            if re.search(pattern, error, re.IGNORECASE):
                return info["summary"], {**info, "details": error_message.strip(), "bug_pattern": "C89_STANDARD_VIOLATION"}

        # 3. Variable Scope Issues
        if "redefinition of" in error:
            var_match = re.search(r"redefinition of ['‘](.+?)['’]", error_message)
            return (
                "Variable Redefinition Error",
                {
                    "summary": "Duplicate Variable Declaration",
                    "details": f"Duplicate declaration of '{var_match.group(1)}'" if var_match else "Variable redeclaration",
                    "solution": "Use unique variable names in same scope",
                    "severity": "High",
                    "bug_pattern": "VARIABLE_REDEFINITION"
                }
            )

        # 4. Type Conversion Issues
        if "comparison of integer expressions of different signedness" in error:
            return (
                "Signed/Unsigned Comparison",
                {
                    "summary": "Type Comparison Warning",
                    "details": "Mixing signed and unsigned integers in comparison",
                    "solution": "Use explicit casts or consistent types",
                    "severity": "Medium",
                    "bug_pattern": "SIGN_COMPARE"
                }
            )

        # 5. Unused Variables
        if "unused variable" in error:
            unused_vars = list(set(re.findall(r"unused variable ['‘](.+?)['’]", error_message)))
            return (
                "Unused Variable Warning",
                {
                    "summary": f"Unused Variables ({len(unused_vars)})",
                    "details": f"Variables not used: {', '.join(unused_vars)}",
                    "solution": "Remove unused variables or add usage",
                    "severity": "Low",
                    "bug_pattern": "UNUSED_VARIABLE"
                }
            )
        
        # 6. Unrecognized command line options
        if "unrecognized command-line option" in error:
            parts = [p.strip("'") for p in error.split("'") if p.strip()]
            flag = parts[1] if len(parts) > 1 else "unknown_flag"
            
            return (
                "Unsupported Compiler Flag",
                {
                    "summary": f"Unsupported flag: {flag}",
                    "details": f"The compiler doesn't recognize the '{flag}' option",
                    "solution": f"Remove {flag} or use a newer compiler version",
                    "severity": "Low",
                    "bug_pattern": "UNSUPPORTED_FLAG"
                }
            )
        
        # 7. Unrecognized arguments
        if "unrecognized argument" in error:
            parts = [p.strip("'") for p in error.split("'") if p.strip()]
            argument = parts[1] if len(parts) > 1 else "unknown_argument"
            
            return (
                "Unrecognized Argument Error",
                {
                    "summary": f"Unrecognized argument: {argument}",
                    "details": f"The compiler doesn't recognize the '{argument}' argument",
                    "solution": f"Remove '{argument}' or check for correct syntax",
                    "severity": "Low",
                    "bug_pattern": "UNRECOGNIZED_ARGUMENT"
                }

            )
        
        # 8. Undefined references
        if "undefined reference" in error:
            parts = [p.strip("'") for p in error.split("'") if p.strip()]
            symbol = parts[1] if len(parts) > 1 else "unknown_symbol"
            
            crash_reason = "Linker Error"
            readable_error = {
                "summary": "Undefined Function/Variable Reference",
                "details": f"The linker couldn't find the definition for: {symbol}",
                "solution": (
                    f"Check if '{symbol}' is properly defined and linked. "
                    "Ensure required object files or libraries are included, and verify the correct order of linking."
                ),
                "missing_symbol": symbol,
                "severity": "High"
            }

        # 9. Syntax Errors
        syntax_patterns = {
            r"expected (‘.*?’)": "Missing Token",
            r"missing terminating ['‘”](.)['’”] character": "Unclosed String/Char",
            r"redeclaration of ‘.*?’": "Duplicate Declaration",
            r"does not name a type": "Type Declaration Error",
            r"too (many|few) arguments to function": "Argument Count Mismatch"
        }

        for pattern, error_type in syntax_patterns.items():
            if re.search(pattern, error):
                crash_reason = f"Syntax Error: {error_type}"
                readable_error = {
                    "summary": f"Code Syntax Issue - {error_type}",
                    "details": extract_relevant_line(error_message),
                    "solution": "Review code syntax and language rules",
                    "severity": "High",
                    "bug_pattern": "SYNTAX_ERROR"
                }
                return crash_reason, readable_error
            
        # 10. Optimization Bugs
        if "-O" in str(flags) and ("miscompilation" in error or "wrong code" in error):
            crash_reason = "Optimization Bug"
            readable_error = {
                "summary": "Compiler Optimization Issue",
                "details": "Potential compiler bug in optimization passes",
                "solution": "Try different optimization level (-O1/-O0) and report issue",
                "severity": "Critical",
                "bug_pattern": "OPTIMIZATION_BUG"
            }
            return crash_reason, readable_error

        # 11. Warning-Related Errors
        if "all warnings being treated as errors" in error:
            warnings = [line.strip() for line in error_message.split('\n') if "warning:" in line]
            crash_reason = "Warnings as Errors"
            readable_error = {
                "summary": "Warnings Treated as Errors",
                "details": f"{len(warnings)} warnings promoted to errors",
                "solution": "Fix warnings or remove -Werror flag",
                "severity": "Medium",
                "bug_pattern": "WERROR"
            }
            return crash_reason, readable_error

        # 12. Template Errors (C++ specific)
        if "error: template" in error or "required from here" in error:
            trace = extract_template_trace(error_message)
            crash_reason = "Template Instantiation Error"
            readable_error = {
                "summary": "C++ Template Issue",
                "details": trace[-1] if trace else "Template argument mismatch",
                "solution": "Check template arguments and constraints",
                "severity": "High",
                "bug_pattern": "TEMPLATE_ERROR"
            }
            return crash_reason, readable_error

        # 13. Sanitizer Errors
        sanitizer_patterns = {
            r"addresssanitizer": "ASAN",
            r"undefinedbehaviorsanitizer": "UBSAN",
            r"leaksanitizer": "LSAN"
        }
        for pattern, sanitizer in sanitizer_patterns.items():
            if re.search(pattern, error):
                crash_reason = f"Sanitizer: {sanitizer} Error"
                readable_error = {
                    "summary": f"{sanitizer} Runtime Error",
                    "details": extract_sanitizer_details(error_message),
                    "solution": "Debug memory/runtime issues in code",
                    "severity": "Critical",
                    "bug_pattern": f"SANITIZER_{sanitizer}"
                }
                return crash_reason, readable_error

        # 14. Architecture/ABI Issues
        if "incompatible target" in error or "ABI mismatch" in error:
            arch_match = re.search(r"between ‘(.*?)’ and ‘(.*?)’", error_message)
            crash_reason = "ABI/Architecture Mismatch"
            readable_error = {
                "summary": "Binary Interface Compatibility Issue",
                "details": f"Target mismatch: {arch_match.group(0) if arch_match else 'unknown'}",
                "solution": "Use consistent -march and -mabi flags",
                "severity": "High",
                "bug_pattern": "ABI_MISMATCH"
            }
            return crash_reason, readable_error

            
        # 15. Standard Compliance Issues
        std_patterns = {
            r"only allowed in c99 mode": ("C99", "-std=c99"),
            r"iso c\+\+17 does not allow": ("C++17", "-std=c++20"),
            r"invalid in c89 mode": ("C89", "-std=c99"),
            r"was not declared in this scope": ("C++ Standard", "-std=c++latest"),
            r"use of auto in lambda parameter only available with": ("C++14+", "-std=c++14 or later"),
            r"type .*? of 'constexpr' variable": ("C++ Standard", "-std=c++17 or later")
        }

        for pattern, (std_name, recommendation) in std_patterns.items():
            if re.search(pattern, error):
                crash_reason = f"Standard Compliance: {std_name}"
                readable_error = {
                    "summary": f"{std_name} Standard Violation",
                    "details": f"Code uses features not allowed in {standard}",
                    "solution": f"Use {recommendation} or modify code",
                    "severity": "High",
                    "bug_pattern": "STANDARD_VIOLATION"
                }
                return crash_reason, readable_error
            
        # 15. No file or directory issue
        if "no such file or directory" in error.lower():
            parts = [p.strip("'") for p in error.split("'") if p.strip()]
            missing_file = parts[1] if len(parts) > 1 else "unknown_file"
            
            crash_reason = "Missing File Error"
            readable_error = {
                "summary": "Required Header or Source File Not Found",
                "details": f"The compiler cannot locate: {missing_file}",
                "solution": (
                    f"Check if '{missing_file}' exists and is correctly referenced. "
                    "This issue is often caused by missing dependencies or incorrect system architecture. "
                    "Ensure all required libraries/packages are installed and paths are set correctly."
                ),
                "missing_file": missing_file,
                "severity": "High",
                "bug_pattern": "MISSING_FILE"
            }

        # 16. Compilation Configuration Errors
        if "constexpr evaluation depth exceeds" in error.lower():
            crash_reason = "Compilation Configuration Error"
            readable_error = {
                "summary": "Constexpr Evaluation Depth Limit Exceeded",
                "details": "The compiler stopped evaluation because the recursion depth exceeded the allowed limit.",
                "solution": (
                    "Increase the depth limit using '-fconstexpr-depth=<value>', "
                    "or refactor code to reduce recursion in constexpr functions."
                ),
                "severity": "Medium",
                "bug_pattern": "CONSTEXPR_DEPTH_LIMIT"
            }
        
        # 17. Non-categorised Errors
        if "error:" in error.lower():
            crash_reason = "General Compilation Error"
            readable_error = {
                "summary": "Unhandled Compilation Error",
                "details": (
                    "The compiler encountered an issue that does not match predefined error patterns."
                ),
                "solution": (
                    "Check the full error message for clues, verify syntax and compiler settings, "
                    "and try compiling with different flags or debugging tools."
                ),
                "severity": "Medium",
                "bug_pattern": "GENERAL_COMPILATION_ERROR"
            }

    except Exception as e:
        print(f"Error classification failed: {str(e)}")
        crash_reason = "Classification Failure"
        readable_error = {
            "summary": "Error Analysis Failed",
            "details": f"{error_message[:200]}... [truncated]",
            "solution": "Please report this classification failure",
            "severity": "High"
        }
    
    return crash_reason, readable_error



# Helper functions

def get_gcc_version(compiler="gcc"):
    """Get GCC version string"""
    try:
        result = subprocess.run([f'{compiler}', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        return result.stdout.split('\n')[0].split()[-1]
    except Exception as e:
        return "unknown"

def get_flag_info(flag):
    """Database of 100+ GCC flags with version info"""
    flag_db = {
        '-Wnull-pointer-subtraction': {'since': '12.1', 'min_version': '12.1'},
        '-Warith-conversion': {'since': '11.0', 'min_version': '11.0'},
        '-Warray-bounds=2': {'since': '4.8', 'min_version': '4.8'},
        '-Wformat-overflow': {'since': '7.0', 'min_version': '7.0'},
        '-Wformat-truncation': {'since': '7.0', 'min_version': '7.0'},
        '-Wdouble-promotion': {'since': '4.5', 'min_version': '4.5'},
        '-Wimplicit-fallthrough': {'since': '7.0', 'min_version': '7.0'},
        '-Wcast-qual': {'since': '3.3', 'min_version': '3.3'},
        '-Wshadow': {'since': '2.95', 'min_version': '2.95'},
        '-Wwrite-strings': {'since': '2.95', 'min_version': '2.95'},
        '-Wformat-security': {'since': '3.4', 'min_version': '3.4'},
        '-Wnull-dereference': {'since': '6.0', 'min_version': '6.0'},
        '-Wstack-protector': {'since': '4.9', 'min_version': '4.9'},
        '-Wtrampolines': {'since': '4.6', 'min_version': '4.6'},
        '-Wstrict-overflow': {'since': '4.2', 'min_version': '4.2'},
        '-Warray-bounds': {'since': '4.3', 'min_version': '4.3'},
        '-Wshift-overflow': {'since': '6.0', 'min_version': '6.0'},
        '-Wduplicated-cond': {'since': '6.0', 'min_version': '6.0'},
        '-Wduplicated-branches': {'since': '6.0', 'min_version': '6.0'},
        '-Wlogical-op': {'since': '6.0', 'min_version': '6.0'},
        '-Wrestrict': {'since': '8.0', 'min_version': '8.0'},
        '-Wimplicit-int': {'since': '3.0', 'min_version': '3.0'},
        '-Wold-style-definition': {'since': '4.3', 'min_version': '4.3'},
        '-Wmissing-prototypes': {'since': '2.95', 'min_version': '2.95'},
        '-Wpedantic': {'since': '3.2', 'min_version': '3.2'},
        '-Wconversion': {'since': '4.3', 'min_version': '4.3'},
        '-Wtraditional-conversion': {'since': '4.6', 'min_version': '4.6'},
        '-Wdeclaration-after-statement': {'since': '4.6', 'min_version': '4.6'},
        '-Wundef': {'since': '3.4', 'min_version': '3.4'},
        '-Wuninitialized': {'since': '2.95', 'min_version': '2.95'},
        '-Wpointer-sign': {'since': '4.1', 'min_version': '4.1'},
        '-Wsizeof-pointer-memaccess': {'since': '4.7', 'min_version': '4.7'},
        '-Wstrict-aliasing': {'since': '3.4', 'min_version': '3.4'},
        '-Wstack-usage': {'since': '7.0', 'min_version': '7.0'},
        '-Wattribute-warning': {'since': '9.0', 'min_version': '9.0'},
    }
    return flag_db.get(flag, {'since': 'unknown', 'min_version': 'unknown'})


def extract_relevant_line(error_msg):
    """Extract the first non-empty line with error context"""
    lines = [line.strip() for line in error_msg.split('\n') if line.strip()]
    for line in lines:
        if any(keyword in line for keyword in ['error:', 'warning:']):
            return line
    return error_msg[:200] + "..." if len(error_msg) > 200 else error_msg

def extract_template_trace(error_msg):
    """Extract C++ template instantiation trace"""
    return [line.strip() for line in error_msg.split('\n') if "required from" in line]

def extract_sanitizer_details(error_msg):
    """Extract sanitizer-specific information"""
    details = []
    for line in error_msg.split('\n'):
        if any(kw in line for kw in ['SUMMARY:', 'AddressSanitizer:']):
            details.append(line.strip())
    return '\n'.join(details[:3])

def extract_warnings(warning_message):
    """Extract and format warnings from compiler output"""
    warnings = [line.strip() for line in warning_message.split('\n') if "warning:" in line]
    return {
        "count": len(warnings),
        "items": warnings,
        "most_common": Counter(w.split(':')[-1].strip() for w in warnings).most_common(3)
    }

def get_optimization_level(flags):
    """Extract optimization level from flags"""
    for flag in flags:
        if flag.startswith('-O'):
            return flag
    return "-O0 (default)"

def generate_debugging_tips(crash_reason, standard):
    """Generate helpful debugging tips based on error type"""
    tips = []
    
    if "C89 compatibility" in crash_reason:
        tips.append(f"Try compiling with {standard.replace('c89', 'c99')} or newer standard")
        tips.append("Move all variable declarations to the start of their blocks")
        tips.append("Declare loop counters before the for statement")
    
    elif "Unsupported flag" in crash_reason:
        tips.append("Check your GCC version with 'gcc --version'")
        tips.append("Consult GCC documentation for version-specific flags")
    
    elif "Linker error" in crash_reason:
        tips.append("Check for missing source files in your compilation")
        tips.append("Verify all required libraries are linked properly")
    
    return tips if tips else ["Review compiler output for specific error details"]


def print_compilation_summary(results, error_log, success_log,ice_error_log, output_file="compilation_summary.txt"):
    """Print and save a comprehensive compilation summary"""
    success = sum(1 for r in results if r["status"] == "Success")
    failures = len(results) - success
    
    summary_lines = [
        f"\n{' Compilation Summary ':=^60}",
        f"Total attempts: {len(results)}",
        f"Successful compilations: {success}",
        f"Failed compilations: {failures}",
    ]
    
    if failures > 0:
        summary_lines.append("\nTop Failure Reasons:")
        reasons = Counter(r["crash_reason"] for r in results if r["status"] == "Failed")
        for reason, count in reasons.most_common(5):
            summary_lines.append(f"- {reason}: {count} time(s)")
    
    summary_lines.extend([
        f"\nDetailed results saved to:",
        f"- Successes: {success_log}",
        f"- Internal compilation errors: {ice_error_log}",
        f"- Errors: {error_log}",
        "=" * 60
    ])

    # Print summary to console
    print("\n".join(summary_lines))

    # Save summary to file
    with open(output_file, "w") as file:
        file.write("\n".join(summary_lines))

    print(f"\nSummary saved to: {output_file}")


if __name__ == '__main__':
    try:
        # while True:
        #     print("Generating and compiling programs...")
        #     generate_programs_and_compile()
        
        generate_programs_and_compile()
    except Exception as e:
        print(e)

 #python3 -m Compiler_Tester.compiler_tester 