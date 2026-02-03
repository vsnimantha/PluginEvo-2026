import os, copy, random, datetime,hashlib,json
from src.gp_manager.common import constant as const
from src.gp_manager.common import utils
from src.gp_manager import gp_helpers as gh
from src.common import static_analyser,compile_checker
from src.ast_manager.ast_to_code.ast_to_code_parser import emit_translation_unit


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def prog_hash(ast):
    """
    Compute a stable hash of an AST to identify unique programs.

    This version uses SHA-256 on the emitted source code string to ensure
    deterministic results across runs. It helps detect duplicate individuals
    and verify that crossover/mutation produces novel offspring.

    Parameters
    ----------
    ast : AST
        Abstract syntax tree to hash.

    Returns
    -------
    str
        Hex digest of the program's source code representation.
    """
    # Prefer full source emission if available
    if hasattr(ast, "to_source") and callable(ast.to_source):
        code = ast.to_source()
    else:
        try:
            # If you have an emitter for compilable code, use it here
            code = emit_translation_unit(ast)
        except Exception:
            code = repr(ast)

    # Normalize whitespace to avoid cosmetic differences
    normalized = "\n".join(line.strip() for line in code.splitlines())

    # Compute stable SHA-256 digest
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()



def has_valid_main(ast):
    """
    Check if an AST contains a valid main function with a compound statement body.
    
    Ensures syntactic validity of evolved programs. A valid main must:
    - Be a FUNCTION_DECL with spelling "main"
    - Contain at least one COMPOUND_STMT child (function body)
    
    Parameters
    ----------
    ast : AST
        Abstract syntax tree to validate.
    
    Returns
    -------
    bool
        True if ast has valid main function, False otherwise.
    """
    for f in ast.children:
        if f.kind == "FUNCTION_DECL" and f.spelling == "main":
            return any(c.kind == "COMPOUND_STMT" for c in f.children)
    return False


# ============================================================================
# POPULATION INITIALIZATION
# ============================================================================


def initialize_population(seeds, metas, pop_size):
    """
    Initialize the population from seed programs and fill to target size.
    
    Starts with provided seeds and their metadata, then randomly duplicates seeds
    (with None metadata) to reach pop_size. Ensures diversity is initialized from
    seed programs while maintaining population size constraint.
    
    Parameters
    ----------
    seeds : list
        Seed AST programs to initialize population.
    metas : list
        Metadata corresponding to each seed (can contain None values).
    pop_size : int
        Target population size. If less than seeds, only first pop_size are used.
        If more, seeds are randomly duplicated to fill.
    
    Returns
    -------
    list of tuple
        Population as list of (ast, meta) pairs, length pop_size.
    """
    population = [(utils.safe_copy(s), utils.safe_copy(m)) for s, m in zip(seeds, metas)]
    while len(population) < pop_size and len(seeds) > 0:
        population.append((utils.safe_copy(random.choice(seeds)), None))
    return population


def get_best_individual(fitnesses):
    """
    Find index and value of best-fitness individual.
    
    Parameters
    ----------
    fitnesses : list of float
        Fitness values for population.
    
    Returns
    -------
    tuple
        (best_idx, best_fitness) - index of best individual and its fitness value.
    """
    best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
    return best_idx, fitnesses[best_idx]


# ============================================================================
# SELECTION & MATING POOL
# ============================================================================


def build_mating_pool(pop_asts, fitnesses, pop_size, elitism, 
                     max_reuse, selection_method, tournament_k, case_results):
    """
    Build mating pool for breeding with diversity protection.
    
    Selects parents using tournament or other selection method, respecting
    max_reuse constraint to prevent population convergence. If selection fails
    to fill mating pool within max_attempts, randomly fills remaining slots.
    
    Parameters
    ----------
    pop_asts : list
        List of AST programs (population without metadata).
    fitnesses : list of float
        Fitness value for each program.
    pop_size : int
        Target population size (for calculating pool size).
    elitism : int
        Number of elites (used to determine pool size).
    max_reuse : int
        Maximum times same individual can appear in mating pool.
    selection_method : const.Selection_Methods
        Selection strategy (e.g., TOURNAMENT_SELECT).
    tournament_k : int
        Tournament size if using tournament selection.
    case_results : dict or None
        Optional cached fitness results for selection optimization.
    
    Returns
    -------
    list
        Mating pool of selected AST programs, shuffled and ready for pairing.
    """
    mating_pool = []
    reuse_counts = {}
    attempts = 0
    max_attempts = 20 * pop_size
    target_pool_size = 2 * (pop_size - elitism)
    
    # Select parents with reuse cap
    while len(mating_pool) < target_pool_size and attempts < max_attempts:
        parent = gh.select_individual(
            pop_asts, fitnesses,
            method=selection_method,
            tournament_k=tournament_k,
            case_results=case_results
        )
        h = prog_hash(parent)
        if reuse_counts.get(h, 0) < max_reuse:
            mating_pool.append(parent)
            reuse_counts[h] = reuse_counts.get(h, 0) + 1
        attempts += 1
    
    # Fallback: fill remaining slots with random selection
    while len(mating_pool) < target_pool_size:
        mating_pool.append(random.choice(pop_asts))
    
    # Shuffle to avoid systematic bias in parent pairing
    random.shuffle(mating_pool)
    
    return mating_pool


# ============================================================================
# GENETIC OPERATORS: CROSSOVER & MUTATION
# ============================================================================


def apply_crossover(p1_ast, p2_ast, crossover_prob, crossover_method, strict=False):
    """
    Apply crossover to two parents. If crossover fails to produce novelty
    after 5 attempts, return copies of parents.

    Parameters
    ----------
    p1_ast : AST
        First parent program.
    p2_ast : AST
        Second parent program.
    crossover_prob : float
        Probability (0.0-1.0) that crossover occurs.
    crossover_method : const.Crossover_Methods
        Crossover strategy (e.g., SUBTREE).
    strict : bool
        If True, require both children to differ from both parents.
        If False, accept if at least one child differs.
    """
    if random.random() < crossover_prob:
        attempts = 0
        while attempts < 5:
            c1, c2 = gh.crossover_ast(p1_ast, p2_ast, crossover_method)

            # Debug: show hashes
            print("[DEBUG] Parent1 hash:", prog_hash(p1_ast))
            print("[DEBUG] Parent2 hash:", prog_hash(p2_ast))
            print("[DEBUG] Child1 hash:", prog_hash(c1))
            print("[DEBUG] Child2 hash:", prog_hash(c2))
            if strict:
                # Strict mode: both children must differ from both parents
                if (prog_hash(c1) not in (prog_hash(p1_ast), prog_hash(p2_ast)) and
                    prog_hash(c2) not in (prog_hash(p1_ast), prog_hash(p2_ast))):
                    print("[DEBUG] Strict novelty condition satisfied.")
                    return c1, c2
            else:
                # Loose mode: accept if at least one child differs
                if (prog_hash(c1) != prog_hash(p1_ast) or
                    prog_hash(c2) != prog_hash(p2_ast)):
                    print("[DEBUG] Loose novelty condition satisfied.")
                    return c1, c2

            attempts += 1

        print("[DEBUG] Crossover failed to produce novelty after 5 attempts. Falling back to cloning parents.")
        return utils.safe_copy(p1_ast), utils.safe_copy(p2_ast)
    else:
        print("[DEBUG] Crossover skipped due to probability check. Cloning parents.")
        return utils.safe_copy(p1_ast), utils.safe_copy(p2_ast)




def apply_mutation(offspring, mutation_prob, include_decl_mut_prob):
    """
    Apply independent point mutation to an offspring.
    
    With probability mutation_prob, randomly modifies the offspring's AST.
    Only operates if enable_mutation is True.
    
    Parameters
    ----------
    offspring : AST
        Offspring program to potentially mutate.
    mutation_prob : float
        Probability (0.0-1.0) of applying mutation.
    enable_mutation : bool
        Master switch for mutation; if False, returns offspring unchanged.
    include_decl_mut_prob : float
        Probability of mutating declarations.
    
    Returns
    -------
    AST
        Mutated (or unchanged) offspring.
    """
    r = random.random()
    print(f"Random draw: {r}, threshold: {mutation_prob}")
    if r < mutation_prob:
        offspring = gh.mutate_ast(offspring, include_decl_prob=include_decl_mut_prob)

    return offspring


# ============================================================================
# OFFSPRING PRODUCTION
# ============================================================================


def produce_offspring(mating_pool, pop_size, elitism, crossover_prob, mutation_prob,
                     enable_mutation, include_decl_mut_prob, crossover_method,compile_check=True,repair_off_spring=True):
    """
    Generate offspring from mating pool via crossover, mutation, and validation.
    
    Pairs individuals from mating pool, applies genetic operators (crossover and
    mutation), validates offspring, and builds next population. Repeats until
    population reaches target size.
    
    Parameters
    ----------
    mating_pool : list
        Shuffled list of selected parents.
    pop_size : int
        Target population size.
    elitism : int
        Number of individuals already reserved for elites (for counting available slots).
    crossover_prob : float
        Probability of crossover for each pair.
    mutation_prob : float
        Probability of mutation for each offspring.
    enable_mutation : bool
        Whether to enable mutation operator.
    include_decl_mut_prob : float
        Probability of mutating declarations.
    crossover_method : const.Crossover_Methods
        Crossover strategy.
    
    Returns
    -------
    list of tuple
        Offspring as list of (ast, None) pairs.
    """
    offspring_pop = []
    
    for i in range(0, len(mating_pool), 2):
        if len(offspring_pop) >= pop_size - elitism:
            break
        
        p1_ast, p2_ast = mating_pool[i], mating_pool[i + 1]
        
        # Apply genetic operators
        c1, c2 = apply_crossover(p1_ast, p2_ast, crossover_prob, crossover_method)
        
        # Validate offspring structure
        if not (has_valid_main(c1) and has_valid_main(c2)):
            c1, c2 = utils.safe_copy(p1_ast), utils.safe_copy(p2_ast)
        
        # Apply independent mutation
        if enable_mutation:
            c1 = apply_mutation(c1, mutation_prob, include_decl_mut_prob)
            c2 = apply_mutation(c2, mutation_prob, include_decl_mut_prob)

        if compile_check:
            # === Compiler validation step ===
            code1 = emit_translation_unit(c1)
            code2 = emit_translation_unit(c2)

            ok1, msg1 = compile_checker.check_compile_from_string(code1)
            ok2, msg2 = compile_checker.check_compile_from_string(code2)

            if repair_off_spring:
                if not ok1:
                    print(f"[DEBUG] Offspring 1 failed compilation: {msg1}")
                    c1 = repair_offspring(c1, p1_ast, p2_ast, crossover_method, crossover_prob)
                    # Final fallback if still invalid
                    code1 = emit_translation_unit(c1)
                    ok1, _ = compile_checker.check_compile_from_string(code1)
                    if not ok1:
                        print("[DEBUG] Repair failed, cloning parent1.")
                        c1 = utils.safe_copy(p1_ast)

                if not ok2:
                    print(f"[DEBUG] Offspring 2 failed compilation: {msg2}")
                    c2 = repair_offspring(c2, p1_ast, p2_ast, crossover_method, crossover_prob)
                    # Final fallback if still invalid
                    code2 = emit_translation_unit(c2)
                    ok2, _ = compile_checker.check_compile_from_string(code2)
                    if not ok2:
                        print("[DEBUG] Repair failed, cloning parent2.")
                        c2 = utils.safe_copy(p2_ast)


        
        # Add offspring to population
        offspring_pop.append((c1, None))
        if len(offspring_pop) < pop_size - elitism:
            offspring_pop.append((c2, None))
    
    return offspring_pop


def repair_offspring(ast, parent1_ast, parent2_ast,
                     crossover_method, crossover_prob=1.0,max_retries=3):
    """
    Attempt to repair an invalid offspring by retrying crossover.
    
    Parameters
    ----------
    ast : object
        The invalid offspring AST.
    parent1_ast : object
        First parent AST.
    parent2_ast : object
        Second parent AST.
    crossover_method : const.Crossover_Methods
        Crossover strategy to use for retries.
    crossover_prob : float
        Probability of crossover (forced to 1.0 for repair).
    enable_mutation : bool
        Whether mutation is allowed as fallback (default False here).
    include_decl_mut_prob : float
        Probability of mutating declarations (not used in repair).
    max_retries : int
        How many times to retry crossover before fallback.
    
    Returns
    -------
    object
        A repaired AST that passes syntax/compilation checks.
    """
    for attempt in range(max_retries):
        c1, c2 = apply_crossover(utils.safe_copy(parent1_ast),
                                 utils.safe_copy(parent2_ast),
                                 crossover_prob,
                                 crossover_method)
        # Validate candidates
        for candidate in (c1, c2):
            code = emit_translation_unit(candidate)
            ok, _ = compile_checker.check_compile_from_string(code)
            if ok:
                print(f"[DEBUG] Repair succeeded after {attempt+1} crossover attempt(s).")
                return candidate
    
    # Fallback: clone one of the parents if all retries fail
    print("[DEBUG] Repair failed, cloning parent.")
    return utils.safe_copy(parent1_ast)



# ============================================================================
# LOGGING & SAVING
# ============================================================================

def record_generation_info(run_dir, generation, best_fit):
    """
    Append generation info to a JSON file in run_dir.
    Each entry contains generation index and best fitness.
    """
    json_path = os.path.join(run_dir, "generation_log.json")

    # Load existing data if file exists
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new record
    data.append({
        "generation": generation,
        "best_fitness": round(best_fit, 3)
    })

    # Save back to file
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)


def log_event(event_type, message, run_dir, print_log=True):
    """
    Append an event message to a run log file.
    """
    if print_log:
        print(message)

    if run_dir is None:
        return

    log_file = os.path.join(run_dir, "events.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [{event_type}] {message}\n")


def save_generation_if_needed(save_runs, run_dir, population, fitnesses, generation):
    """
    Save population and fitness data for current generation if enabled.
    
    Parameters
    ----------
    save_runs : bool
        Whether saving is enabled.
    run_dir : str or None
        Directory to save to (None if saving disabled).
    population : list of tuple
        Current population.
    fitnesses : list of float
        Fitness values.
    generation : int or str
        Generation number (can be "final" for final generation).
    """
    if save_runs and run_dir:
        gh.save_generation(population, fitnesses, generation, outdir=run_dir)


def setup_run_directory(save_runs, outdir):
    """
    Create timestamped run directory if saving is enabled.
    
    Parameters
    ----------
    save_runs : bool
        Whether saving is enabled.
    outdir : str
        Parent output directory.
    
    Returns
    -------
    str or None
        Path to created run directory, or None if saving disabled.
    """
    if save_runs:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(outdir, f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        return run_dir
    return None


# ============================================================================
# MAIN EVOLUTIONARY LOOP
# ============================================================================

def evolve(seeds, metas, cfg,
           pop_size=50, generations=50,
           crossover_prob=0.8, mutation_prob=0.01, elitism=1,
           selection_method=const.Selection_Methods.TOURNAMENT_SELECT,
           crossover_method=const.Crossover_Methods.SUBTREE,
           tournament_k=3,
           case_results=None,
           include_decl_mut_prob=0.0,
           enable_mutation=False,
           max_reuse=2,
           save_runs=False,
           outdir=const.GP_RUNS_DIR,
           target_fitness=0.95,
           rng_seed=None,
           stagnation_patience=100,
           compile_check_offspring=True,
           fitness_mode=const.Fitness_Mode.PLUGIN):
    """
    Genetic Programming Evolutionary Loop (Main Entry Point)
    
    Evolves a population of AST-based programs through selection, crossover, and mutation
    over multiple generations to optimize fitness. Uses tournament selection, subtree 
    crossover, and point mutation to explore the program space.
    
    Parameters
    ----------
    seeds : list
        Initial population of AST programs to seed the evolutionary run.
        Used as basis for population initialization and diversity maintenance.
    
    metas : list
        Metadata associated with each seed program (e.g., constraints, annotations).
        Parallel to seeds; can contain None for programs without metadata.
    
    cfg : object
        Configuration object containing problem-specific settings and hyperparameters.
        May contain a 'seed' attribute for deterministic randomization.
    
    pop_size : int, default=50
        Population size for each generation. Recommended: 50-100 for typical problems.
    
    generations : int, default=50
        Number of evolutionary generations to run. Recommended: 50-200.
    
    crossover_prob : float, default=0.8
        Probability (0.0-1.0) that two parent programs undergo genetic recombination.
        Recommended: 0.8-0.9 for effective genetic exchange.
    
    mutation_prob : float, default=0.01
        Probability (0.0-1.0) that an offspring undergoes random structural modification.
        Recommended: 0.01-0.1 to balance exploration and exploitation.
    
    elitism : int, default=1
        Number of best-fitness individuals automatically copied to next generation.
        Typical values: 1-5.
    
    selection_method : const.Selection_Methods, default=TOURNAMENT_SELECT
        Method for selecting parents (e.g., TOURNAMENT_SELECT, ROULETTE_WHEEL, RANK_SELECT).
    
    crossover_method : const.Crossover_Methods, default=SUBTREE
        Genetic recombination strategy (e.g., SUBTREE, ONE_POINT, UNIFORM).
    
    tournament_k : int, default=3
        Number of individuals sampled for tournament selection.
        Typical: 3-7. Higher k increases selection pressure.
    
    case_results : dict or None, default=None
        Optional cached fitness test results for optimization.
    
    include_decl_mut_prob : float, default=0.0
        Probability (0.0-1.0) that mutation affects variable declarations.
        Typical: 0.0-0.2 to maintain syntactic validity.
    
    enable_mutation : bool, default=False
        Master switch to enable/disable mutation operators.
        Should typically be True for effective GP.
    
    max_reuse : int, default=2
        Maximum times the same unique program can appear in mating pool.
        Helps maintain genetic diversity. Typical: 2-3.
    
    save_runs : bool, default=False
        If True, saves populations and fitnesses for every generation to disk.
    
    outdir : str, default=const.GP_RUNS_DIR
        Output directory where run results are saved (if save_runs=True).
    
    target_fitness : float or None, default=None
        Optional target fitness for early stopping.
    
    rng_seed : int or None, default=None
        Random number generator seed for reproducibility.
        If None, attempts to use cfg.seed if available.
    
    stagnation_patience : int, default=10
        Number of consecutive generations allowed without improvement in best fitness
        or coverage before early stopping is triggered. Acts as a safeguard against
        evolutionary stagnation, preventing wasted computation when the population
        ceases to progress. If the best fitness remains unchanged for this many
        generations, the run is terminated early under the assumption that further
        improvement is unlikely.

    
    Returns
    -------
    tuple
        (best_program, best_fitness, run_dir)
        - best_program : AST of the highest-fitness individual found
        - best_fitness : Fitness value of best_program
        - run_dir : Path to saved run directory (None if save_runs=False)
    """
    
    # === RNG Seeding ===
    if rng_seed is None and hasattr(cfg, "seed"):
        rng_seed = cfg.seed
    if rng_seed is not None:
        random.seed(rng_seed)

    # === Setup ===
    run_dir = setup_run_directory(save_runs, outdir)
    population = initialize_population(seeds, metas, pop_size)

    best_fit=None
    stagnation_counter=0

    # === Main Evolutionary Loop ===
    for g in range(generations):
        # Evaluate fitness + metadata
        if g == 0:
            results = [(gh.initial_metadata_fitness(ast, meta, cfg,mode=fitness_mode), meta)
                       for ast, meta in population]
        else:
            results = [gh.evolve_meta_data_fitness(ast, cfg,mode=fitness_mode)
                       for ast, _ in population] 

        # Split out floats for selection, keep tuples for saving
        fitnesses = [fit for fit, _ in results]
        best_idx, current_best_fit = get_best_individual(fitnesses)

        if best_fit is None or current_best_fit > best_fit:
            best_fit = current_best_fit
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        if stagnation_counter >= stagnation_patience:
            log_event("Stagnation stop - Patience Exceeded",
            f"Stagnation detected after {stagnation_patience} generations (best_fit={best_fit:.6f}).",
            run_dir)
            break

        log_event("Information",
        f"[DEBUG] Stagnation counter = {stagnation_counter}/{stagnation_patience}",
        run_dir)

        # Debug print
        log_event("Information",
          f"[DEBUG] Generation {g}: Best index = {best_idx}, "
          f"Current best = {current_best_fit:.6f}, Historical best = {best_fit:.6f}",
          run_dir)


        # Log progress
        log_event("Information",f"Gen {g:02d} | best={current_best_fit:.3f}",run_dir)
        record_generation_info(run_dir, g, current_best_fit) #record info on the json to use in visualisation purposes
        save_generation_if_needed(save_runs, run_dir, population, results, g)

        # Early stopping if the threasholds are met
        if target_fitness is not None and best_fit >= target_fitness:
            log_event("Early Stop-Target Reached",
            f"Early stop at gen {g:02d} (target_fitness {target_fitness} reached, best_fit={best_fit:.6f}).",
            run_dir)
            
            break

        # === Elitism: Preserve best individuals ===
        elite_idxs = sorted(range(len(population)),
                            key=lambda i: fitnesses[i],
                            reverse=True)[:elitism]
        next_pop = [utils.safe_copy(population[i]) for i in elite_idxs]

        # === Build mating pool ===
        pop_asts = [ast for ast, _ in population]

        valid_population=[]
        if fitness_mode == const.Fitness_Mode.PLUGIN:
            valid_population = [
                (ast, fit)
                for (ast, fit), (_, _) in zip(zip(pop_asts, fitnesses), population)
                if fit > 0 and static_analyser.check_syntax_from_string(emit_translation_unit(ast))
            ]

        elif fitness_mode==const.Fitness_Mode.COMPILER:
            valid_population = [
                (ast, fit)
                for (ast, fit), (_, _) in zip(zip(pop_asts, fitnesses), population)
                if fit > 0
            ]

        valid_pop_asts = [ast for ast, _ in valid_population]
        valid_fitnesses = [fit for _, fit in valid_population]


        # Debug print: original vs valid population
        orig_len = len(population)
        valid_len = len(valid_population)
        filtered_out = orig_len - valid_len

        log_event("Information",f"[DEBUG] Population size = {orig_len}, Valid = {valid_len}, Filtered out = {filtered_out}",run_dir)
        # print(f"[DEBUG] Population size = {orig_len}, Valid = {valid_len}, Filtered out = {filtered_out}")

        if len(valid_population)==0 and len(valid_fitnesses)==0:
            # This happens when there is no valid population found
            # Often common when proxy fitness is switched off and coverage server is unavailable
            # uncomment the following if non filterd population is to be used instead
            # Please not that valid population ensure quality of individuals that are used for mating pool
            # Using invalid population may lead to degenerate evolution

            # mating_pool = build_mating_pool(pop_asts, fitnesses, pop_size, elitism,
            #                            max_reuse, selection_method, tournament_k,
            #                            case_results)

            log_event("Information","[DEBUG] No valid individuals found. Terminating evolution.",run_dir)

            break
        else:

            log_event("Information","[DEBUG] Building mating pool from valid individuals.",run_dir)

            mating_pool = build_mating_pool(valid_pop_asts, valid_fitnesses, pop_size, elitism,
                                        max_reuse, selection_method, tournament_k,
                                        case_results)

        
        # === Produce offspring ===
        offspring = produce_offspring(mating_pool, pop_size, elitism, crossover_prob,
                                      mutation_prob, enable_mutation, include_decl_mut_prob,
                                      crossover_method,compile_check_offspring)

        # === Next population ===
        next_pop.extend(offspring)
        population = next_pop[:pop_size]

    # === Final evaluation and return ===
    final_results = [gh.evolve_meta_data_fitness(ast, cfg,mode=fitness_mode) for ast, _ in population]
    final_fitnesses = [fit for fit, _ in final_results]
    best_idx, best_fit = get_best_individual(final_fitnesses)

    # Save final generation artifacts
    save_generation_if_needed(save_runs, run_dir, population, final_results, "final")

    # Log final fitness info
    log_event("Final GP Result", f"Final evaluation completed. Best individual index = {best_idx}, "
        f"Best fitness = {best_fit:.6f}", run_dir)

    return population[best_idx][0], best_fit, run_dir



# -----------------------------
# Main harness
# -----------------------------
if __name__ == "__main__":
    # seed_folder = "Test/CPP_Programs_Meta_Real_Sample"
    seed_folder = "Test/CPP_Programs_Meta_Small"
    seeds, metas = gh.load_seed_programs_with_meta(seed_folder)
    print(f"Loaded {len(seeds)} seed programs (metadata used only for Gen 0).")

    if not seeds:
        print(f"No seed programs found in {seed_folder}")
    else:
        class Cfg:
            seed = 42
            target_fitness = None
        cfg = Cfg()

        #Mutation rarely works when the probability is low and work when the probability is high

        best_ast, best_fit, run_dir = evolve(
            seeds,
            metas,
            cfg=cfg,
            pop_size=len(seeds),
            generations=1,
            crossover_prob=0.9,
            mutation_prob=1.0,
            elitism=2,
            selection_method=const.Selection_Methods.TOURNAMENT_SELECT,
            crossover_method=const.Crossover_Methods.SUBTREE,
            tournament_k=5,
            case_results=None,
            include_decl_mut_prob=0.1,
            save_runs=True,
            outdir=const.GP_RUNS_COMPILER_DIR,
            target_fitness=getattr(cfg, "target_fitness", None),
            rng_seed=getattr(cfg, "seed", None),
            enable_mutation=True,
            compile_check_offspring=False,
            fitness_mode=const.Fitness_Mode.PLUGIN
        )

        print("Best proxy fitness:", best_fit)
        print("\nGenerated code for best individual:")
        print(gh.parse_ast_to_code(best_ast))

        print(run_dir)


# python3 -m src.gp_manager.gp_algorithm