# PluginEvo: Systematic GCC Plugin Testing

A coverage-driven, activation-guided pipeline for systematic GCC plugin
testing using genetic programming. This repository contains the full
source code, plugin configurations, templates, and pre-computed
evaluation results for all 16 plugins evaluated in the paper.

---

## Repository Structure

```
PluginEvo/
├── src/                       # Source code for all four components
│   ├── gp_manager/            # EvoPlug: genetic programming engine
│   ├── ast_manager/           # RecurSource: mutable Clang AST library
│   ├── communication_manager/ # PluginSight client interface
│   └── common/                # Shared utilities
├── GCC_Plugins/               # All 16 evaluated GCC plugins
├── configs/                   # Per-plugin configuration files
├── templates/                 # Per-plugin SynCR template files
├── Test_Programs/             # Seed programs for each plugin
├── results/                   # Pre-computed coverage results for all 16 plugins
├── Triage_Reports/            # Per-bug triage notes and confirmation status
└── requirements/              # Dependency lists
```

---

## System Requirements

- **OS:** Ubuntu 22.04 or Ubuntu 24.04 (tested only on these distributions)
- **Python:** 3.10 or later
- **GCC:** Versions 10–14 (install all for full plugin compatibility)

Install system dependencies:

```bash
sudo apt update
sudo apt install gcc gcc-plugin-dev
```

For full GCC version support:

```bash
sudo apt install gcc-10 gcc-11 gcc-12 gcc-13 gcc-14
```

---

## Installing Python Requirements

```bash
pip install -r requirements.txt
```

Each plugin application inside `GCC_Plugins/` also contains its own
`requirements` folder. Install those before running plugin-specific tests:

```bash
pip install -r GCC_Plugins/<plugin_name>/requirements/requirements.txt
```

---

## Running a Full PluginEvo Experiment

To run the full PluginEvo pipeline on a specific plugin:

```bash
python3 -m src.gp_manager.gp_algorithm --config configs/<plugin_name>.cfg
```

For example, to run on the `cprintf` plugin:

```bash
python3 -m src.gp_manager.gp_algorithm --config configs/cprintf.cfg
```

Results are saved to the directory specified in the configuration file.
A full PluginEvo run requires 24–36 CPU hours per plugin, dominated by
repeated compilation, plugin execution, and coverage instrumentation.

---

## Using Pre-computed Results

To reproduce the tables and figures in the paper without rerunning the
full experiment, pre-computed coverage results for all 16 plugins are
available in the `results/` directory. Each subdirectory contains:

- `coverage.json` — per-metric coverage results (lines, branches,
  decisions, functions, calls)
- `bugs.json` — detected bug reports with stack traces
- `generation_log.json` — fitness evolution across generations

These files directly correspond to the data reported in Tables 3, 4,
and 5 and Figure 2 of the paper.

---

## Using Components Independently

All four components are independently usable without the full pipeline.

### SynCR: Plugin-Aware Seed Generator

Generate plugin-aware seed programs for a given plugin:

```bash
python3 -m src.syncr.generator --config configs/<plugin_name>.cfg \
    --output Test_Programs/<plugin_name>/ --count 100
```

### PluginSight: Standalone Plugin Tester

Compile and evaluate a C/C++ program against a GCC plugin:

```bash
python3 -m src.communication_manager.pluginsight \
    --plugin GCC_Plugins/<plugin_name>/ \
    --source <path_to_program.c> \
    --gcc-version 12
```

PluginSight returns structured coverage and failure reports independently
of the GP search loop and can be used with any test generation strategy,
including external fuzzers or manual test suites.

### RecurSource: Mutable AST Library

RecurSource is importable as a standalone library for structural
C/C++ program transformation and source regeneration:

```python
from src.ast_manager.code_to_ast.ast_parser import ASTParser
from src.ast_manager.ast_to_code.ast_to_code_parser import emit_translation_unit

parser = ASTParser("program.cpp", language="c++", std="c++17")
root = parser.parse(False)
ast = parser.clang_cursor_to_astnode(root)

# Modify the AST here, then regenerate compilable source:
source = emit_translation_unit(ast)
```

### EvoPlug: Genetic Programming Engine

EvoPlug can be used with any fitness oracle by implementing the
interface expected by `gp_adaptive_fitness_requester`. See
`src/gp_manager/fitness_plugin.py` for an example implementation.

---

## Using Custom Configurations

1. Open the plugin repository you want to work with in `GCC_Plugins/`.
2. Replace its existing configuration file with the config from `configs/`.
3. Adjust the parameters in the configuration file to match your
   test scenario.

The following parameters are most commonly adjusted per plugin:

- `gcc_version` — GCC version to use for compilation
- `plugin_path` — path to the compiled plugin `.so`
- `template_dir` — path to the plugin-specific SynCR templates
- `compiler_flags` — additional flags passed to GCC during compilation

---

## GCC Plugin Setup

The required GCC plugins are located in the `GCC_Plugins/` folder.
Each plugin subdirectory contains build instructions. To build a plugin:

```bash
cd GCC_Plugins/<plugin_name>
make
```

Ensure the resulting `.so` file path matches the `plugin_path` entry
in the corresponding configuration file.

---

## GP Hyperparameters

The following hyperparameters were used in all experiments reported in
the paper. They are set in the per-plugin configuration files in
`configs/` and override the code defaults.

| Parameter | Paper Value | Description |
|---|---|---|
| `pop_size` | 100 | Population size |
| `generations` | 100 | Maximum generations |
| `crossover_prob` | 0.8 | Subtree crossover probability |
| `mutation_prob` | 0.01 | Per-node mutation probability |
| `elitism` | 1 | Number of elites preserved |
| `selection_method` | `TOURNAMENT_SELECT` | Selection strategy |
| `tournament_k` | 3 | Tournament size |
| `crossover_method` | `SUBTREE` | Crossover strategy |
| `enable_mutation` | `True` | Mutation enabled |
| `stagnation_patience` | 50 | Generations without improvement before early stopping |
| `target_fitness` | 0.95 | Early stopping coverage threshold |
| `fitness_mode` | `PLUGIN` | Fitness signal source |

> **Note:** The code defaults in `gp_algorithm.py` differ from the
> values above. Always use the per-plugin cfg files in `configs/` to
> reproduce the paper results.

Fitness weights and wall-clock time budget are set in the per-plugin
cfg files.

---

## Prototype Status

All applications included in this repository are research prototypes
and experimental versions. They are intended for testing, research, and
evaluation purposes only. Functionality, stability, and compatibility
may change as development continues.

---

## Triage Reports

The `Triage_Reports/` directory contains the triage documentation for the
10 bugs confirmed by PluginEvo, organised as one subdirectory per affected
plugin (7 plugins total: `funcp_encrypt`, `gcc_assert_introspect`,
`stack_leak`, `cprintf`, `DFED`, `SecRetAddress`, `static_analyzer`). Each
subdirectory contains:

- `reproducer.c` / `reproducer.cpp` — a minimal program that triggers the
  failure
- `stack_trace.txt` — the compiler diagnostic or internal compiler error
  (ICE) trace pointing to the plugin or registered pass
- `triage_notes.md` — the manual triage notes recording how the bug
  classification criteria were applied (compiles successfully without the
  plugin; fails when the plugin is enabled; diagnostic or stack trace
  points to plugin code)
- `status.json` — current status (`reported` or `confirmed`) and, where
  applicable, the developer's response

As reported in the paper, the `DFED` bug has been confirmed by its
developer; the remaining nine are marked `reported` and are awaiting
response.

---

## Citation

If you use this artifact, please cite the paper:

```
[Citation to be added upon publication]
```
