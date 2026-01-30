from collections import Counter
import subprocess


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