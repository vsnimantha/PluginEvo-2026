from fastapi import FastAPI,Query,Body
from Program_Generator.program_generator_tmpl_gp_compiler_test import ProgramGeneratorFull_GP_Compiler_Test
from Config.global_config import config
from Template_Manager.template_manager_impl import TemplateManagerImpl
from Compiler_Tester import compiler_tester
import uvicorn,time,os,uvicorn,itertools,random

import Utilities.file_management_utils as file_utils


app = FastAPI()
EVAL_DIR = "Compiler_Testing_For_GP"

@app.get("/health")
async def check_health():
    return True

# @app.get("/generate_programs_for_gp_compiler_test")
# async def generate_programs_for_gp_compiler_test(
#     number_of_programs: int = Query(2, alias="number_of_programs"),
#     programming_language: str = Query("C++", alias="programming_language"),
#     template: str = Query("random", alias="template")
# ):
#     try:
#         template_manager = TemplateManagerImpl(config.PATHS.template_path)
#         template_list = template_manager.templates

#         responses: list[dict] = []
#         distribution: dict[str, int] = {}

#         def process_generated(generated_programs, timestamp):
#             for rendered_template, file_name in generated_programs:
#                 compiler_summary=""
#                 if file_name:
#                     path=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/{file_name}"
#                     path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}/{file_name}"
#                     folder_path_compile=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}/"
#                     folder_path_data=f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{file_name}"
#                     file_utils.create_folder(folder_path_compile)
#                     file_utils.create_folder(folder_path_data)

#                     # Call compiler tester with positional args
#                     compiler_summary = compiler_tester.compile_program(
#                         path, path_compile, folder_path_data, folder_path_compile
#                     )

#                 responses.append({
#                     "code": rendered_template,
#                     "filename": file_name,
#                     "meta": compiler_summary
#                 })


#         if template.lower() == "random":
#             if not template_list:
#                 return {"error": "No templates available"}

#             num_templates = len(template_list)
#             base_count = number_of_programs // num_templates
#             remainder = number_of_programs % num_templates

#             for i, tmpl in enumerate(template_list):
#                 count_for_this_template = base_count + (1 if i < remainder else 0)
#                 if count_for_this_template == 0:
#                     continue

#                 tmpl_name = getattr(tmpl, "name", str(tmpl))
#                 program_generator = ProgramGeneratorFull_GP_Compiler_Test(
#                     num_programs=count_for_this_template,
#                     language=programming_language,
#                     template_type=tmpl_name
#                 )

#                 generated_programs, folder_name = program_generator.generate_program()
#                 process_generated(generated_programs, folder_name)
#                 distribution[tmpl_name] = distribution.get(tmpl_name, 0) + count_for_this_template

#         else:
#             program_generator = ProgramGeneratorFull_GP_Compiler_Test(
#                 num_programs=number_of_programs,
#                 language=programming_language,
#                 template_type=template
#             )
#             generated_programs, folder_name = program_generator.generate_program()
#             process_generated(generated_programs, folder_name)
#             distribution[template] = number_of_programs

#         return {"seeds": responses, "distribution": distribution}

#     except Exception as e:
#         return {"error": str(e)}

@app.get("/generate_programs_for_gp_compiler_test")
async def generate_programs_for_gp_compiler_test(
    number_of_programs: int = Query(2, alias="number_of_programs"),
    programming_language: str = Query("C++", alias="programming_language"),
    template: str = Query("random", alias="template")
):
    try:
        template_manager = TemplateManagerImpl(config.PATHS.template_path)
        template_list = template_manager.templates

        responses: list[dict] = []
        distribution: dict[str, int] = {}

        def process_generated(generated_programs, timestamp):
            for rendered_template, file_name in generated_programs:
                compiler_summary = ""
                if file_name:
                    path = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/{file_name}"
                    path_compile = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}/{file_name}"
                    folder_path_compile = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Compiled/{file_name}/"
                    folder_path_data = f"{config.PATHS.output_path}/{timestamp}/{config.PATHS.generated_program_output}/Data/{file_name}"
                    file_utils.create_folder(folder_path_compile)
                    file_utils.create_folder(folder_path_data)

                    compiler_summary = compiler_tester.compile_program(
                        path, path_compile, folder_path_data, folder_path_compile
                    )

                responses.append({
                    "code": rendered_template,
                    "filename": file_name,
                    "meta": compiler_summary
                })

        if template.lower() == "random":
            if not template_list:
                return {"error": "No templates available"}

            # Shuffle templates once per request so the order changes each run
            # This avoids always starting with the same template.
            random.shuffle(template_list)

            # Use itertools.cycle to rotate through templates fairly.
            # Every template is guaranteed to be used before any repeats.
            template_cycle = itertools.cycle(template_list)

            for _ in range(number_of_programs):
                tmpl = next(template_cycle)
                tmpl_name = getattr(tmpl, "name", str(tmpl))

                program_generator = ProgramGeneratorFull_GP_Compiler_Test(
                    num_programs=1,  # one program per iteration for fairness
                    language=programming_language,
                    template_type=tmpl_name
                )

                generated_programs, folder_name = program_generator.generate_program()
                process_generated(generated_programs, folder_name)
                distribution[tmpl_name] = distribution.get(tmpl_name, 0) + 1

        else:
            program_generator = ProgramGeneratorFull_GP_Compiler_Test(
                num_programs=number_of_programs,
                language=programming_language,
                template_type=template
            )
            generated_programs, folder_name = program_generator.generate_program()
            process_generated(generated_programs, folder_name)
            distribution[template] = number_of_programs

        return {"seeds": responses, "distribution": distribution}

    except Exception as e:
        print("ERROR in generate_programs_for_gp_compiler_test:", repr(e))
        return {"error": str(e)}


@app.post("/test_single_offspring")
async def test_single_offspring(request: dict = Body(...)):
    
    code = request.get("code", "")
    fname = request.get("filename", f"program_{int(time.time())}.cpp")
    
    # Create temp directory for this program
    temp_dir = os.path.join(EVAL_DIR, f"temp_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)
    
    compiler_test_summary = ""
    
    try:
        # Save source file
        cpp_path = os.path.join(temp_dir, fname)
        with open(cpp_path, "w") as f:
            f.write(code)


    # Source file path
        path = cpp_path

        # Create dedicated folders
        folder_path_compile = os.path.join(temp_dir, "Compiled", fname)
        folder_path_data = os.path.join(temp_dir, "Data", fname)

        file_utils.create_folder(folder_path_compile)
        file_utils.create_folder(folder_path_data)

        # Output executable path (avoid .cpp extension!)
        base_name, _ = os.path.splitext(fname)
        path_compile = os.path.join(folder_path_compile, base_name + "_exec")



        compiler_test_summary=compiler_tester.compile_program(path,path_compile,folder_path_data,folder_path_compile)
        return compiler_test_summary

    except Exception as e:
        # If something goes wrong, return the error string
        return {"error": str(e)}
    
    return None




@app.post("/test_population")
async def test_population(population: list = Body(...)):
    """
    Accept evolved programs as JSON, run compiler testing,
    save them in a batch folder, and return compiler results.
    Each program is handled individually so one failure
    doesn't break the whole batch.
    """
    batch_id = f"batch_{int(time.time())}"
    batch_dir = os.path.join(EVAL_DIR, batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    evaluated = []
    print(f"[INFO] Testing {len(population)} programs, saving in {batch_dir}")

    for prog in population:
        fname = prog.get("filename", f"program_{int(time.time())}.cpp")
        code = prog.get("code", "")
        result = {
            "id": prog.get("id"),
            "filename": fname,
            "code": code,
            "meta": {},
            "error": None
        }

        try:
            # Save source file
            cpp_path = os.path.join(batch_dir, fname)
            with open(cpp_path, "w") as f:
                f.write(code)

            # Create dedicated folders
            folder_path_compile = os.path.join(batch_dir, "Compiled", fname)
            folder_path_data = os.path.join(batch_dir, "Data", fname)
            file_utils.create_folder(folder_path_compile)
            file_utils.create_folder(folder_path_data)

            # Output executable path (avoid .cpp extension!)
            base_name, _ = os.path.splitext(fname)
            path_compile = os.path.join(folder_path_compile, base_name + "_exec")

            # Run compiler tester
            compiler_summary = compiler_tester.compile_program(
                cpp_path, path_compile, folder_path_data, folder_path_compile
            )

            result["meta"] = compiler_summary

        except Exception as e:
            err_msg = f"Program {fname} failed: {e}"
            print(f"[ERROR] {err_msg}")
            result["error"] = str(e)

        evaluated.append(result)

    return {"batch_id": batch_id, "population": evaluated, "saved_in": batch_dir}

    
def start_server():
    """
    Starts the FastAPI server for App A.
    """
    uvicorn.run(app, host=config.COMPILER_TESTER_COMMUNICATION_MANAGER.server_host, port=config.COMPILER_TESTER_COMMUNICATION_MANAGER.server_port,timeout_keep_alive=50000,timeout_graceful_shutdown=50000)

def main():

    start_server()


if __name__ == "__main__":
    main()
    
# python3 -m Compiler_Tester_Communication_Manager.compilation_test_server 
