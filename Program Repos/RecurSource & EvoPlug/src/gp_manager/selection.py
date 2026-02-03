import random, copy
from src.gp_manager.common import utils

def tournament_select(pop, fitnesses, k=3):
    """
    Tournament Selection:
    - Randomly sample k individuals from the population.
    - Return the one with the highest fitness.
    - Larger k increases selection pressure (more likely to pick the best).
    """
    idxs = random.sample(range(len(pop)), min(k, len(pop)))
    best_i = max(idxs, key=lambda i: fitnesses[i])
    return utils.safe_copy(pop[best_i])


def roulette_wheel_select(pop, fitnesses):
    """
    Roulette-Wheel (Fitness Proportionate) Selection:
    - Each individual gets a slice of probability proportional to its fitness.
    - Spin the 'wheel' to select one.
    - Works best when fitness values vary widely.
    """
    total_fit = sum(fitnesses)
    if total_fit == 0:
        # If all fitnesses are zero, just pick randomly
        return utils.safe_copy(random.choice(pop))
    pick = random.uniform(0, total_fit)
    current = 0
    for ind, fit in zip(pop, fitnesses):
        current += fit
        if current >= pick:
            return utils.safe_copy(ind)
    # Fallback in case of rounding issues
    return utils.safe_copy(pop[-1])


def rank_select(pop, fitnesses):
    """
    Rank Selection:
    - Sort individuals by fitness.
    - Assign probabilities based on rank (not raw fitness).
    - Helps when fitness values are clustered close together.
    """
    sorted_indices = sorted(range(len(pop)), key=lambda i: fitnesses[i])
    n = len(pop)
    ranks = list(range(1, n+1))  # lowest gets 1, highest gets n
    total = sum(ranks)
    pick = random.uniform(0, total)
    current = 0
    for rank, idx in zip(ranks, sorted_indices):
        current += rank
        if current >= pick:
            return utils.safe_copy(pop[idx])
    return utils.safe_copy(pop[sorted_indices[-1]])


def lexicase_select(pop, case_results):
    """
    Lexicase Selection:
    - Designed for multi-test-case fitness (e.g. coverage per input).
    - Randomize the order of test cases.
    - Filter candidates: keep only those that are best on the current case.
    - Continue until one candidate remains or all cases are used.
    - Preserves 'specialists' that excel on different cases.
    """
    candidates = list(range(len(pop)))
    cases = list(range(len(case_results[0])))
    random.shuffle(cases)
    for c in cases:
        # Find best performance on this case among remaining candidates
        best = max(case_results[i][c] for i in candidates)
        # Keep only those that match the best
        candidates = [i for i in candidates if case_results[i][c] == best]
        if len(candidates) == 1:
            break
    chosen_idx = random.choice(candidates)
    return utils.safe_copy(pop[chosen_idx])
