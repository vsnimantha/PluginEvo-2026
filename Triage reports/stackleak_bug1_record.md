# Confirmed Bug Record: stack_leak #1

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | stack_leak (compiled_plugin), g++-10 x86_64 |
| Crash site | add_stack_tracking_gasm, stackleak_plugin.c:131 |
| Chain | :131 -> add_stack_tracking :172 -> stackleak_instrument_execute :265/:220 |
| Class | ROBUSTNESS — crashes on missing 'arch' argument (user config error) |
| Origin | **PLUGIN — CONFIRMED BY TRACE** |
| Static-detectable | NO (reachable assert; needs whole-program reasoning) |

## Console trace
```
during GIMPLE pass: stackleak_instrument
test.cpp: In function 'void alpha()':
test.cpp:3:6: internal compiler error: in add_stack_tracking_gasm, at stackleak_plugin.c:131
0x...  add_stack_tracking_gasm         stackleak_plugin.c:131
0x...  add_stack_tracking              stackleak_plugin.c:172
0x...  stackleak_instrument_execute    stackleak_plugin.c:265
```
Command: g++-10 -fplugin=compiled_plugin.so
  -fplugin-arg-compiled_plugin-track-min-size=1024 -g test.cpp -o test.o
  (NOTE: arch=x86 NOT passed)

## Root cause in source — stackleak_plugin.c:124-131
```c
static void add_stack_tracking_gasm(gimple_stmt_iterator *gsi, bool after)
{
	gasm *asm_call = NULL;
	tree sp_decl, input;
	vec<tree, va_gc> *inputs = NULL;

	/* 'no_caller_saved_registers' is currently supported only for x86 */
	gcc_assert(build_for_x86);          // <-- :131 fires when build_for_x86 == false
```
`build_for_x86` is false by default (:46) and set true ONLY if the plugin is
invoked with `arch=x86` (:601). The run passed track-min-size but not arch=x86,
so the assert aborts with an ICE.

## Classification — HONEST NUANCE
ROBUSTNESS bug, NOT a logic defect. The assert is intentional; it fires on a
USER CONFIGURATION ERROR (missing required arch arg). The defensible criticism:
the plugin uses gcc_assert (hard ICE) for a user-input condition that should be
a graceful error() (as it does for unknown options at :607). WEAKER than DFED:
DFED crashes when used correctly; stackleak crashes when used incorrectly.

## Triggers — ALL dedup to this one bug (crash line :131 in every case)
| Program | Function | ice_location |
|---|---|---|
| test.cpp | alpha | :131 |
| test_bug_found_1.1.cpp | frame_size_edge | :131 (via :220) |
| test_bug_found_1.2.cpp | pure_leaf_1 | :131 |
| test_bug_found_1.3.cpp | ctor_stress | :131 |
| test_bug_found_1.4.cpp | main | :131 |
=> 1 distinct bug, 5 triggers. NOT 2 bugs.

## Phase 2 — Static Backtrack
| Tool | Result |
|---|---|
| cppcheck | NOT flagged |
| g++ -Wall -Wextra | NOT flagged |
Reachable-assert reasoning is beyond static tools. 2x2 cell: CONFIRMED + STATICALLY-MISSED.
