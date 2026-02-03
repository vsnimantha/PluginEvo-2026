from pathlib import Path
import Plugin_Manager.coverage_generator as coverage_generator
import Plugin_Manager.plugin_complier as plugin_compiler
import Plugin_Manager.program_complier_with_plugin as program_compiler_with_plugin
from Config.global_config import config
import sys
import os
import subprocess
import Feedback_Manager.program_requester as program_requester
import threading
import Utilities.file_management_utils as file_management_utils
import Utilities.debug_print_handler_utils as debug_print_handler_utils
import Utilities.program_debug_info_utils as program_debug_info_utils

from Utilities.loading_animation import Spinner






def compile_plugin_with_coverage_flags():
    
    try:
        output_plugin_path=f"{config.PATHS.plugin_output_path}{config.PATHS.plugin_output_name}"


        if config.COVERAGE_ANALYSER.compile_plugin_always:
            plugin_compiler.compile_gcc_plugin(
                source_dir=config.PATHS.gcc_plugin_path,
                output_plugin=output_plugin_path
            )
        else:
            compiled_plugin_file_path = Path(output_plugin_path)
            if compiled_plugin_file_path.is_file():
                print(f"Compiled plugin exists at: {compiled_plugin_file_path}")
            else:
                print(f"Compiled plugin  does not exist at: {compiled_plugin_file_path}")
                plugin_compiler.compile_gcc_plugin(
                source_dir=config.PATHS.gcc_plugin_path,
                output_plugin=output_plugin_path)
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)

def complie_program_with_plugin(program="Plugin_Manager/Sample_Program/funcp-encrypt/test.c"):
    cpp_file = program
    program_directory = os.path.dirname(program)
    file_name = Path(os.path.basename(program)).stem

    output_name = f"{program_directory}/{file_name}.o"

    plugin_path = f"{config.PATHS.plugin_output_path}{config.PATHS.plugin_output_name}"
   
    print("[DEBUG] Program file is:", cpp_file)

    # Parse optional plugin arguments
    plugin_args = {}

    if config.COVERAGE_ANALYSER.use_specific_plugin_arguments:
        if config.PLUGIN_SPECIFIC_ARUGMENTS:
            args = config._config['PLUGIN_SPECIFIC_ARUGMENTS'].items()
        for key,value in args:
                plugin_args[key] = value
    
    return program_compiler_with_plugin.compile_with_gcc_plugin(cpp_file, output_name, plugin_path, plugin_args)

def generate_coverage(program_folder="Test_App",program_name_path="test_latent_entropy.c"):
      # Verify gcov is installed
    if not coverage_generator.check_gcov_installation():
        sys.exit(1)
    
    # Find source files automatically
    try:
        exclude_dirs=[]
        if config.PLUGIN_FOLDER_EXCLUDES:
            excluded_items = config._config['PLUGIN_FOLDER_EXCLUDES'].items()
            for key,value in excluded_items:
                    exclude_dirs.append(value)

        source_files = coverage_generator.find_source_files(config.PATHS.plugin_output_path,config.COVERAGE_ANALYSER.source_extensions,exclude_dirs=exclude_dirs)

        if not source_files:
            print(f"No source files found in {config.PATHS.plugin_output_path} with extensions {config.COVERAGE_ANALYSER.source_extensions}")
            sys.exit(1)
            
        print(f"Found {len(source_files)} source files:")
        for src in source_files:
            print(f"  - {src}")
    
    except Exception as e:
        print(f"Error finding source files: {str(e)}")
        sys.exit(1)
    
    # Generate reports
    try:
        program_name = Path(program_name_path).name
        report_path=f"{config.PATHS.main_report_path}/{program_folder}/{program_name}"
        gcov_json_path=f"{report_path}/{config.PATHS.gcov_json_output_path}"
        if config.COVERAGE_ANALYSER.generate_gcov_data:
            coverage_generator.generate_gcov_reports(config.PATHS.plugin_output_path,
                                                     config.PATHS.plugin_output_name,
                                                     source_files,
                                                     report_path,
                                                     gcov_json_path)
        

        gcovr_flags=[]
        if config.GCOVR_CONFIGURATION.gcov_version and config.GCOVR_CONFIGURATION.gcov_version!="default":
            gcovr_flags.append("--gcov-executable")
            gcovr_flags.append(config.GCOVR_CONFIGURATION.gcov_version)
        
        if config.GCOVR_CONFIGURATION.verbose:
            gcovr_flags.append("--verbose")


        coverage_summary=""
        if config.COVERAGE_ANALYSER.generate_gcovr_html_report:
            coverage_generator.generate_html_report(f"{os.getcwd()}/{report_path}/{config.PATHS.gcovr_html_report_path}",gcovr_flags)
        
        if config.COVERAGE_ANALYSER.generate_gcovr_json_report:
            coverage_generator.generate_json_report(f"{os.getcwd()}/{report_path}/{config.PATHS.gcovr_json_report_path}",gcovr_flags)
        
        if config.COVERAGE_ANALYSER.generate_gcovr_jacoco_xml_report:
            coverage_generator.generate_jacoco_xml_report(f"{os.getcwd()}/{report_path}/{config.PATHS.gcovr_jacoco_xml_report_path}",gcovr_flags)

        if config.COVERAGE_ANALYSER.print_gcovr_data_to_console:
            coverage_summary=coverage_generator.print_gcovr_summary(f"{os.getcwd()}/{report_path}/{config.PATHS.gcovr_summary_report_path}",gcovr_flags)

        return coverage_summary
    
    except subprocess.CalledProcessError as e:
        print(f"\nError during coverage generation: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

def main():

    if config.COVERAGE_ANALYSER.clean_gcov_report_directory:
        file_management_utils.clean_directory(config.PATHS.main_report_path)

    if config.COVERAGE_ANALYSER.clean_generated_program_directory:
        file_management_utils.clean_directory(config.PATHS.generated_program_save_path)
    
    print("Sending the request and the time may depend on the number of programs needed to be generated...")
    generated_programs=[]
    program_folder_path=""
    url = config.FEEDBACK_MANAGER.generate_url

    spinner = Spinner(message="Awaiting Response")
    spinner.start()

    # Send the API request
    response = program_requester.request_programs(url)

    # Stop the spinner once the request is complete
    spinner.stop()
    
    if response and response.status_code == 200:
        print("Request successful!") #Debug print
        print("Response:", response.text) #Debug print
        generated_programs,program_folder_path=program_requester.process_response(response.text)

        print(f"Total of {len(generated_programs)} generated programs saved at {program_folder_path}")
        
        # print("Compiling the plugin...") #Debug print
        # compile_plugin_with_coverage_flags()
        if generated_programs and len(generated_programs)>=1:
            print("Starting the coverage analysis...")
            for item in generated_programs:
                
                print("Compiling the plugin...") #Debug print
                compile_plugin_with_coverage_flags()
                complie_program_with_plugin(program=item)
                generate_coverage(program_folder_path,item)
                #Removing the coverage data from the plugin directory once the process is completed
                if config.COVERAGE_ANALYSER.clear_gcov_data:
                    print()
                    print("Cleaning up the plugin directory's gcov data")
                    coverage_generator.clean_up(config.PATHS.plugin_output_path)
    else:
        print("\nNo response received. Please verify that the server is running and accessible. If the issue persists, it may be due to another error.")
        handle_failed_request_with_timeout(timeout=5)

            

def handle_failed_request_with_timeout(timeout):
    """
    Handles user input for running a sample program with a timeout mechanism.
    
    Parameters:
    timeout (int): The duration (in seconds) after which the program exits if no input is provided.
    """

    def timeout_handler():
        """
        Function to handle the timeout event. 
        Prints a message and exits the program when the timeout is reached.
        """
        print("\nNo response received. Exiting...")
        os._exit(1)

    while True:
        try:
            timer = threading.Timer(timeout, timeout_handler)
            timer.start()
            
            user_input = input("Would you like to run the generate coverage info with the built-in sample program? (Y/N): ").strip().lower()
            if user_input in ["y", "yes"]:
                main_test()
                break 
            elif user_input in ["n", "no"]:
                break  
            else:
                print("Invalid input. Please enter 'Y' or 'N'.")
                continue
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            timer.cancel()


def main_test():
    if config.COVERAGE_ANALYSER.clean_gcov_report_directory:
        file_management_utils.clean_directory(config.PATHS.main_report_path)

    if config.COVERAGE_ANALYSER.clean_generated_program_directory:
        file_management_utils.clean_directory(config.PATHS.generated_program_save_path)

    compile_plugin_with_coverage_flags()
    complie_program_with_plugin()
    generate_coverage()

    #Removing the coverage data from the plugin directory once the process is completed
    if config.COVERAGE_ANALYSER.clear_gcov_data:
        print()
        print("Cleaning up the plugin directory's gcov data")
        coverage_generator.clean_up(config.PATHS.plugin_output_path)

    

if __name__ == "__main__": 

    log_file=""
    if config.GENERAL.debug_mode:
        debug_print_handler_utils.enable_print()
        log_file=program_debug_info_utils.start_write_console_output_to_log_file() 
    else:
        debug_print_handler_utils.disable_print() 



    if config.COVERAGE_ANALYSER.offline_mode:
        main_test()
    else:
        main()


    
    if config.GENERAL.debug_mode:
        program_debug_info_utils.stop_write_console_output_to_log_file(log_file) 

# python3 -m Executor.executor 