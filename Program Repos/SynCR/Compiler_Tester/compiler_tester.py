import subprocess
import sys
import Utilities.file_management_utils as file_utils
import json
import re

from Utilities.constants import Constants
from Utilities.compiler_tester_utils import extract_warnings, get_optimization_level, generate_debugging_tips
from Program_Generator.program_generator_tmpl import ProgramGeneratorFull
from pathlib import Path
from Config.global_config import config
from collections import Counter
from Compiler_Tester.error_classification import classify_error
from Compiler_Tester.compilation_flags import maximum_base_flags,minimal_base_flags
from Compiler_Tester.differential_tester import compare_binaries_in_folder


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
                    path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}/{file_name}"
                    folder_path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}/"
                    folder_path_data=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{file_name}"
                    file_utils.create_folder(folder_path_compile)
                    file_utils.create_folder(folder_path_data)
                    compile_program(path,path_compile,folder_path_data,folder_path_compile)
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
                compile_program(path,path_compile,folder_path_data,folder_path_compile)

            else:
                print("File name error, file name not found, please check whether it exists")

# def compile_program(program_file, compile_output, folder_path_data,folder_path_compile=None,compiler_flag_mode="Min",return_summary=True):
#     error_log_file = f"{folder_path_data}/error_log.json"
#     ice_error_log_file = f"{folder_path_data}/ice_error_log.json"
#     success_log_file = f"{folder_path_data}/success_log.json"
#     compilation_summary_log_file = f"{folder_path_data}/summary_log.txt"
#     language = config.PROGRAM_GENERATION.programming_language.lower()

#     print("Compiling C/C++ file:", program_file)

#     if not Path(program_file).exists():
#         error_info = {
#             "filename": program_file,
#             "language": language,
#             "command": None,
#             "error": "Source file not found",
#             "crash_reason": "File does not exist",
#             "readable_error": {
#                 "summary": "Source file missing",
#                 "details": f"The specified source file '{program_file}' was not found",
#                 "solution": "Check the file path and ensure the file exists",
#                 "severity": "Critical"
#             }
#         }
#         with open(error_log_file, "w") as f:
#             json.dump(error_info, f, indent=4)
#         print(f"Error logged to {error_log_file}")
#         return
    
    

#     compilers_c = ["gcc", "gcc-13", "gcc-12", "gcc-11", "gcc-10","clang","clang-17","clang-16","clang-15"]
#     compilers_cpp = ["g++", "g++-13", "g++-12", "g++-11", "g++-10","clang++","clang++-17","clang++-16","clang++-15"]
#     # compilers_c = ["clang"]
#     # compilers_cpp = ["clang++"]

#     compiler_running=compilers_c if language == 'c' else compilers_cpp

#     for item in compiler_running:
#         compiler=item
#         error_log_file = f"{folder_path_data}/error_log_{compiler}.json"
#         ice_error_log_file = f"{folder_path_data}/ice_error_log_{compiler}.json"
#         success_log_file = f"{folder_path_data}/success_log_{compiler}.json"
#         differential_log_file = f"{folder_path_data}/differential_log_{compiler}.json"
#         compilation_summary_log_file = f"{folder_path_data}/summary_log_{compiler}.txt"

        
#         base_flags = maximum_base_flags if compiler_flag_mode=="Max" else minimal_base_flags

#         # Select compiler based on language
#         # compiler = "gcc" if language == 'c' else "g++"
#         standards = base_flags['standards'].get(language, [])
        
#         # Systematic testing approach (700+ combinations)
#         test_combinations = [
#             # Base test with all warnings
#             base_flags['warnings'],
            
#             # Test each optimization level with basic warnings
#             *[[opt] + base_flags['warnings'][:5] for opt in base_flags['optimizations']],
            
#             # Add sanitizer tests
#             *[[sanitizer] + base_flags['warnings'][:5] for sanitizer in base_flags['sanitizers']],
            
#             # Add architecture tests
#             *[[arch] + base_flags['warnings'][:5] for arch in base_flags['architecture']],
            
#             # Test standards with basic warnings
#             *[base_flags['warnings'][:3] + [std] for std in standards],
            
#             # Test debug flags
#             *[[debug] + base_flags['warnings'][:3] for debug in base_flags['debug']],
            
#             # Test code generation flags
#             *[[codegen] + base_flags['warnings'][:3] for codegen in base_flags['codegen']],
#         ]
        
#         results = []     
#         # Test all combinations
#         for std in standards:
#             for test_flags in test_combinations:
#                 output_suffix = f"_{compiler}_{std[5:]}_{test_flags}_{hash(tuple(test_flags)) % 1000:04d}"
#                 output_file = f"{compile_output}{output_suffix}.o"
                
#                 cmd = [compiler, std] + test_flags + [program_file, "-o", output_file]
#                 print("Compile command:", " ".join(cmd))
                
#                 try:
#                     result = subprocess.run(
#                         cmd,
#                         check=True,
#                         stderr=subprocess.PIPE,
#                         stdout=subprocess.PIPE,
#                         timeout=30
#                     )
                    
#                     result_info = {
#                         "filename": program_file,
#                         "language": language,
#                         "standard": std,
#                         "flags": test_flags,
#                         "command": " ".join(cmd),
#                         "status": "Success",
#                         "output_file": output_file,
#                         "warnings": result.stderr.decode(),
#                         "compiler":compiler,
#                         "readable_summary": {
#                             "status": "Compilation successful",
#                             "warnings": extract_warnings(result.stderr.decode()),
#                             "optimization_level": get_optimization_level(test_flags),
#                             "standard_used": std,
#                             "flag_count": len(test_flags),
#                             "flags_used": test_flags
#                         }
#                     }
#                     results.append(result_info)
#                     print(f"Successfully compiled with {std} and flags")
#                 except subprocess.CalledProcessError as e:
#                     error_message = e.stderr.decode()
#                     print(f"Compilation failed:", error_message)

#                     crash_reason, readable_error = classify_error(error_message, std, test_flags,compiler)
                    
#                     result_info = {
#                         "filename": program_file,
#                         "language": language,
#                         "standard": std,
#                         "flags": test_flags,
#                         "command": " ".join(cmd),
#                         "status": "Failed",
#                         "error": error_message,
#                         "crash_reason": crash_reason,
#                         "compiler":compiler,
#                         "readable_error": readable_error,
#                         "debugging_tips": generate_debugging_tips(crash_reason, std),
#                         "flags_used": test_flags
#                     }
#                     results.append(result_info)

#                 except subprocess.TimeoutExpired:
#                     result_info = {
#                         "filename": program_file,
#                         "language": language,
#                         "standard": std,
#                         "flags": test_flags,
#                         "command": " ".join(cmd),
#                         "status": "Failed",
#                         "error": "Compilation timed out",
#                         "crash_reason": "Timeout",
#                         "compiler":compiler,
#                         "readable_error": {
#                             "summary": "Compilation timed out",
#                             "details": "Compiler took more than 30 seconds to process",
#                             "solution": "Try with fewer optimization flags or check for complex templates/includes",
#                             "severity": "High",
#                             "possible_causes": [
#                                 "Excessive template instantiation",
#                                 "Compiler bug with specific flag combination",
#                                 "System resource constraints"
#                             ]
#                         },
#                         "flags_used": test_flags
#                     }
#                     results.append(result_info)

    
#         #Section differential testing.
#         differential_testin_based_line_compilation = False #Enable disable differential testing
#         mismatch_results = []
#         if differential_testin_based_line_compilation:
#             base_line_file = f"{compile_output}_{compiler}_baseline.o"
#             cmd = [compiler, "-O0","-Wall"] + [program_file, "-o", base_line_file]
#             result = subprocess.run(
#                         cmd,
#                         check=True,
#                         stderr=subprocess.PIPE,
#                         stdout=subprocess.PIPE,
#                         timeout=30
#                     )
            
#             mismatch_results, symbolic_output = compare_binaries_in_folder(folder_path_compile,program_file)
#             print("Symbolic Output")
#             print(symbolic_output)    

#             if mismatch_results:
#                 print(f"\n🧪 Differential mismatches found: {len(mismatch_results)}")
#                 for m in mismatch_results:
#                     # Decode keys if needed
#                     m = {k.decode() if isinstance(k, bytes) else k: v for k, v in m.items()}
#                     print(f"🔹 Mismatch in: {m['variant_file']} (vs {m['baseline_file']})")
#             else:
#                 print()
#                 print("No differential mismatches found.")


            
            
#         # Save results
#         # TODO:: Implement breaking the files between multiple files
#         # To address the large files.
        
#         with open(differential_log_file, "w") as f:
#             json.dump(mismatch_results, f, indent=4)

#         with open(success_log_file, "w") as f:
#             json.dump([r for r in results if r["status"] == "Success"], f, indent=4)
        
#         with open(error_log_file, "w") as f:
#             json.dump([r for r in results if r["status"] == "Failed"], f, indent=4)

#         with open(ice_error_log_file, "w") as f:
#             json.dump([r for r in results if r["status"] == "Failed" and r["crash_reason"] == "Compiler Internal Error (ICE)"], f, indent=4)


#         print_compilation_summary(results, error_log_file, success_log_file,ice_error_log_file,differential_log_file,compilation_summary_log_file)


#         if return_summary:
#             # Build compact summary for GP
#             overall_summary = {
#                 "program_file": program_file,
#                 "total_attempts": len(results),
#                 "success_count": sum(1 for r in results if r["status"] == "Success"),
#                 "failure_count": sum(1 for r in results if r["status"] == "Failed"),
#                 "ice_count": sum(1 for r in results if r["status"] == "Failed" and r["crash_reason"] == "Compiler Internal Error (ICE)"),
#                 "timeout_count": sum(1 for r in results if r.get("crash_reason") == "Timeout"),
#                 "differential_mismatches": len(mismatch_results),
#                 "compiled": any(r["status"] == "Success" for r in results),
#                 "logs": {
#                     "success_log": success_log_file,
#                     "error_log": error_log_file,
#                     "ice_error_log": ice_error_log_file,
#                     "differential_log": differential_log_file,
#                     "summary_log": compilation_summary_log_file
#                 }
#             }


#             print(f"\n[SUMMARY DICT] {overall_summary}")

#             return overall_summary

def compile_program(program_file, compile_output, folder_path_data,
                    folder_path_compile=None, compiler_flag_mode="Min",
                    return_summary=True):
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

    compilers_c = ["gcc", "gcc-13", "gcc-12", "gcc-11", "gcc-10",
                   "clang", "clang-17", "clang-16", "clang-15"]
    compilers_cpp = ["g++", "g++-13", "g++-12", "g++-11", "g++-10",
                     "clang++", "clang++-17", "clang++-16", "clang++-15"]

    compiler_running = compilers_c if language == 'c' else compilers_cpp

    # Global aggregations across all compilers
    all_results = []
    all_mismatch_results = []
    logs_per_compiler = {}

    for item in compiler_running:
        compiler = item

        error_log_file = f"{folder_path_data}/error_log_{compiler}.json"
        ice_error_log_file = f"{folder_path_data}/ice_error_log_{compiler}.json"
        success_log_file = f"{folder_path_data}/success_log_{compiler}.json"
        differential_log_file = f"{folder_path_data}/differential_log_{compiler}.json"
        compilation_summary_log_file = f"{folder_path_data}/summary_log_{compiler}.txt"

        base_flags = maximum_base_flags if compiler_flag_mode == "Max" else minimal_base_flags
        standards = base_flags['standards'].get(language, [])

        test_combinations = [
            base_flags['warnings'],
            *[[opt] + base_flags['warnings'][:5] for opt in base_flags['optimizations']],
            *[[sanitizer] + base_flags['warnings'][:5] for sanitizer in base_flags['sanitizers']],
            *[[arch] + base_flags['warnings'][:5] for arch in base_flags['architecture']],
            *[base_flags['warnings'][:3] + [std] for std in standards],
            *[[debug] + base_flags['warnings'][:3] for debug in base_flags['debug']],
            *[[codegen] + base_flags['warnings'][:3] for codegen in base_flags['codegen']],
        ]

        results = []

        for std in standards:
            for test_flags in test_combinations:
                output_suffix = f"_{compiler}_{std[5:]}_{test_flags}_{hash(tuple(test_flags)) % 1000:04d}"
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
                        "compiler": compiler,
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
                    print("Compilation failed:", error_message)

                    crash_reason, readable_error = classify_error(
                        error_message, std, test_flags, compiler
                    )

                    result_info = {
                        "filename": program_file,
                        "language": language,
                        "standard": std,
                        "flags": test_flags,
                        "command": " ".join(cmd),
                        "status": "Failed",
                        "error": error_message,
                        "crash_reason": crash_reason,
                        "compiler": compiler,
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
                        "compiler": compiler,
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

        differential_testin_based_line_compilation = False
        mismatch_results = []

        if differential_testin_based_line_compilation:
            base_line_file = f"{compile_output}_{compiler}_baseline.o"
            cmd = [compiler, "-O0", "-Wall", program_file, "-o", base_line_file]
            result = subprocess.run(
                cmd,
                check=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                timeout=30
            )

            mismatch_results, symbolic_output = compare_binaries_in_folder(
                folder_path_compile, program_file
            )
            print("Symbolic Output")
            print(symbolic_output)

            if mismatch_results:
                print(f"\n🧪 Differential mismatches found: {len(mismatch_results)}")
                for m in mismatch_results:
                    m = {k.decode() if isinstance(k, bytes) else k: v
                         for k, v in m.items()}
                    print(f"🔹 Mismatch in: {m['variant_file']} (vs {m['baseline_file']})")
            else:
                print()
                print("No differential mismatches found.")

        with open(differential_log_file, "w") as f:
            json.dump(mismatch_results, f, indent=4)

        with open(success_log_file, "w") as f:
            json.dump([r for r in results if r["status"] == "Success"], f, indent=4)

        with open(error_log_file, "w") as f:
            json.dump([r for r in results if r["status"] == "Failed"], f, indent=4)

        with open(ice_error_log_file, "w") as f:
            json.dump(
                [r for r in results
                 if r["status"] == "Failed"
                 and r["crash_reason"] == "Compiler Internal Error (ICE)"],
                f,
                indent=4
            )

        print_compilation_summary(
            results,
            error_log_file,
            success_log_file,
            ice_error_log_file,
            differential_log_file,
            compilation_summary_log_file
        )

        # Aggregate per-compiler results
        all_results.extend(results)
        all_mismatch_results.extend(mismatch_results)
        logs_per_compiler[compiler] = {
            "success_log": success_log_file,
            "error_log": error_log_file,
            "ice_error_log": ice_error_log_file,
            "differential_log": differential_log_file,
            "summary_log": compilation_summary_log_file,
        }

    if return_summary:
        overall_summary = {
            "program_file": program_file,
            "total_attempts": len(all_results),
            "success_count": sum(1 for r in all_results if r["status"] == "Success"),
            "failure_count": sum(1 for r in all_results if r["status"] == "Failed"),
            "ice_count": sum(
                1 for r in all_results
                if r["status"] == "Failed"
                and r.get("crash_reason") == "Compiler Internal Error (ICE)"
            ),
            "timeout_count": sum(
                1 for r in all_results
                if r.get("crash_reason") == "Timeout"
            ),
            "differential_mismatches": len(all_mismatch_results),
            "compiled": any(r["status"] == "Success" for r in all_results),
            "logs_per_compiler": logs_per_compiler,
        }

        print(f"\n[SUMMARY DICT] {overall_summary}")
        return overall_summary

def print_compilation_summary(results, error_log, success_log,ice_error_log,differential_log, output_file="compilation_summary.txt"):
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
        f"- Differential Testing results: {differential_log}",
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

#  python3 -m Compiler_Tester.compiler_tester 