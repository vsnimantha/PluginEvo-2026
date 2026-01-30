import re
from Utilities.compiler_tester_utils import get_gcc_version, extract_relevant_line, extract_template_trace, extract_sanitizer_details

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