from fastapi import FastAPI
from src.communication_manager.run_config import RunConfig
import uvicorn, httpx, os, json, time
from src.gp_manager import gp_helpers as gh
from src.gp_manager.common import constant as const
from src.gp_manager.gp_algorithm import evolve

from src.communication_manager import gp_communication_constants


app = FastAPI(title="GP Server Compiler Testing")


def transform_meta(filename: str, meta: dict) -> dict:
    return {
        "filename": filename,
        "success_count": meta.get("success_count", 0),
        "failure_count": meta.get("failure_count", 0),
        "ice_count": meta.get("ice_count", 0),
        "timeout_count": meta.get("timeout_count", 0),
        "differential_mismatches": meta.get("differential_mismatches", 0),
        "compiled": meta.get("compiled", False),
    }


def get_compiler_score(prog: dict) -> float:
    if prog.get("error"):
        return 0.0
    meta = prog.get("meta") or {}

    success_score = meta.get("success_count", 0) * 0.05
    ice_score = meta.get("ice_count", 0) * 2.0
    mismatch_score = meta.get("differential_mismatches", 0) * 3.0
    failure_penalty = meta.get("failure_count", 0) * 0.1
    timeout_penalty = meta.get("timeout_count", 0) * 0.2
    compiled_bonus = 1.0 if meta.get("compiled", False) else 0.0

    return max(0.0, compiled_bonus + success_score + ice_score + mismatch_score - failure_penalty - timeout_penalty)


def collect_final_population(run_dir: str):
    final_dir = os.path.join(run_dir, "final")
    if not os.path.exists(final_dir):
        raise FileNotFoundError(f"No 'final' directory found in {run_dir}")
    population = []
    for i, fname in enumerate(sorted(os.listdir(final_dir))):
        if fname.endswith(".cpp"):
            cpp_path = os.path.join(final_dir, fname)
            with open(cpp_path) as f:
                code = f.read()
            population.append({
                "id": f"prog_{i}",
                "filename": fname,
                "code": code
            })
    return population


def send_population_for_evaluation(run_dir, compiler_server_url=gp_communication_constants.COMPILER_TEST_SERVER_URL):
    population = collect_final_population(run_dir)
    # print("[DEBUG] Population to be sent:")
    # print(json.dumps(population, indent=2)[:1000])
    print(f"[INFO] Sending {len(population)} programs from {run_dir}/final")
    with httpx.Client(timeout=gp_communication_constants.REQUEST_TIMEOUT) as client:
        resp = client.post(f"{compiler_server_url}/test_population", json=population)
        print(f"[INFO] Response status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        print(f"[INFO] Received response keys: {list(data.keys())}")
        return data


@app.post("/run")
async def run_gp(cfg: RunConfig):
    # Step 1: request seeds
    async with httpx.AsyncClient(timeout=gp_communication_constants.REQUEST_TIMEOUT_COMPILER_TEST) as client:
        try:
            resp = await client.get(
                f"{gp_communication_constants.COMPILER_TEST_SERVER_URL}/generate_programs_for_gp_compiler_test",
                params={
                    "number_of_programs": cfg.pop_size,
                    "programming_language": "C++",
                    "template": "random"
                }
            )
            resp.raise_for_status()  # raises HTTPError for non-2xx responses

            payload = resp.json()
            seeds_data = payload.get("seeds")
            if seeds_data is None:
                raise ValueError("Missing 'seeds' in response payload")

        except httpx.ReadTimeout:
            raise RuntimeError("Request to compiler server timed out. Consider increasing timeout or checking server load.")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Compiler server returned error: {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")

    # Step 2: create run-specific folder
    run_id = f"run_{int(time.time())}"
    run_dir = os.path.join(gp_communication_constants.SEED_DIR_COMPILER_TEST, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # Step 3: save seeds locally
    for s in seeds_data:
        fname = s["filename"]
        if not fname.endswith(".cpp"):
            fname = fname.strip() + ".cpp"
        cpp_path = os.path.join(run_dir, fname)
        with open(cpp_path, "w") as f:
            f.write(s["code"])
        meta = s.get("meta", {})
        flat_meta = transform_meta(fname, meta)
        with open(cpp_path + ".json", "w") as jf:
            json.dump(flat_meta, jf, indent=2)

    # Step 4: load seeds into ASTs
    seeds, metas = gh.load_seed_programs_with_meta(run_dir)


    # Step 5: run first evolve to produce children
    best_ast, best_fit, population_dir = evolve(
        seeds,
        metas,
        cfg=cfg,
        pop_size=cfg.pop_size,
        generations=cfg.generations,
        crossover_prob=cfg.crossover_prob,
        mutation_prob=cfg.mutation_prob,
        elitism=cfg.elitism,
        selection_method=const.Selection_Methods.TOURNAMENT_SELECT,
        crossover_method=const.Crossover_Methods.SUBTREE,
        save_runs=True,
        enable_mutation=True,
        outdir=run_dir,
        stagnation_patience=cfg.stagnation_patience,
        compile_check_offspring=False,
        fitness_mode=const.Fitness_Mode.COMPILER
    )
    best_code = gh.parse_ast_to_code(best_ast)

    # Step 6: loop until threshold or max_cycles
    threshold = cfg.target_coverage or 95.0
    current_best = 0.0
    cycle = 0
    best_program = None

    history = {
        "run_id": run_id,
        "seed_count": len(seeds_data),
        "cycles": []
    }

    population_data_dir = population_dir

    while cycle < cfg.max_cycles and current_best < threshold:
    # while cycle < 10:
        cycle += 1
        print(f"[INFO] Cycle {cycle}")

        # Evaluate the evolved children
        compiler_results = send_population_for_evaluation(population_data_dir, gp_communication_constants.COMPILER_TEST_SERVER_URL)

        # Debug print
        # print("[DEBUG] Full compiler_results:")
        # print(json.dumps(Compiler_results, indent=2)[:2000])

        # Update fitness and save metadata JSON
        for prog in compiler_results.get("population", []):
            prog["fitness"] = get_compiler_score(prog)
            fname = prog["filename"]
            cpp_path = os.path.join(population_data_dir, "final", fname)
            meta = prog.get("meta", {})
            flat_meta = transform_meta(fname, meta)
            flat_meta["fitness"] = prog["fitness"]
            with open(cpp_path + ".json", "w") as jf:
                json.dump(flat_meta, jf, indent=2)

        if compiler_results["population"]:
            current_best = max(p["fitness"] for p in compiler_results["population"])
            best_program = max(compiler_results["population"], key=lambda p: p["fitness"])
        else:
            current_best = 0.0
            best_program = None

        # Record cycle
        history["cycles"].append({
            "cycle": cycle,
            "population_size": len(compiler_results["population"]),
            "best_fitness": current_best,
            "fitness_values": [p["fitness"] for p in compiler_results["population"]],
        })

        print(f"[INFO] Cycle {cycle} best fitness: {current_best:.3f}")

        print(f"[DEBUG] Cycle {cycle} check: current_best={current_best:.3f}, threshold={threshold:.3f}")

        if current_best >= threshold:
            print(f"[INFO] Breaking at cycle {cycle} because current_best={current_best:.3f} >= threshold={threshold:.3f}")
            break


        population_cpp_path = os.path.join(population_data_dir, "final")
        # Reload population from disk and evolve again
        population, metas = gh.load_seed_programs_with_meta(population_cpp_path)

        # print("[DEBUG] Population data dir:", population_cpp_path)
        # print("[DEBUG] Loaded population size:", len(population))
        # print("[DEBUG] Loaded metas size:", len(metas))

        # # Inspect the first few entries
        # for i, prog in enumerate(population[:3]):
        #     print(f"[DEBUG] Program {i}: {prog}")   # depending on type, may be AST or dict

        # for i, meta in enumerate(metas[:3]):
        #     print(f"[DEBUG] Meta {i}: {json.dumps(meta, indent=2)}")


        best_ast, best_fit, population_dir = evolve(
            population,
            metas,
            cfg=cfg,
            pop_size=cfg.pop_size,
            generations=cfg.generations,
            crossover_prob=cfg.crossover_prob,
            mutation_prob=cfg.mutation_prob,
            elitism=cfg.elitism,
            selection_method=const.Selection_Methods.TOURNAMENT_SELECT,
            crossover_method=const.Crossover_Methods.SUBTREE,
            save_runs=True,
            enable_mutation=True,
            outdir=run_dir,
            stagnation_patience=cfg.stagnation_patience,
            compile_check_offspring=False,
            fitness_mode=const.Fitness_Mode.COMPILER
        )
        population_data_dir = population_dir

    # Save history
    with open(os.path.join(run_dir, "history.json"), "w") as hf:
        json.dump(history, hf, indent=2)

    return {
        "run_id": run_id,
        "cycles_run": cycle,
        "best_code": best_code,
        "best_fitness": current_best,
        "best_program": best_program,
        "history": history
    }

def start_server():
    uvicorn.run(app, host=gp_communication_constants.SERVER_HOST_COMPILER_TEST, port=gp_communication_constants.SERVER_PORT_COMPILER_TEST)


def main():
    start_server()


if __name__ == "__main__":
    main()


# python3 -m src.communication_manager.gp_server_compiler_testing 

# curl -X POST http://localhost:8008/run   -H "Content-Type: application/json"   -d '{ 
#     "pop_size": 6,
#     "generations": 10,
#     "crossover_prob": 0.6,
#     "mutation_prob": 0.35,
#     "elitism": 1,
#     "target_coverage": 95.0
#   }'