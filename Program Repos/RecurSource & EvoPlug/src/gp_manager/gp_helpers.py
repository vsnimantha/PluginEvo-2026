# gp_helpers.py
import os, copy, json, random, datetime
from typing import Any
from pathlib import Path
from src.gp_manager.common import constant as const, gp_utils,utils
from src.ast_manager.ast_to_code.ast_to_code_parser import emit_translation_unit
from src.common import static_analyser,chart_generator
from src.gp_manager import selection, crossover
from src.gp_manager.mutations import mutate_node
from src.ast_manager.code_to_ast.ast_parser import ASTParser
from src.gp_manager import fitness_plugin,fitness_compiler

# -----------------------------
# Mutation operator
# -----------------------------
def mutate_ast(ast, include_decl_prob=0.0):
    # Try deep copy first, fallback to shallow copy or original
    try:
        new_ast = utils.safe_copy(ast)
    except Exception as e:
        print(f"[DEBUG] deepcopy failed: {e}")
        try:
            new_ast = copy.copy(ast)
            print("[DEBUG] Fallback to shallow copy succeeded.")
        except Exception as e2:
            print(f"[DEBUG] shallow copy also failed: {e2}")
            new_ast = ast  # final fallback

    # Ensure ast is not None or invalid
    if new_ast is None:
        print("[DEBUG] AST is None, returning original.")
        return ast

    cats = {"expr", "stmt"} | ({"decl"} if random.random() < include_decl_prob else set())
    candidates = gp_utils.collect_nodes(
        new_ast,
        lambda n: const.category(n) in cats and n.kind != "RAW_TOKENS"
    )
    if not candidates:
        print("[DEBUG] No mutation candidates found.")
        return new_ast

    target = random.choice(candidates)
    print(f"[DEBUG] Mutating node: kind={target.kind}, category={const.category(target)}, value={getattr(target, 'value', None)}")

    mutate_node(target)
    return new_ast


# -----------------------------
# Crossover operator
# -----------------------------
def crossover_ast(ast1, ast2, method=const.Crossover_Methods.SUBTREE):
    if method == const.Crossover_Methods.SUBTREE:
        return crossover.subtree_crossover(ast1, ast2)
    elif method == const.Crossover_Methods.SIZE_FAIR:
        return crossover.size_fair_crossover(ast1, ast2)
    elif method == const.Crossover_Methods.UNIFORM:
        return crossover.uniform_crossover(ast1, ast2)
    elif method == const.Crossover_Methods.ONE_POINT:
        return crossover.one_point_crossover(ast1, ast2)
    else:
        raise ValueError(f"Unknown crossover method: {method}")

# -----------------------------
# Fitness functions
# -----------------------------

def initial_metadata_fitness(ast, meta, cfg=None,mode=const.Fitness_Mode.PLUGIN):
    if mode==const.Fitness_Mode.PLUGIN:
        return fitness_plugin.initial_metadata_fitness(ast,meta,cfg)
    elif mode==const.Fitness_Mode.COMPILER:
        return fitness_compiler.initial_metadata_fitness(ast,meta,cfg)

#BEST TO SET only_correct_code_for True for coverage
def evolve_meta_data_fitness(ast, cfg=None, only_correct_code=True, allow_proxy_fitness=False,mode=const.Fitness_Mode.PLUGIN):
    if mode==const.Fitness_Mode.PLUGIN:
        return fitness_plugin.evolve_meta_data_fitness(ast,cfg,only_correct_code=only_correct_code,allow_proxy_fitness=allow_proxy_fitness)
    elif mode==const.Fitness_Mode.COMPILER:
        return fitness_compiler.evolve_meta_data_fitness(ast,cfg,only_correct_code=False,allow_proxy_fitness=allow_proxy_fitness)

# -----------------------------
# Selection dispatch
# -----------------------------
def select_individual(pop_asts, fitnesses,
                      method=const.Selection_Methods.TOURNAMENT_SELECT,
                      tournament_k=3,
                      case_results=None):
    if method == const.Selection_Methods.TOURNAMENT_SELECT:
        return selection.tournament_select(pop_asts, fitnesses, k=tournament_k)
    elif method == const.Selection_Methods.ROULETTE_WHEEL_SELECT:
        return selection.roulette_wheel_select(pop_asts, fitnesses)
    elif method == const.Selection_Methods.RANK_SELECT:
        return selection.rank_select(pop_asts, fitnesses)
    elif method == const.Selection_Methods.LEXICASE_SELECT:
        if case_results is None:
            raise ValueError("Lexicase selection requires 'case_results'.")
        return selection.lexicase_select(pop_asts, case_results)
    else:
        raise ValueError(f"Unknown selection method: {method}")

# -----------------------------
# Save generation
# -----------------------------

def save_generation(population, fitnesses, gen, outdir=const.GP_RUNS_DIR,generate_chart=False):
    os.makedirs(outdir, exist_ok=True)
    gdir = os.path.join(outdir, f"gen_{gen:02d}") if isinstance(gen, int) else os.path.join(outdir, str(gen))
    os.makedirs(gdir, exist_ok=True)

    metrics_lines = ["index,fitness,size,has_meta\n"]
    best_idx = None
    best_fit = float("-inf")

    for i, ((ast, pop_meta), (fit, eval_meta)) in enumerate(zip(population, fitnesses)):
        size = gp_utils.count_nodes(ast)
        meta_to_save = eval_meta if eval_meta is not None else pop_meta
        has_meta = 1 if meta_to_save is not None else 0

        metrics_lines.append(f"{i},{fit:.6f},{size},{has_meta}\n")

        # Save AST dump as plain text
        try:
            ast_path = os.path.join(gdir, f"ind_{i:02d}_fit{fit:.3f}_ast.txt")
            save_astnode(ast, ast_path)
        except Exception as e:
            with open(os.path.join(gdir, f"ind_{i:02d}_fit{fit:.3f}_ast.txt"), "w") as af:
                af.write(f"// AST dump failed: {e}\n")

        # Save AST dump as JSON
        try:
            ast_json_path = os.path.join(gdir, f"ind_{i:02d}_fit{fit:.3f}_ast.json")
            save_astnode_json(ast, ast_json_path)
        except Exception as e:
            with open(ast_json_path, "w") as af:
                af.write(f"// AST JSON dump failed: {e}\n")

        try:
            src = emit_translation_unit(ast)
        except Exception as e:
            src = f"// Emission failed: {e}\n"

        with open(os.path.join(gdir, f"ind_{i:02d}_fit{fit:.3f}.cpp"), "w") as f:
            f.write(src)

        if meta_to_save is not None:
            with open(os.path.join(gdir, f"ind_{i:02d}_fit{fit:.3f}.json"), "w") as mf:
                json.dump(meta_to_save, mf, indent=2, sort_keys=True)

        # Track best individual
        if fit > best_fit:
            best_fit = fit
            best_idx = i
            best_ast = ast
            best_meta_to_save = meta_to_save

    # Save metrics CSV
    metrics_name = f"{gen}_metrics.csv" if not isinstance(gen, int) else f"gen_{gen:02d}_metrics.csv"
    with open(os.path.join(gdir, metrics_name), "w") as mf:
        mf.writelines(metrics_lines)

    # Save best individual separately in the same directory
    if best_idx is not None:
        try:
            src = emit_translation_unit(best_ast)
        except Exception as e:
            src = f"// Emission failed: {e}\n"

        with open(os.path.join(gdir, f"best_individual_fit{best_fit:.3f}.cpp"), "w") as f:
            f.write(src)

        if best_meta_to_save is not None:
            with open(os.path.join(gdir, f"best_individual_fit{best_fit:.3f}.json"), "w") as mf:
                json.dump(best_meta_to_save, mf, indent=2, sort_keys=True)


    # Save ranked fitness overview (index + fitness only) 
    ranked = sorted(
        [(i, fit) for i, (fit, _) in enumerate(fitnesses)],
        key=lambda x: x[1],
        reverse=True
    )

    # Save JSON
    ranked_path = os.path.join(
        gdir,
        f"gen_{gen:02d}_ranked.json" if isinstance(gen, int) else f"{gen}_ranked.json"
    )
    with open(ranked_path, "w") as rf:
        json.dump(
            [{"index": i, "fitness": f"{fit:.6f}"} for i, fit in ranked],
            rf,
            indent=2
        )

    if generate_chart:
        chart_generator.generate_charts_from_json(ranked_path,gdir)

    # Save plain text log
    ranked_log_path = os.path.join(
        gdir,
        f"gen_{gen:02d}_ranked.log" if isinstance(gen, int) else f"{gen}_ranked.log"
    )
    with open(ranked_log_path, "w") as lf:
        for i, fit in ranked:
            lf.write(f"Index {i:02d} | Fitness={fit:.6f}\n")




def save_astnode(node, filepath, indent=""):
    """
    Save the AST structure to a text file using the same format
    as print_astnode, but writing to disk instead of stdout.
    """
    with open(filepath, "w", encoding="utf-8") as f:

        def _walk(n, ind=""):
            f.write(f"{ind}{n.kind}: spelling={repr(n.spelling)}, "
                    f"token_value={repr(n.token_value)}, "
                    f"type_name={repr(getattr(n, 'type_name', None))}\n")
            for child in n.children:
                _walk(child, ind + "  ")

        _walk(node, indent)

def ast_to_dict(node):
    """Recursively convert AST node to a dictionary for JSON serialization."""
    return {
        "kind": node.kind,
        "spelling": getattr(node, "spelling", None),
        "token_value": getattr(node, "token_value", None),
        "type_name": getattr(node, "type_name", None),
        "children": [ast_to_dict(child) for child in getattr(node, "children", [])]
    }

def save_astnode_json(node, filepath):
    """Save AST structure as JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(ast_to_dict(node), f, indent=2, sort_keys=True)


# -----------------------------
# Parsing helpers
# -----------------------------
def parse_code_to_ast(path):
    parser = ASTParser(path, language="c++", std="c++17")
    try:
        root = parser.parse(False)
        return parser.clang_cursor_to_astnode(root)
    except Exception as e:
        print(f"Parse failed for {path}: {e}")
        return None

def load_seed_programs_with_meta(folder):
    print("[DEBUG] Loading the seed programs...")
    cpp_files = list(Path(folder).glob("*.cpp"))
    seeds, metas = [], []
    for f in cpp_files:
        print(f"[DEBUG] Parsing file: {f}") 
        ast = parse_code_to_ast(f)
        if ast is not None:
            seeds.append(ast)
            meta_path = Path(str(f) + ".json")
            if meta_path.exists():
                with open(meta_path) as mf:
                    metas.append(json.load(mf))
            else:
                metas.append(None)
    print("[DEBUG] Loaded seed programs successfully.")
    return seeds, metas

def parse_ast_to_code(ast):
    return emit_translation_unit(ast)
