from fastapi import FastAPI
from src.communication_manager.run_config import RunConfig
import uvicorn, httpx, os, json, time
from src.gp_manager import gp_helpers as gh
from src.gp_manager.common import constant as const
from src.gp_manager.gp_algorithm import evolve

from src.communication_manager import gp_communication_constants

 
app = FastAPI(title="GP Plugin Crash Testing Server")


def transform_meta(filename: str, foldername: str, meta: dict) -> dict:
    """
    Flatten crash-related meta for storage alongside the .cpp file.
    """
    crash = (meta or {}).get("crash", {}) if isinstance(meta, dict) else {}
    return {
        "filename": filename,
        "foldername": foldername,
        "crashed": bool(crash.get("crashed", False)),
        "phase": crash.get("phase"),
        "returncode": crash.get("returncode"),
        "stderr": crash.get("stderr"),
        "stdout": crash.get("stdout"),
    }


def get_bug_score(prog: dict) -> float:
    """
    Fitness proxy for bug-finding:

      - 0.0 if no crash or program error.
      - 1.0 if crashed.
      - +0.5 if stderr looks like an ICE.
      - +0.5 if stderr looks plugin-related.

    Tune the heuristics for your plugin messages.
    """
    if prog.get("error"):
        return 0.0

    meta = prog.get("meta") or {}
    crash = meta.get("crash", {}) if isinstance(meta, dict) else {}
    crashed = bool(crash.get("crashed", False))
    if not crashed:
        return 0.0

    stderr = (crash.get("stderr") or "").lower()

    is_ice = any(
        token in stderr
        for token in [
            "internal compiler error",
            "please submit a full bug report",
            "ice:",
        ]
    )
    is_plugin_related = any(
        token in stderr
        for token in [
            "cprintf",        # adjust to your plugin identifier(s)
            "gcc plugin",
            "plugin error",
        ]
    )

    score = 1.0
    if is_ice:
        score += 0.5
    if is_plugin_related:
        score += 0.5

    return score


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


def send_population_for_evaluation(
    run_dir: str,
    crash_server_url: str = gp_communication_constants.PLUGIN_CRASH_TEST_SERVER_URL,
):
    population = collect_final_population(run_dir)
    print("[DEBUG] Population to be sent:")
    print(json.dumps(population, indent=2)[:1000])
    print(f"[INFO] Sending {len(population)} programs from {run_dir}/final")
    with httpx.Client(timeout=gp_communication_constants.REQUEST_TIMEOUT) as client:
        resp = client.post(f"{crash_server_url}/evaluate_population", json=population)
        print(f"[INFO] Response status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        print(f"[INFO] Received response keys: {list(data.keys())}")
        return data


@app.post("/run")
async def run_gp(cfg: RunConfig):
    # Step 1: request seeds from crash server
    async with httpx.AsyncClient(timeout=gp_communication_constants.REQUEST_TIMEOUT_PLUGIN_CRASH_TEST) as client:
        try:
            resp = await client.get(
                f"{gp_communication_constants.PLUGIN_CRASH_TEST_SERVER_URL}/seeds",
                params={
                    "number_of_programs": cfg.pop_size,
                    "programming_language": "C++",
                    "template": "random",
                },
            )
            resp.raise_for_status()

            payload = resp.json()
            seeds_data = payload.get("seeds")
            if seeds_data is None:
                raise ValueError("Missing 'seeds' in response payload")

        except httpx.ReadTimeout:
            raise RuntimeError(
                "Request to crash server timed out. "
                "Consider increasing timeout or checking server load."
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Crash server returned error: {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")

    # Step 2: create run-specific folder
    run_id = f"run_{int(time.time())}"
    run_dir = os.path.join(gp_communication_constants.SEED_DIR_PLUGIN_CRASH, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # Step 3: save seeds locally
    for s in seeds_data:
        fname = s["filename"]
        folder = s["folder"]
        if not fname.endswith(".cpp"):
            fname = fname.strip() + ".cpp"
        cpp_path = os.path.join(run_dir, fname)
        with open(cpp_path, "w") as f:
            f.write(s["code"])
        meta = s.get("meta", {})
        flat_meta = transform_meta(fname, folder, meta)
        with open(cpp_path + ".json", "w") as jf:
            json.dump(flat_meta, jf, indent=2)

    # Step 4: load seeds into ASTs
    seeds, metas = gh.load_seed_programs_with_meta(run_dir)

    # Step 5: initial evolve
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
        compile_check_offspring=True,
        fitness_mode=const.Fitness_Mode.PLUGIN,
    )
    best_code = gh.parse_ast_to_code(best_ast)

    # For crash search, treat cfg.target_coverage as a bug score threshold, or set a default.
    bug_threshold = cfg.target_coverage or 1.0
    current_best = 0.0
    cycle = 0
    best_program = None

    history = {
        "run_id": run_id,
        "seed_count": len(seeds_data),
        "cycles": [],
    }

    population_data_dir = population_dir

    while cycle < cfg.max_cycles and current_best < bug_threshold:
        cycle += 1
        print(f"[INFO] Cycle {cycle}")

        # Evaluate the evolved children for crashes
        eval_results = send_population_for_evaluation(
            population_data_dir,
            gp_communication_constants.PLUGIN_CRASH_TEST_SERVER_URL,
        )

        # Update fitness and save metadata JSON
        for prog in eval_results.get("population", []):
            prog["fitness"] = get_bug_score(prog)
            fname = prog["filename"]
            foldername = prog["folder"]
            cpp_path = os.path.join(population_data_dir, "final", fname)
            meta = prog.get("meta", {})
            flat_meta = transform_meta(fname, foldername, meta)
            flat_meta["fitness"] = prog["fitness"]
            with open(cpp_path + ".json", "w") as jf:
                json.dump(flat_meta, jf, indent=2)

        if eval_results["population"]:
            current_best = max(p["fitness"] for p in eval_results["population"])
            best_program = max(eval_results["population"], key=lambda p: p["fitness"])
        else:
            current_best = 0.0
            best_program = None

        # Record cycle
        history["cycles"].append({
            "cycle": cycle,
            "population_size": len(eval_results["population"]),
            "best_bug_score": current_best,
            "bug_scores": [p["fitness"] for p in eval_results["population"]],
        })

        print(f"[INFO] Cycle {cycle} best bug score: {current_best:.3f}")
        print(f"[DEBUG] Cycle {cycle} check: current_best={current_best:.3f}, threshold={bug_threshold:.3f}")

        if current_best >= bug_threshold:
            print(
                f"[INFO] Breaking at cycle {cycle} because "
                f"current_best={current_best:.3f} >= threshold={bug_threshold:.3f}"
            )
            break

        population_cpp_path = os.path.join(population_data_dir, "final")
        population, metas = gh.load_seed_programs_with_meta(population_cpp_path)

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
            compile_check_offspring=True,
            fitness_mode=const.Fitness_Mode.PLUGIN,
        )
        population_data_dir = population_dir

    # Save history
    with open(os.path.join(run_dir, "history.json"), "w") as hf:
        json.dump(history, hf, indent=2)

    return {
        "run_id": run_id,
        "cycles_run": cycle,
        "best_code": best_code,
        "best_bug_score": current_best,
        "best_program": best_program,
        "history": history,
    }


def start_server():
    uvicorn.run(
        app,
        host=gp_communication_constants.SERVER_HOST_PLUGIN_CRASH_TEST,
        port=gp_communication_constants.SERVER_PORT_PLUGIN_CRASH_TEST,
    )


def main():
    start_server()


if __name__ == "__main__":
    main()
    
# python3 -m src.communication_manager.gp_server_plugin_test