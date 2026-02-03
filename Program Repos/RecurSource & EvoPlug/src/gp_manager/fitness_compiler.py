import random
from typing import Any
from src.gp_manager.common import constant as const, gp_utils
from src.ast_manager.ast_to_code.ast_to_code_parser import emit_translation_unit
from src.common import static_analyser
from src.communication_manager import gp_adaptive_fitness_requester

def fitness_evaluator(
    ast,
    summary: dict,
    cfg=None,
    use_size_penalty=False,
    target_bug_type=const.Compiler_Target_Bug_Type.ICE,
):
    """
    Evaluate fitness based on compiler bug discovery.
    Focus can be ICE (default) or DIFF for differential mismatches.
    """
    if summary is None:
        print("[DEBUG] Summary is None → returning 0.0")
        return 0.0

    print("[DEBUG] Raw summary:", summary)

    def safe_val(key):
        val = summary.get(key)
        return int(val) if isinstance(val, (int, float)) else 0

    total = (
        safe_val("success_count")
        + safe_val("failure_count")
        + safe_val("ice_count")
        + safe_val("timeout_count")
        + safe_val("differential_mismatches")
    )
    if total == 0:
        total = 1

    print(f"[DEBUG] Total attempts (recomputed): {total}")

    ice_frac = safe_val("ice_count") / total
    mismatch_frac = safe_val("differential_mismatches") / total
    failure_frac = safe_val("failure_count") / total
    timeout_frac = safe_val("timeout_count") / total
    success_frac = safe_val("success_count") / total

    print(
        f"[DEBUG] Fractions → ICE: {ice_frac:.3f}, Mismatch: {mismatch_frac:.3f}, "
        f"Failure: {failure_frac:.3f}, Timeout: {timeout_frac:.3f}, Success: {success_frac:.3f}"
    )

    # Choose weights depending on focus
    if target_bug_type == const.Compiler_Target_Bug_Type.ICE:
        fitness = (
            0.6 * ice_frac
            + 0.4 * mismatch_frac
            - 0.1 * failure_frac
            - 0.1 * timeout_frac
            - 0.2 * success_frac
        )
    elif target_bug_type == const.Compiler_Target_Bug_Type.DIFF:
        fitness = (
            0.7 * mismatch_frac  # emphasize differential mismatches
            + 0.2 * ice_frac  # ICEs less important
            - 0.05 * failure_frac  # lighter penalty
            - 0.05 * timeout_frac
            - 0.1 * success_frac  # success is expected, small penalty
        )
    else:
        # Graceful fallback
        print(
            f"[WARN] Unknown target_bug_type={target_bug_type}. "
            "Defaulting to ICE-centric scoring."
        )
        fitness = (
            0.6 * ice_frac
            + 0.4 * mismatch_frac
            - 0.1 * failure_frac
            - 0.1 * timeout_frac
            - 0.2 * success_frac
        )

    print(f"[DEBUG] Initial fitness ({target_bug_type}-centric): {fitness:.3f}")

    if ice_frac == 0 and mismatch_frac == 0 and failure_frac == 0 and timeout_frac == 0:
        diversity_bonus = 0.005 * gp_utils.count_unique_node_types(ast)
        fitness += diversity_bonus

    if use_size_penalty:
        size_penalty = 0.001 * gp_utils.count_nodes(ast)
        fitness -= size_penalty
        print(
            f"[DEBUG] Size penalty applied: -{size_penalty:.3f} → fitness now {fitness:.3f}"
        )

    clamped = max(0.0, min(1.0, fitness))
    print(f"[DEBUG] Final clamped fitness: {clamped:.3f}")

    return clamped


def evolve_meta_data_fitness(ast, cfg=None, only_correct_code=False, allow_proxy_fitness=False):
    """
    Request compiler testing results via API/service and evaluate fitness.
    """
    summary = None

    if gp_adaptive_fitness_requester.check_compiler_api_health():
        code = emit_translation_unit(ast)
        if only_correct_code:
            is_code_correct = static_analyser.check_syntax_from_string(code)
            if is_code_correct:
                summary = gp_adaptive_fitness_requester.get_compiler_result_from_api(source_code=code)
        else:
            summary = gp_adaptive_fitness_requester.get_compiler_result_from_api(source_code=code)

        return fitness_evaluator(ast, summary, cfg), summary

    else:
        # API not healthy → fallback
        if allow_proxy_fitness:
            return proxy_fitness(ast, cfg), summary
        else:
            return fitness_evaluator(ast, None, cfg), summary


def initial_metadata_fitness(ast, summary, cfg=None):
    return fitness_evaluator(ast, summary, cfg)


def proxy_fitness(ast, cfg=None):
    """
    Heuristic fallback when compiler tester API is unavailable.
    """
    size = gp_utils.count_nodes(ast)
    depth = gp_utils.tree_depth(ast)
    branches = gp_utils.count_branches(ast)

    # normalize heuristics
    size_score = max(0.0, 1.0 - 0.001 * size)
    depth_score = min(1.0, depth / 50.0)
    branch_score = min(1.0, branches / 20.0)

    noise = random.uniform(-0.02, 0.02)

    return max(0.0, min(1.0, 0.5*size_score + 0.3*depth_score + 0.2*branch_score + noise))
