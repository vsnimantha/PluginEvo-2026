===========================================================
Code Generation & Coverage Analysis Configuration Reference  
===========================================================

**[PATHS]**

gcc_plugin_path            = Primary GCC plugin directory (should not end with /)
plugin_output_path         = Main plugin output directory (should end with /)
plugin_output_name         = Compiled plugin filename (.so)
generated_program_save_path = Directory for generated programs
main_report_path           = Root directory for all reports  
gcov_json_output_path      = Gcov JSON report directory
gcovr_html_report_path     = Gcovr HTML report directory  
gcovr_json_report_path     = Gcovr JSON report directory
gcovr_jacoco_xml_report_path = Gcovr JaCoCo XML report directory
specific_plugin_headers_inclue_path = Custom plugin headers path (for FIRES plugin or any plugin that needs custom headers)

[COVERAGE_ANALYSER]

compile_plugin_always      = [True/False] Control whether to compile the plugin always
clear_gcov_data           = [True/False] Clear Gcov data from the folder
**Special Note, if the plugin does not need to be compiled always, make sure to switch the clear_gcov_data flag to False, if not, gcov will not have any data to process best configuration option would be to [compile_plugin_always=True and clear_gcov_data=True] or [compile_plugin_always=False and clear_gcov_data=False] unless you need to specifically clean the data even when the plugin does not compile always. However, run it once with the [compile_plugin_always=True and clear_gcov_data=False] so that it keeps the gcov files if you accdiently remove the files**


clean_gcov_report_directory = [True/False] Clear Gcov reports before generation
clean_generated_program_directory = [True/False] Clean program output directory  
print_gcovr_data_to_console = [True/False] Show Gcovr output in console
generate_gcovr_html_report = [True/False] Create HTML coverage report  
generate_gcovr_json_report = [True/False] Generate JSON coverage report
generate_gcovr_jacoco_xml_report = [True/False] Produce JaCoCo XML report  
generate_gcov_data        = [True/False] Run Gcov analysis
source_extensions         = List of source file extensions to analyze (e.g., ['.c', '.cc', '.cpp'])
format_json_output        = [True/False] Pretty-print JSON reports
prompt_test_program_when_request_fails = [True/False] Interactive fallback
offline_mode              = [True/False] Disable network operations
use_plugin_specific_additional_includes = [True/False] Enable custom includes (FIRES Plugin)
use_specific_plugin_headers = [True/False] Use dedicated header path (FIRES plugin)
use_specific_plugin_arguments = [True/False] Apply plugin-specific args
use_additional_plugin_compiler_flags = [True/False] Enable additional plugin compilation flags
gcov_version              = Gcov version to use (e.g., gcov-10), use 'default' to use the default configuration of the system
use_additional_program_compiler_flags = [True/False] Enable additional program compilation flags

[PLUGIN_COMPILATION_GCC_CONFIGURATION]
gcc_version               = GCC version for plugin compilation (e.g., gcc-10) use 'default' to use the default configuration of the system
cxx_version               = G++ version for plugin compilation (e.g., g++-10) use 'default' to use the default configuration of the system
use_condition_coverage    = [True/False] Enable condition coverage analysis

[ADDITIONAL_PLUGIN_COMPILER_FLAGS]
flag_1                    = Additional compiler flag 1 (e.g., -std=gnu++14)
flag_2                    = Additional compiler flag 2 (e.g., -w)
...                       = Additional flags as needed

[PLUGIN_SPECIFIC_ADDITIONAL_INCLUDES]
include_1                 = Additional include directory 1 (e.g., Asm)
include_2                 = Additional include directory 2 (e.g., Techniques)
...                       = Additional includes as needed

[PLUGIN_SPECIFIC_ARGUMENTS] - Plugin specific arguments go here, below are some examples
function                  = Target function for analysis (leave empty for all)
techniqueType             = CFED technique type (e.g., fullCFED)
techniqueSpecific         = Specific technique (e.g., RACFED)
selectiveLevel            = Selective analysis level (integer, 0 for none)

[PLUGIN_FOLDER_EXCLUDES]
exclude 1=folder_name     = Directories to exclude from analysis

[PROGRAM_COMPILATION_GCC_CONFIGURATION]
gcc_version               = Target GCC path (e.g., arm-none-eabi-gcc) use 'default' to use the default configuration of the system
cxx_version               = Target G++ path (e.g., arm-none-eabi-g++) use 'default' to use the default configuration of the system

[PROGRAM_COMPILATION_ADDITIONAL_FLAGS_CONFIGURATION]
flag_1                    = Target compilation flag 1 (e.g., -mlittle-endian)
flag_2                    = Target compilation flag 2 (e.g., -mthumb)
...                       = Additional target flags as needed

[GCOVR_CONFIGURATION]
gcov_version              = Gcov version for Gcovr (e.g., gcov-10) use 'default' to use the default configuration of the system
verbose                   = [True/False] Verbose Gcovr output

[GENERAL]
debug_mode                = [True/False] Enable debugging output

[FEEDBACK_MANAGER]  
server_host               = Feedback service hostname/IP (e.g., 0.0.0.0)
server_port               = Feedback service port number (e.g., 5001)
generate_url              = Program generation endpoint URL
destination_url           = Report submission endpoint URL

=== EXAMPLE CONFIGURATION ===

[PATHS]
gcc_plugin_path = /home/user/FIRES/cfed_plugin
plugin_output_path = /home/user/FIRES/cfed_plugin/
plugin_output_name = compiled_plugin.so
generated_program_save_path = Generated_Programs
main_report_path = Reports

[COVERAGE_ANALYSER]
compile_plugin_always = False
clear_gcov_data = False
generate_gcovr_html_report = True
generate_gcovr_json_report = True
source_extensions = ['.c', '.cpp']
offline_mode = True

[PLUGIN_COMPILATION_GCC_CONFIGURATION]
gcc_version = gcc-10
cxx_version = g++-10
use_condition_coverage = True

=== USAGE NOTES ===  

1. All paths use forward slashes (/)
2. Boolean values must be True/False (case-sensitive)
3. Add more include/exclude entries with incrementing numbers
4. Enable debug_mode for troubleshooting
5. Set offline_mode=True for air-gapped systems
6. Source extensions format: ['.ext1', '.ext2']
7. Multiple plugin arguments go on separate lines
8. Clean flags ensure fresh analysis environments
9. For ARM targets, specify full path to toolchain compilers
10. Plugin-specific headers and includes are primarily for FIRES plugin