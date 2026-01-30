=============================================
Smart Code Generator Configuration Reference
=============================================

[PATHS]
grammar_path           = Path to grammar definition files
template_path          = Directory containing program templates  
output_path            = Main output directory 
generated_program_output = Subfolder for generated programs (Sub folder within the current_generating_code_path)
ast_json_output        = Directory for AST JSON exports (Sub folder within the current_generating_code_path)
ast_diagrams_output    = Directory for AST visualizations  (Sub folder within the current_generating_code_path)
current_generating_code_path = Active working directory (This will be automaticlally updated to the current directory and resetted after the execution)

[PROGRAM_GENERATION] 
build_a_random_template = [True/False] Create random templates
use_random_templates   = [True/False] Random template selection
specific_template      = Force specific template file
smart_generation = [True/False] Exhaustive generation  
combination_limit      = Max combinations to generate (int)
save_generated_programs = [True/False] Save output files
print_ast_to_console   = [True/False] Console AST display
save_ast               = [True/False] Save AST representations
open_saved_ast_images  = [True/False] Auto-open AST diagrams (Only works when the save_ast is True)
save_ast_as_json       = [True/False] Export AST as JSON
print_template_to_console = [True/False] Show template source
print_rendered_template_to_console = [True/False] Show filled templates
format_generated_code  = [True/False] Apply code formatting
static_analysis_of_generate_code = [True/False] Run static analysis
print_array_data       = [True/False] Display array contents
programming_language = [C,C++,(Any other future Languages)] Make sure grammar and template paths are set for each languages correctly

[TEMPLATE_GENERATION]
number_of_functions    = Target functions per template (int)  
number_of_other_elements = Non-function elements (int)

[GENERAL]  
debug_mode             = [True/False] Verbose debug output

[FEEDBACK_MANAGER]
server_host            = Feedback service host
server_port            = Feedback service port (int)
destination_url        = Compilation endpoint

=== EXAMPLE CONFIGURATION ===

[PATHS]
grammar_path = Grammar/Python
template_path = Templates/Python  
output_path = Output/Python
ast_json_output = AST/Python/JSON

[PROGRAM_GENERATION]
use_random_templates = True
combination_limit = 15
save_ast_as_json = True
format_generated_code = True

[TEMPLATE_GENERATION]  
number_of_functions = 3
number_of_other_elements = 4

[GENERAL]
debug_mode = False

=== USAGE NOTES ===

1. All paths are relative to project root
2. Use forward slashes (/) in paths
3. Boolean values must be True/False (case-sensitive)
4. Template counts are approximate targets
5. Disable console outputs in production
6. Enable debug_mode for troubleshooting