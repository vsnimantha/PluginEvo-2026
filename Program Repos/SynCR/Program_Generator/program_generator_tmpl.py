from Program_Generator.program_generator_common import ProgramGenerator
from Template_Manager.template_manager_impl import TemplateManagerImpl
from Data.block_map_loader import load_block_map
from Config.global_config import config
from Program_Generator.Template_Handler.template_handler_single import TemplateHandlerSingle
from Program_Generator.Template_Handler.template_handler_multi import TemplateHandlerMulti
from Utilities.file_management_utils import create_folder_with_timestamp,create_folder
from Utilities.constants import Constants
import subprocess
import os

class ProgramGeneratorFull(ProgramGenerator):
    
    def __init__(self):
        if not hasattr(self, 'initialized'):  
            super().__init__()
            self.initialized =True
            self.template_manager = TemplateManagerImpl(config.PATHS.template_path)
            self.block_map=load_block_map()


    def generate_program(self):
        folder_path,time_stamp=create_folder_with_timestamp(config.PATHS.output_path) #time_stamp is used in the response from the server so that it can be saved in the same structure in requester app
        config.update_config_value('PATHS', 'current_generating_code_path', folder_path) #setting the current execution folder path

        templateHandler=None
        if config.PROGRAM_GENERATION.smart_generation:
            templateHandler=TemplateHandlerMulti(self.grammar_parser,folder_path)
            generated_program_list=templateHandler.generate_program()

            config.update_config_value('PATHS', 'current_generating_code_path', Constants.DEFAULT_OUTPUT_PATH) #resetting the current execution folder path

            return generated_program_list,time_stamp
        else:
            templateHandler=TemplateHandlerSingle(self.grammar_parser,folder_path)
            generated_program,file_name=templateHandler.generate_program()

            config.update_config_value('PATHS', 'current_generating_code_path', Constants.DEFAULT_OUTPUT_PATH) #resetting the current execution folder path
            
            return (generated_program,file_name),time_stamp


def generate_program_main_wihtout_feedback():   
    program_generator = ProgramGeneratorFull()
    programs,time_stamp=program_generator.generate_program()

#Testing the program generator and extracting the feedback
def generate_program_main():   
    program_generator = ProgramGeneratorFull()
    programs,time_stamp=program_generator.generate_program()
    return get_feedback(programs, time_stamp)


def compile_program(source_path, compiled_path, data_folder):
    """ Verifies the existence and compiles the program, returning compilation data. """
    compilation_data = {
        "source_path": source_path,
        "exists": os.path.exists(source_path),
        "compiled_successfully": False,
        "error": None
    }

    if compilation_data["exists"]:
        try:
            compile_command = f"gcc {source_path} -o {compiled_path}"  # Adjust based on your compiler
            result = subprocess.run(compile_command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Compilation successful: {source_path} -> {compiled_path}")
                compilation_data["compiled_successfully"] = True
            else:
                print(f"Compilation failed for {source_path}: {result.stderr}")
                compilation_data["error"] = result.stderr
        except Exception as e:
            print(f"Error compiling {source_path}: {e}")
            compilation_data["error"] = str(e)
    else:
        print(f"Program does not exist: {source_path}")

    return compilation_data

def get_feedback(programs, timestamp):
    program_count = 0  # Counter for number of programs
    feedback_data = []  # List to store compilation data for each program

    if programs:
        if config.PROGRAM_GENERATION.smart_generation:
            print("Smart random generation........................")
            for rendered_template, file_name in programs:
                if file_name:
                    path = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/{file_name}"
                    path_compile = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}"
                    folder_path_compile = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled"
                    folder_path_data = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{file_name}"

                    create_folder(folder_path_compile)
                    create_folder(folder_path_data)

                    compilation_result = compile_program(path, path_compile, folder_path_data)
                    feedback_data.append(compilation_result)
                    program_count += 1  # Increment program count
                else:
                    print("File name error, file name not found, please check whether it exists")

        else:
            print("Single random generation.........")

            if len(programs) > 1 and programs[1]:  # Ensure index exists
                path = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/{programs[1]}"
                path_compile = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{programs[1]}"
                folder_path_compile = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled"
                folder_path_data = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{programs[1]}"

                create_folder(folder_path_compile)
                create_folder(folder_path_data)

                compilation_result = compile_program(path, path_compile, folder_path_data)
                feedback_data.append(compilation_result)
                program_count += 1  # Increment program count
            else:
                print("File name error, file name not found, please check whether it exists")

    print(f"Total programs processed: {program_count}")
    return feedback_data  


def process_feedback(feedback_data,num_programs):
    """ Processes feedback and prints summary of results. """
    flattened_feedback = [program for entry in feedback_data for program in entry]

    total_programs = len(flattened_feedback)
    compiled_successfully = sum(1 for program in flattened_feedback if program['compiled_successfully'])
    failed_compilation = total_programs - compiled_successfully

    print(f"\nSummary:")
    print(f"Generated {num_programs} programs.")
    print(f"Successfully static analysed {total_programs} programs.")
    print(f"{compiled_successfully} programs compiled successfully.")
    print(f"{failed_compilation} programs failed to compile.")

def process_feedback_v2(feedback_data, num_programs):
    """ Processes feedback and prints summary of results for structured data. """
    
    total_programs = len(feedback_data)
    compiled_successfully = sum(1 for program in feedback_data if program['compiled_successfully'])
    failed_compilation = total_programs - compiled_successfully

    print(f"\nSummary:")
    print(f"Generated {num_programs} programs.")
    print(f"Successfully static analysed {total_programs} programs.")
    print(f"{compiled_successfully} programs compiled successfully.")
    print(f"{failed_compilation} programs failed to compile.")

if __name__ == '__main__':
    program_data= generate_program_main_wihtout_feedback()
    # print(program_data)
    # process_feedback_v2(program_data,config.PROGRAM_GENERATION.combination_limit)
    feedback=[]
    # num_programs = 100
    # for item in range(0,num_programs):
    #     feedback.append(generate_program_main())
    
    # process_feedback(feedback,num_programs)
   #python3 -m Program_Generator.program_generator_tmpl 