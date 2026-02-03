from typing import Final

EXPR_KINDS: Final[set[str]] = {
    "BINARY_OPERATOR", "UNEXPOSED_EXPR", "DECL_REF_EXPR",
    "INTEGER_LITERAL", "STRING_LITERAL", "CALL_EXPR"
}
STMT_KINDS: Final[set[str]] = {
    "RETURN_STMT", "DECL_STMT", "IF_STMT", "FOR_STMT",
    "COMPOUND_STMT", "CALL_EXPR", "RAW_TOKENS", "USING_DIRECTIVE"
}
DECL_KINDS: Final[set[str]] = {"VAR_DECL", "PARM_DECL", "FUNCTION_DECL", "INCLUSION_DIRECTIVE", "NAMESPACE_REF"}

def category(node):
    if node.kind in EXPR_KINDS: return "expr"
    if node.kind in STMT_KINDS: return "stmt"
    if node.kind in DECL_KINDS: return "decl"
    return "other"


class Selection_Methods:
    TOURNAMENT_SELECT: Final[str] = 'tournament_select'
    ROULETTE_WHEEL_SELECT: Final[str] = 'roulette_wheel_select'
    RANK_SELECT: Final[str] ='rank_select'
    LEXICASE_SELECT: Final[str] ='lexicase_select'

class Crossover_Methods:
    SUBTREE: Final[str] = 'subtree_crossover'          # Koza, 1992
    SIZE_FAIR: Final[str] = 'size_fair_crossover'      # Langdon, 1995
    UNIFORM: Final[str] = 'uniform_crossover'          # Syswerda, 1989 (adapted to GP)
    ONE_POINT: Final[str] = 'one_point_crossover'      # Holland, 1975 (adapted by Koza)


GP_RUNS_DIR: Final[str] = "GP_Runs" # OFFLINE TESTING PURPOSE DIRECTORY
GP_RUNS_COMPILER_DIR: Final[str] = "GP_Compiler_Runs" # OFFLINE TESTING PURPOSE DIRECTORY

class Fitness_Mode:
    COMPILER: Final[str] = 'compiler'
    PLUGIN: Final[str] = 'plugin'

class Plugin_Target_Type:
    COVERAGE: Final[str] = 'Coverage'
    CRASH_BUGS: Final[str] = 'Crash_Bugs'

class Compiler_Target_Bug_Type:
    ICE: Final[str] = 'ICE'
    DIFF: Final[str] = 'DIFF'