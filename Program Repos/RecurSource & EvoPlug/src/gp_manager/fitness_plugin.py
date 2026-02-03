import random
from typing import Any
from src.gp_manager.common import constant as const, gp_utils
from src.ast_manager.ast_to_code.ast_to_code_parser import emit_translation_unit
from src.common import static_analyser
from src.communication_manager import gp_adaptive_fitness_requester


def _coverage_fitness(ast, meta, use_size_penalty: bool):
    # meta is expected to be a coverage dict here
    line_cov = meta.get("line_coverage", 0.0) / 100.0
    branch_cov = meta.get("branch_coverage", 0.0) / 100.0
    decision_cov = meta.get("decision_coverage", 0.0) / 100.0
    func_cov = meta.get("function_coverage", 0.0) / 100.0
    call_cov = meta.get("call_coverage", 0.0) / 100.0

    coverage_score = (
        0.3 * line_cov +
        0.2 * branch_cov +
        0.2 * decision_cov +
        0.2 * func_cov +
        0.1 * call_cov
    )

    size_penalty = 0.001 * gp_utils.count_nodes(ast) if use_size_penalty else 0.0
    return max(0.0, coverage_score - size_penalty)


def _crash_bug_fitness(ast, meta, use_size_penalty: bool):
    """
    Fitness for plugin crash/bug finding.

    Assumes meta has a "crash" entry with:
      { "crashed": bool, "stderr": str, ... }

    Strategy:
      - Base fitness 1.0 for any crash.
      - Bonus if stderr looks like ICE / plugin related.
      - Optional size penalty to keep programs small.
    """
    crash_info = meta.get("crash", {}) if isinstance(meta, dict) else {}
    crashed = bool(crash_info.get("crashed", False))
    stderr = (crash_info.get("stderr") or "").lower()

    if not crashed:
        # No crash → very low but non-zero to keep them in the population if needed
        base = 0.0
    else:
        base = 1.0

    # Heuristic: identify “interesting” compiler/plugin bugs
    is_ice = any(
        token in stderr
        for token in [
            "internal compiler error",
            "please submit a full bug report",
            "ice:",
        ]
    )
    # Tune this to your plugin name / typical messages
    is_plugin_related = any(
        token in stderr
        for token in [
            "cprintf",        # plugin name
            "gcc plugin",     # generic
            "plugin error",
        ]
    )

    bonus = 0.0
    if crashed and is_ice:
        bonus += 0.5
    if crashed and is_plugin_related:
        bonus += 0.5

    score = base + bonus  # max around 2.0 with this scheme

    size_penalty = 0.001 * gp_utils.count_nodes(ast) if use_size_penalty else 0.0
    return max(0.0, score - size_penalty)


def fitness_evaluator(
    ast,
    meta,
    cfg=None,
    use_size_penalty: bool = False,
    target_fitness_type=const.Plugin_Target_Type.COVERAGE,
):
    if not isinstance(meta, dict):
        print(f"[DEBUG] fitness_evaluator: meta is not a dict ({type(meta)}), returning 0.0")
        return 0.0

    if target_fitness_type == const.Plugin_Target_Type.COVERAGE:
        # meta is expected to be the coverage dict directly
        return _coverage_fitness(ast, meta, use_size_penalty)

    if target_fitness_type == const.Plugin_Target_Type.CRASH_BUGS:
        # meta is expected to be the full meta dict from the server
        return _crash_bug_fitness(ast, meta, use_size_penalty)

    # Fallback for unknown target type
    return 0.0




# def fitness_evaluator(ast, meta, cfg=None, use_size_penalty=False):
#     if not isinstance(meta, dict):
#         print(f"[DEBUG] fitness_evaluator: meta is not a dict ({type(meta)}), returning 0.0")
#         return 0.0

#     # Normalize coverage metrics to [0,1]
#     line_cov = meta.get("line_coverage", 0.0) / 100.0
#     branch_cov = meta.get("branch_coverage", 0.0) / 100.0
#     decision_cov = meta.get("decision_coverage", 0.0) / 100.0
#     func_cov = meta.get("function_coverage", 0.0) / 100.0
#     call_cov = meta.get("call_coverage", 0.0) / 100.0

#     coverage_score = (
#         0.3 * line_cov +
#         0.2 * branch_cov +
#         0.2 * decision_cov +
#         0.2 * func_cov +
#         0.1 * call_cov
#     )

#     size_penalty = 0.001 * gp_utils.count_nodes(ast) if use_size_penalty else 0.0
#     return max(0.0, coverage_score - size_penalty)


# TODO: IMPLEMENT PLUGIN CRASH TEST SCENARIO TO TALK TO THE CRASH TEST SERVER
def evolve_meta_data_fitness(ast, cfg=None, only_correct_code=True, allow_proxy_fitness=False):
    meta: dict[str, Any] | None = None

    if gp_adaptive_fitness_requester.check_api_health():
        code = emit_translation_unit(ast)
        if only_correct_code:
            is_code_correct = static_analyser.check_syntax_from_string(code)
            if is_code_correct:  # send only statically correct code
                meta = gp_adaptive_fitness_requester.get_coverage_from_api(source_code=code)
        else:
            meta = gp_adaptive_fitness_requester.get_coverage_from_api(source_code=code)

        # Always delegate to fitness_evaluator, even if meta is None
        return fitness_evaluator(ast, meta, cfg), meta

    else:
        # API not healthy → fallback
        if allow_proxy_fitness:
            return proxy_fitness(ast, cfg), meta
        else:
            # Pass meta=None so fitness_evaluator returns 0.0
            return fitness_evaluator(ast, None, cfg), meta

    
def initial_metadata_fitness(ast, meta, cfg=None):
    return fitness_evaluator(ast,meta,cfg)

def proxy_fitness(ast, cfg=None):
    size = gp_utils.count_nodes(ast)
    depth = gp_utils.tree_depth(ast)
    branches = gp_utils.count_branches(ast)

    # normalize heuristics
    size_score = max(0.0, 1.0 - 0.001 * size)
    depth_score = min(1.0, depth / 50.0)   # cap at 50
    branch_score = min(1.0, branches / 20.0)

    noise = random.uniform(-0.02, 0.02)

    return max(0.0, min(1.0, 0.5*size_score + 0.3*depth_score + 0.2*branch_score + noise))