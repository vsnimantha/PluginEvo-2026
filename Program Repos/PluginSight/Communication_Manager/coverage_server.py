import uvicorn
import os
import re
import json
import time
from pathlib import Path
from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from typing import List, Dict, Optional
from Config.global_config import config
from Communication_Manager import program_requester
from Executor import executor
import Plugin_Manager.coverage_generator as coverage_generator
import Utilities.file_management_utils as file_management_utils

class CompilationError(Exception):
    pass

# Simple config variables
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001
REQUEST_TIMEOUT=12000

EVAL_DIR = "evaluations"

app = FastAPI(title="Coverage Analysis Server")

class Program(BaseModel):
    filename: Optional[str] = None
    code: str
    meta: Dict = {}

@app.get("/health")
async def check_health():
    return True

@app.get("/seeds")
async def get_seeds(number_of_programs: int = Query(2, alias="number_of_programs"),
    programming_language: str = Query("C++", alias="programming_language"),
    template: str = Query("random", alias="template")):
    try:
        url = config.FEEDBACK_MANAGER.generate_url_gp
        response = program_requester.request_programs(url,number_of_programs=number_of_programs,programming_language=programming_language,template=template)

        data = response.json()

        # print(f"[DEBUG] Response from program requester: {response.text}")
        generated_programs, program_folder_path = program_requester.process_response(data)


        print(f"Total of {len(generated_programs)} generated programs saved at {program_folder_path}")
        seeds=[]
        # print("Compiling the plugin...") #Debug print
        # compile_plugin_with_coverage_flags()
        if generated_programs and len(generated_programs)>=1:
            print("Starting the coverage analysis...")
            for program,file_path in generated_programs:
                # print(file_path)

                if config.COVERAGE_ANALYSER.clean_gcov_report_directory:
                    file_management_utils.clean_directory(config.PATHS.main_report_path)

                if config.COVERAGE_ANALYSER.clean_generated_program_directory:
                    file_management_utils.clean_directory(config.PATHS.generated_program_save_path)
                
                print("Compiling the plugin...") #Debug print
                executor.compile_plugin_with_coverage_flags()
                executor.complie_program_with_plugin(program=file_path)
                coverage_text=executor.generate_coverage(program_folder_path,file_path)
                        # Parse metrics
                coverage_summary = parse_coverage_summary(coverage_text)

                # Save JSON file
                save_coverage_json(file_path, coverage_summary)
                
                # #Removing the coverage data from the plugin directory once the process is completed
                if config.COVERAGE_ANALYSER.clear_gcov_data:
                    print()
                    print("Cleaning up the plugin directory's gcov data")
                    coverage_generator.clean_up(config.PATHS.plugin_output_path)
    
                # print(coverage_summary) Debug print

                file_name = Path(os.path.basename(file_path)).name
                seeds.append({"filename": file_name,"folder":program_folder_path, "code": program, "meta": {"coverage": coverage_summary}})

        return {"seeds": seeds, "saved_in": program_folder_path}

    except Exception as e:
        print(f"Error in /seeds: {e}")
        return {"error": str(e)}


# Better to switch of saving Gcov json and other files because it takes a lot of space when running the gp
# generate_gcovr_html_report=False
# generate_gcovr_json_report=False
# generate_gcovr_jacoco_xml_report=False
@app.post("/analyze")
async def analyze_program(request: dict = Body(...)):
    """
    Analyze coverage for a single program.
    
    Expected request:
    {
        "code": "int main() { ... }",
        "filename": "program.cpp"  # optional
    }
    
    Returns:
    {
        "filename": "program.cpp",
        "coverage": {
            "line_coverage": 75.5,
            "function_coverage": 80.0,
            "branch_coverage": 60.0,
            "decision_coverage": 70.0,
            "call_coverage": 85.0
        },
        "error": null
    }
    """
    code = request.get("code", "")
    fname = request.get("filename", f"program_{int(time.time())}.cpp")
    
    # Create temp directory for this program
    temp_dir = os.path.join(EVAL_DIR, f"temp_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)
    
    result = {
        "filename": fname,
        "folder": temp_dir,
        "coverage": {},
        "error": None
    }
    
    coverage_text = ""
    
    try:
        # Save source file
        cpp_path = os.path.join(temp_dir, fname)
        with open(cpp_path, "w") as f:
            f.write(code)
        
        # Compile + run coverage
        executor.compile_plugin_with_coverage_flags()
        executor.complie_program_with_plugin(program=cpp_path)
        coverage_text = executor.generate_coverage(temp_dir, cpp_path)
        
        # Parse coverage
        coverage_summary = parse_coverage_summary(coverage_text)
        result["coverage"] = coverage_summary
        
        # Save coverage JSON
        save_coverage_json(cpp_path, coverage_summary)
        
    except CompilationError as ce:
        print(f"[ERROR] Compilation failed: {ce}")
        result["error"] = str(ce)
        result["coverage"] = {
            "line_coverage": 0.0,
            "function_coverage": 0.0,
            "branch_coverage": 0.0,
            "decision_coverage": 0.0,
            "call_coverage": 0.0
        }
        
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        result["error"] = str(e)
        result["coverage"] = {
            "line_coverage": 0.0,
            "function_coverage": 0.0,
            "branch_coverage": 0.0,
            "decision_coverage": 0.0,
            "call_coverage": 0.0
        }
    
    finally:
        # Cleanup
        if config.COVERAGE_ANALYSER.clear_gcov_data:
            coverage_generator.clean_up(config.PATHS.plugin_output_path)
        
        # Optional: cleanup temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result




@app.post("/evaluate_population")
async def evaluate_population(population: list = Body(...)):
    """
    Accept evolved programs as JSON, run coverage analysis,
    save them in a batch folder, and return coverage results.
    Each program is handled individually so one failure
    doesn't break the whole batch.
    """
    # Step 1: create batch-specific folder
    batch_id = f"batch_{int(time.time())}"
    batch_dir = os.path.join(EVAL_DIR, batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    evaluated = []
    print(f"[INFO] Evaluating {len(population)} programs, saving in {batch_dir}")

    for prog in population:
        fname = prog.get("filename", "unknown.cpp")
        code = prog.get("code", "")
        result = {
            "id": prog.get("id"),
            "filename": fname,
            "folder": batch_dir,
            "code": code,
            "meta": {},
            "error": None
        }

        coverage_text=""
        try:
            # Save source file
            cpp_path = os.path.join(batch_dir, fname)
            with open(cpp_path, "w") as f:
                f.write(code)

            # Compile + run coverage
            executor.compile_plugin_with_coverage_flags()
            executor.complie_program_with_plugin(program=cpp_path)
            coverage_text = executor.generate_coverage(batch_dir, cpp_path)

            coverage_summary = parse_coverage_summary(coverage_text)
            save_coverage_json(cpp_path, coverage_summary)

            if config.COVERAGE_ANALYSER.clear_gcov_data:
                coverage_generator.clean_up(config.PATHS.plugin_output_path)

            result["meta"]["coverage"] = coverage_summary

        except CompilationError as ce:
            print(f"[ERROR] {ce}")
            result["error"] = str(ce)
        except Exception as e:
            # Capture error for this program but continue with others
            err_msg = f"Program {fname} failed: {e}"
            print(f"[ERROR] {err_msg}")
            result["error"] = str(e)
        
        finally:
            coverage_summary = parse_coverage_summary(coverage_text)
            save_coverage_json(cpp_path, coverage_summary)

            if config.COVERAGE_ANALYSER.clear_gcov_data:
                coverage_generator.clean_up(config.PATHS.plugin_output_path)

            result["meta"]["coverage"] = coverage_summary

        evaluated.append(result)

    # Return results and keep batch_dir for history
    return {"batch_id": batch_id, "population": evaluated, "saved_in": batch_dir}


def extract_coverage_score(program_folder: str, program_path: str) -> float:
    """
    Extracts line coverage score from gcovr JSON report for a given program.
    """
    try:
        program_name = Path(program_path).name
        report_dir = Path(config.PATHS.main_report_path) / program_folder / program_name / config.PATHS.gcovr_json_report_path
        report_file = report_dir / "coverage.json"

        if not report_file.is_file():
            print(f"Coverage report not found: {report_file}")
            return 0.0

        with open(report_file, "r") as f:
            data = json.load(f)

        # Adjust this field based on your gcovr config
        return float(data.get("line_coverage", 0.0))

    except Exception as e:
        print(f"Error extracting coverage score for {program_path}: {e}")
        return 0.0
    

# TODO MOVE TO UTILS LATER

def parse_coverage_summary(report_text: str) -> dict:
    """
    Extracts coverage metrics from gcovr text output.
    Returns a dictionary with line, function, branch, decision, and call coverage.
    If a metric is not found, its value will be None.
    """
    metrics = {
        "line_coverage": None,
        "function_coverage": None,
        "branch_coverage": None,
        "decision_coverage": None,
        "call_coverage": None,
    }

    # Match lines like: "lines: 82.8% (24 out of 29)"
    line_match = re.search(r"lines:\s+([\d.]+)%", report_text)
    func_match = re.search(r"functions:\s+([\d.]+)%", report_text)
    branch_match = re.search(r"branches:\s+([\d.]+)%", report_text)
    decision_match = re.search(r"decisions:\s+([\d.]+)%", report_text)
    call_match = re.search(r"calls:\s+([\d.]+)%", report_text)

    if line_match:
        metrics["line_coverage"] = float(line_match.group(1))
    if func_match:
        metrics["function_coverage"] = float(func_match.group(1))
    if branch_match:
        metrics["branch_coverage"] = float(branch_match.group(1))
    if decision_match:
        metrics["decision_coverage"] = float(decision_match.group(1))
    if call_match:
        metrics["call_coverage"] = float(call_match.group(1))

    return metrics


def save_coverage_json(file_path: str, coverage_data: dict):
    """
    Save coverage metrics to a JSON file named after the program.
    """
    json_path =  f"{file_path}_coverage_summary.json"
    with open(json_path, "w") as f:
        json.dump(coverage_data, f, indent=4)
    return str(json_path)




def start_server():
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

def main():
    start_server()

if __name__ == "__main__":
    main()

# Run with:
# python3 -m Communication_Manager.coverage_server
