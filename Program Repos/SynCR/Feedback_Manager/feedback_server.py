from fastapi import FastAPI,Query
from fastapi.responses import JSONResponse
import uvicorn,itertools,random
from Program_Generator.program_generator_tmpl_coverage import ProgramGeneratorFull_Coverage
from Program_Generator.program_generator_tmpl import ProgramGeneratorFull
from Config.global_config import config
from Template_Manager.template_manager_impl import TemplateManagerImpl

app = FastAPI()

def analyze_coverage_report(report):
    """
    Analyzes the coverage report and decides how to improve the code.
    """
    if report and "coverage" in report:
        coverage = report["coverage"]
        print(f"Coverage Report: {coverage}%")
        if coverage < 90:  # Example threshold
            print("Coverage is low. Improving code...")
        else:
            print("Coverage is sufficient.")
    else:
        print("Invalid coverage report received.")

@app.post("/report")
async def receive_report(report: dict):
    """
    API endpoint to receive the coverage report from App B.
    """
    print("Received coverage report from App B.")
    analyze_coverage_report(report)
    return {"status": "Report received"}

@app.get("/generate_programs")
async def generate_programs():
    program_generator = ProgramGeneratorFull()
    generated_programs=program_generator.generate_program()
    
    responses = []

    if len(generated_programs)>1:

        if isinstance(generated_programs[0], list) and len(generated_programs) > 0:
            for program in generated_programs[0]:
                response=JSONResponse(content=program)
                response.headers.append("folder_name",generated_programs[1])
                responses.append(response)
        elif isinstance(generated_programs[0], str):
                response=JSONResponse(content=generated_programs[0])
                response.headers.append("folder_name",generated_programs[1])
                responses.append(response)
        else:
            print("Handling other type")
    else:
        if isinstance(generated_programs, list) and len(generated_programs) > 0:
            for program in generated_programs:
                response=JSONResponse(content=program)
                responses.append(response)
        elif isinstance(generated_programs, str):
                response=JSONResponse(content=program[0])
                responses.append(response)
        else:
            print("Handling other type")
    return responses

# @app.get("/generate_programs_for_gp")
# async def generate_programs_for_gp(
#     number_of_programs: int = Query(2, alias="number_of_programs"),
#     programming_language: str = Query("C++", alias="programming_language"),
#     template: str = Query("random", alias="template")
# ):
#     try:
#         template_manager = TemplateManagerImpl(config.PATHS.template_path)
#         template_list = template_manager.templates

#         responses: list[dict] = []
#         distribution: dict[str, int] = {}

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
#                 program_generator = ProgramGeneratorFull_Coverage(
#                     num_programs=count_for_this_template,
#                     language=programming_language,
#                     template_type=tmpl_name
#                 )

#                 generated_programs, folder_name = program_generator.generate_program()

#                 for program in generated_programs:
#                     if isinstance(program, (list, tuple)) and len(program) == 2:
#                         code, filename = program
#                     else:
#                         code, filename = program, "generated.cpp"

#                     responses.append({
#                         "code": code,
#                         "filename": filename,
#                         "folder_name": folder_name,
#                         "template_used": tmpl_name
#                     })

#                 distribution[tmpl_name] = distribution.get(tmpl_name, 0) + count_for_this_template

#         else:
#             program_generator = ProgramGeneratorFull_Coverage(
#                 num_programs=number_of_programs,
#                 language=programming_language,
#                 template_type=template
#             )
#             generated_programs, folder_name = program_generator.generate_program()

#             for program in generated_programs:
#                 if isinstance(program, (list, tuple)) and len(program) == 2:
#                     code, filename = program
#                 else:
#                     code, filename = program, "generated.cpp"

#                 responses.append({
#                     "code": code,
#                     "filename": filename,
#                     "folder_name": folder_name,
#                     "template_used": template
#                 })

#             distribution[template] = number_of_programs

#         return {"programs": responses, "distribution": distribution}

#     except Exception as e:
#         return {"error": str(e)}

@app.get("/generate_programs_for_gp")
async def generate_programs_for_gp(
    number_of_programs: int = Query(2, alias="number_of_programs"),
    programming_language: str = Query("C++", alias="programming_language"),
    template: str = Query("random", alias="template")
):
    try:
        template_manager = TemplateManagerImpl(config.PATHS.template_path)
        template_list = template_manager.templates

        responses: list[dict] = []
        distribution: dict[str, int] = {}

        if template.lower() == "random":
            if not template_list:
                return {"error": "No templates available"}

            # Shuffle templates once per request so the order changes each run.
            # This avoids always starting with the same template.
            random.shuffle(template_list)

            # Use itertools.cycle to rotate through templates fairly.
            # Every template is guaranteed to be used before any repeats.
            template_cycle = itertools.cycle(template_list)

            for _ in range(number_of_programs):
                tmpl = next(template_cycle)
                tmpl_name = getattr(tmpl, "name", str(tmpl))

                program_generator = ProgramGeneratorFull_Coverage(
                    num_programs=1,  # one program per iteration for fairness
                    language=programming_language,
                    template_type=tmpl_name
                )

                generated_programs, folder_name = program_generator.generate_program()

                for program in generated_programs:
                    if isinstance(program, (list, tuple)) and len(program) == 2:
                        code, filename = program
                    else:
                        code, filename = program, "generated.cpp"

                    responses.append({
                        "code": code,
                        "filename": filename,
                        "folder_name": folder_name,
                        "template_used": tmpl_name
                    })

                distribution[tmpl_name] = distribution.get(tmpl_name, 0) + 1

        else:
            program_generator = ProgramGeneratorFull_Coverage(
                num_programs=number_of_programs,
                language=programming_language,
                template_type=template
            )
            generated_programs, folder_name = program_generator.generate_program()

            for program in generated_programs:
                if isinstance(program, (list, tuple)) and len(program) == 2:
                    code, filename = program
                else:
                    code, filename = program, "generated.cpp"

                responses.append({
                    "code": code,
                    "filename": filename,
                    "folder_name": folder_name,
                    "template_used": template
                })

            distribution[template] = number_of_programs

        return {"programs": responses, "distribution": distribution}

    except Exception as e:
        return {"error": str(e)}


    
def start_server():
    """
    Starts the FastAPI server for App A.
    """
    uvicorn.run(app, host=config.FEEDBACK_MANAGER.server_host, port=config.FEEDBACK_MANAGER.server_port)
    # uvicorn.run(app, host="0.0.0.0", port=5002)

def main():
    """
    Main loop for App A.
    """
    # Start the server in a separate thread
    # server_thread = threading.Thread(target=start_server)
    # server_thread.daemon = True
    # server_thread.start()

    start_server()


if __name__ == "__main__":
    main()
    
# python3 -m Feedback_Manager.feedback_server 

# http://localhost:5002/generate_programs