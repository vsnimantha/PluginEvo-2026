from pydantic import BaseModel
from typing import Optional

class RunConfig(BaseModel):
    pop_size: int = 50
    generations: int = 20
    crossover_prob: float = 0.8
    mutation_prob: float = 0.3
    elitism: int = 1
    target_coverage: Optional[float] = 95.0
    max_cycles: int = 5   # fail-safe upper bound
    stagnation_patience: int = 20   # stagnation control
    enable_mutation: bool = True   # 
