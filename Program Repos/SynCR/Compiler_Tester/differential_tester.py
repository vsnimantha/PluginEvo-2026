import subprocess
import hashlib
import os
import ast
import tempfile

from Compiler_Tester import symbolic_execution

"""
This module performs advanced differential testing on compiled C/C++ binaries by comparing their
runtime behavior and optional LLVM IR output against a trusted baseline—identifying crashes, 
logic divergences, diagnostic inconsistencies, and execution anomalies with rich metadata for each flagged mismatch.
"""

def run_binary(binary_path):
    """
    Executes a binary and returns runtime details.
    """
    try:
        result = subprocess.run([binary_path], capture_output=True, timeout=15, check=True)
        output = result.stdout.decode(errors='ignore')
        stderr = result.stderr.decode(errors='ignore')
        output_hash = hashlib.sha256(output.encode()).hexdigest()
        return {
            "status": "success",
            "output": output,
            "stderr": stderr,
            "hash": output_hash,
            "return_code": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "runtime_error",
            "output": e.stdout.decode(errors='ignore'),
            "stderr": e.stderr.decode(errors='ignore'),
            "hash": None,
            "return_code": e.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": "",
            "stderr": "Execution timed out",
            "hash": None,
            "return_code": None
        }

def generate_ir(source_file, compiler, flags, ir_output_path):
    """
    Generates LLVM IR (.ll) file from source using the given compiler and flags.
    """
    try:
        cmd = [compiler, "-S", "-emit-llvm"] + flags + [source_file, "-o", ir_output_path]
        subprocess.run(cmd, check=True, capture_output=True, timeout=10)
        return True
    except Exception as e:
        print(f"IR generation failed: {ir_output_path} → {e}")
        return False

def get_baseline_binaries(folder_path):
    """
    Finds baseline binaries per compiler from filenames.
    """
    baselines = {}
    for fname in os.listdir(folder_path):
        if "_baseline.o" in fname and fname.endswith(".o"):
            compiler = fname.split("_")[-2]
            baselines[compiler] = os.path.join(folder_path, fname)
    return baselines

def safe_parse_flag_string(flag_str):
    """
    Safely parses a flag list string from filename.
    """
    try:
        return ast.literal_eval(flag_str)
    except:
        return []

def compare_binaries_in_folder(folder_path, source_file=None):
    """
    Compares binaries to their baselines with IR-level diff and diagnostics.
    """
    mismatches = []
    symbolic_diff_text = ""
    ir_diff_text = None

    baselines = get_baseline_binaries(folder_path)
    print(f"Found {len(baselines)} baseline binaries.")
    print("Baselines:", baselines)

    for fname in os.listdir(folder_path):
        if not fname.endswith(".o") or "_baseline.o" in fname:
            print(f"Skipping file: {fname}")
            continue

        parts = fname.split("_")
        compiler = parts[4]
        standard = parts[5]
        raw_flag_str = "_".join(parts[6:-1])
        flags_used = safe_parse_flag_string(raw_flag_str)

        baseline_path = baselines.get(compiler)
        test_path = os.path.join(folder_path, fname)
        print(f"\nTesting {fname} vs baseline: {baseline_path}")

        if not baseline_path or not os.path.exists(test_path):
            print(f"Missing baseline or test binary for {compiler}: {fname}")
            continue

        base_result = run_binary(baseline_path)
        test_result = run_binary(test_path)

        # print(f"Running baseline: {baseline_path}")
        # print(f"Running test: {test_path}")
        # print(f"Base result: {base_result}")
        # print(f"Test result: {test_result}")

        if base_result["hash"] is None or test_result["hash"] is None:
            print(f"Error running binaries for {compiler}: {fname}")
            continue

        # Determine mismatch type
        print("Comparing the binaries.........")
        mismatch_type = None
        if test_result["status"] != "success":
            mismatch_type = "crash"
        elif base_result["hash"] != test_result["hash"]:
            mismatch_type = "logic divergence"
        elif base_result["stderr"] != test_result["stderr"]:
            mismatch_type = "diagnostic drift"
        elif base_result["return_code"] != test_result["return_code"]:
            mismatch_type = "exit code mismatch"
    

        #Debug prints        
        if mismatch_type:
            print(f"Mismatch detected: {mismatch_type}")
        else:
            print("No mismatch detected.")
    


        if mismatch_type == "logic divergence" and source_file:
            with tempfile.TemporaryDirectory() as tmpdir:
                ir_baseline_path = os.path.join(tmpdir, "baseline.ll")
                ir_variant_path = os.path.join(tmpdir, "variant.ll")

                ir_ok_1 = generate_ir(source_file, compiler, ["-O0", "-Wall"], ir_baseline_path)
                ir_ok_2 = generate_ir(source_file, compiler, flags_used, ir_variant_path)

                if ir_ok_1 and ir_ok_2:
                    diff_result = subprocess.run(["diff", ir_baseline_path, ir_variant_path], capture_output=True)
                    if diff_result.returncode in [0,1]:
                        ir_diff_text = diff_result.stdout.decode(errors='ignore')
                    else:
                        ir_diff_text=f"Diff failed: {diff_result.stderr.decode(errors='ignore')}"
                else:
                    ir_diff_text = "IR generation failed or timed out."

        perform_symbolic_compare=False

        if perform_symbolic_compare:
            try:
                symbolic_diff_text = symbolic_execution.symbolic_compare(baseline_path, test_path)
            except Exception as e:
                symbolic_diff_text=f"Symbolic comparison failed: {str(e)}"

        if mismatch_type:
            mismatches.append({
                "compiler": compiler,
                "variant_file": fname,
                "baseline_file": os.path.basename(baseline_path),
                "standard": standard,
                "flags_used": flags_used,
                "mismatch_type": mismatch_type,
                "baseline_output": base_result["output"],
                "variant_output": test_result["output"],
                "baseline_stderr": base_result["stderr"],
                "variant_stderr": test_result["stderr"],
                "baseline_return_code": base_result["return_code"],
                "variant_return_code": test_result["return_code"],
                "ir_diff": ir_diff_text,
                "symbolic_diff": symbolic_diff_text,
            })
            print(f" Mismatch Detected: {mismatch_type} in {fname}")

    return mismatches,symbolic_diff_text
