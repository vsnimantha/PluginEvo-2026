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


class CrashMeta(BaseModel):
    crashed: bool = False
    phase: str = ""
    returncode: Optional[int] = None
    stderr: Optional[str] = None
    stdout: Optional[str] = None


# Simple config variables
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8101
REQUEST_TIMEOUT = 12000

EVAL_DIR = "evaluations_plugin_crash_test"

app = FastAPI(title="Plugin Crash Test Server")


class Program(BaseModel):
    filename: Optional[str] = None
    code: str
    meta: Dict = {}


@app.get("/health")
async def check_health():
    return True

def run_with_crash_capture(program_path: str) -> Dict:
    """
    Call executor.complie_program_with_plugin and normalize its outcome
    into a crash metadata dict for the fitness function.
    """
    try:
        res = executor.complie_program_with_plugin(program=program_path)

        # res is a CompletedProcess from subprocess.run on success
        return {
            "crashed": False,
            "phase": "compile",
            "returncode": res.returncode,
            "stdout": res.stdout.decode(errors="ignore") if res.stdout else "",
            "stderr": res.stderr.decode(errors="ignore") if res.stderr else "",
        }
    except CompilationError as ce:
        # This is how plugin-triggered ICEs and other compilation failures surface
        msg = str(ce)
        return {
            "crashed": True,
            "phase": "compile",
            "returncode": 1,   # you can’t see the original code here, so use 1 or None
            "stdout": "",
            "stderr": msg,
        }
    except FileNotFoundError as fe:
        # Missing source or plugin – classify as crash or infra error as you prefer
        return {
            "crashed": True,
            "phase": "infra",
            "returncode": None,
            "stdout": "",
            "stderr": str(fe),
        }
    except Exception as e:
        # Any other unexpected error
        return {
            "crashed": True,
            "phase": "unknown",
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
        }


@app.get("/seeds")
async def get_seeds(
    number_of_programs: int = Query(2, alias="number_of_programs"),
    programming_language: str = Query("C++", alias="programming_language"),
    template: str = Query("random", alias="template"),
):
    try:
        url = config.FEEDBACK_MANAGER.generate_url_gp
        response = program_requester.request_programs(
            url,
            number_of_programs=number_of_programs,
            programming_language=programming_language,
            template=template,
        )

        data = response.json()
        generated_programs, program_folder_path = program_requester.process_response(data)

        print(f"Total of {len(generated_programs)} generated programs saved at {program_folder_path}")
        seeds = []

        if generated_programs and len(generated_programs) >= 1:
            print("Starting the coverage analysis...")
            for program, file_path in generated_programs:
                if config.COVERAGE_ANALYSER.clean_gcov_report_directory:
                    file_management_utils.clean_directory(config.PATHS.main_report_path)

                if config.COVERAGE_ANALYSER.clean_generated_program_directory:
                    file_management_utils.clean_directory(config.PATHS.generated_program_save_path)

                print("Compiling the plugin...")
                executor.compile_plugin_with_coverage_flags()

                # Capture crash info
                run_res = run_with_crash_capture(file_path)

                coverage_summary = {
                    "line_coverage": 0.0,
                    "function_coverage": 0.0,
                    "branch_coverage": 0.0,
                    "decision_coverage": 0.0,
                    "call_coverage": 0.0,
                }

                coverage_text = ""
                if not run_res["crashed"]:
                    coverage_text = executor.generate_coverage(program_folder_path, file_path)
                    coverage_summary = parse_coverage_summary(coverage_text)
                    save_coverage_json(file_path, coverage_summary)

                if config.COVERAGE_ANALYSER.clear_gcov_data:
                    print()
                    print("Cleaning up the plugin directory's gcov data")
                    coverage_generator.clean_up(config.PATHS.plugin_output_path)

                file_name = Path(os.path.basename(file_path)).name
                seeds.append(
                    {
                        "filename": file_name,
                        "folder": program_folder_path,
                        "code": program,
                        "meta": {
                            "coverage": coverage_summary,
                            "crash": run_res,
                        },
                    }
                )

        return {"seeds": seeds, "saved_in": program_folder_path}

    except Exception as e:
        print(f"Error in /seeds: {e}")
        return {"error": str(e)}


@app.post("/analyze")
async def analyze_program(request: dict = Body(...)):
    """
    Analyze a single program for plugin crashes and optionally coverage.

    Expected request:
    {
        "code": "int main() { ... }",
        "filename": "program.cpp"  # optional
    }

    Returns:
    {
        "filename": "program.cpp",
        "coverage": { ... },  # coverage if no crash, else zeros
        "crash": {
            "crashed": bool,
            "phase": str,
            "returncode": int | null,
            "stderr": str | null,
            "stdout": str | null
        },
        "error": null | str
    }
    """
    code = request.get("code", "")
    fname = request.get("filename", f"program_{int(time.time())}.cpp")

    temp_dir = os.path.join(EVAL_DIR, f"temp_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)

    result = {
        "filename": fname,
        "folder": temp_dir,
        "coverage": {},
        "crash": {
            "crashed": False,
            "phase": "",
            "returncode": None,
            "stderr": None,
            "stdout": None,
        },
        "error": None,
    }

    coverage_text = ""

    try:
        cpp_path = os.path.join(temp_dir, fname)
        with open(cpp_path, "w") as f:
            f.write(code)

        executor.compile_plugin_with_coverage_flags()

        run_res = run_with_crash_capture(cpp_path)
        result["crash"].update(run_res)

        if not run_res["crashed"]:
            coverage_text = executor.generate_coverage(temp_dir, cpp_path)
            coverage_summary = parse_coverage_summary(coverage_text)
            result["coverage"] = coverage_summary
            save_coverage_json(cpp_path, coverage_summary)
        else:
            result["coverage"] = {
                "line_coverage": 0.0,
                "function_coverage": 0.0,
                "branch_coverage": 0.0,
                "decision_coverage": 0.0,
                "call_coverage": 0.0,
            }

    except CompilationError as ce:
        print(f"[ERROR] Compilation failed: {ce}")
        result["error"] = str(ce)
        result["coverage"] = {
            "line_coverage": 0.0,
            "function_coverage": 0.0,
            "branch_coverage": 0.0,
            "decision_coverage": 0.0,
            "call_coverage": 0.0,
        }

    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        result["error"] = str(e)
        if not result["coverage"]:
            result["coverage"] = {
                "line_coverage": 0.0,
                "function_coverage": 0.0,
                "branch_coverage": 0.0,
                "decision_coverage": 0.0,
                "call_coverage": 0.0,
            }

    finally:
        if config.COVERAGE_ANALYSER.clear_gcov_data:
            coverage_generator.clean_up(config.PATHS.plugin_output_path)

        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    return result


@app.post("/evaluate_population")
async def evaluate_population(population: list = Body(...)):
    """
    Accept evolved programs as JSON, run crash and coverage analysis,
    save them in a batch folder, and return results.
    Each program is handled individually so one failure
    doesn't break the whole batch.
    """
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
            "meta": {
                "coverage": {},
                "crash": {
                    "crashed": False,
                    "phase": "",
                    "returncode": None,
                    "stderr": None,
                    "stdout": None,
                },
            },
            "error": None,
        }

        coverage_text = ""
        cpp_path = os.path.join(batch_dir, fname)

        try:
            with open(cpp_path, "w") as f:
                f.write(code)

            executor.compile_plugin_with_coverage_flags()

            run_res = run_with_crash_capture(cpp_path)
            result["meta"]["crash"].update(run_res)

            if not run_res["crashed"]:
                coverage_text = executor.generate_coverage(batch_dir, cpp_path)
                coverage_summary = parse_coverage_summary(coverage_text)
                save_coverage_json(cpp_path, coverage_summary)
                result["meta"]["coverage"] = coverage_summary
            else:
                result["meta"]["coverage"] = {
                    "line_coverage": 0.0,
                    "function_coverage": 0.0,
                    "branch_coverage": 0.0,
                    "decision_coverage": 0.0,
                    "call_coverage": 0.0,
                }

        except CompilationError as ce:
            print(f"[ERROR] {ce}")
            result["error"] = str(ce)
            if not result["meta"]["coverage"]:
                result["meta"]["coverage"] = {
                    "line_coverage": 0.0,
                    "function_coverage": 0.0,
                    "branch_coverage": 0.0,
                    "decision_coverage": 0.0,
                    "call_coverage": 0.0,
                }

        except Exception as e:
            err_msg = f"Program {fname} failed: {e}"
            print(f"[ERROR] {err_msg}")
            result["error"] = str(e)
            if not result["meta"]["coverage"]:
                result["meta"]["coverage"] = {
                    "line_coverage": 0.0,
                    "function_coverage": 0.0,
                    "branch_coverage": 0.0,
                    "decision_coverage": 0.0,
                    "call_coverage": 0.0,
                }

        finally:
            if config.COVERAGE_ANALYSER.clear_gcov_data:
                coverage_generator.clean_up(config.PATHS.plugin_output_path)

        evaluated.append(result)

    return {"batch_id": batch_id, "population": evaluated, "saved_in": batch_dir}


def extract_coverage_score(program_folder: str, program_path: str) -> float:
    """
    Extracts line coverage score from gcovr JSON report for a given program.
    """
    try:
        program_name = Path(program_path).name
        report_dir = (
            Path(config.PATHS.main_report_path)
            / program_folder
            / program_name
            / config.PATHS.gcovr_json_report_path
        )
        report_file = report_dir / "coverage.json"

        if not report_file.is_file():
            print(f"Coverage report not found: {report_file}")
            return 0.0

        with open(report_file, "r") as f:
            data = json.load(f)

        return float(data.get("line_coverage", 0.0))

    except Exception as e:
        print(f"Error extracting coverage score for {program_path}: {e}")
        return 0.0


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
    json_path = f"{file_path}_coverage_summary.json"
    with open(json_path, "w") as f:
        json.dump(coverage_data, f, indent=4)
    return str(json_path)


def start_server():
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)


def main():
    start_server()


if __name__ == "__main__":
    main()

# python3 -m Communication_Manager.plugin_test_server