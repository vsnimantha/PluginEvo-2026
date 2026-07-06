# Confirmed Bug Record: SecRetAddress #1

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | SecRetAddress (compiled_plugin), g++ 13.3.0 x86_64 |
| Crash | Segmentation fault in single_pred_edge (GCC header), called by plugin |
| Crash site | plugin.cpp:153 (instrument_exit) -> single_pred/single_pred_edge |
| Pass | GIMPLE pass: instr_pass2 |
| Trigger | function victim() with multiple exit predecessors; default args |
| Class | LOGIC DEFECT — GCC-API precondition violation (single_pred needs 1 pred) |
| Origin | **PLUGIN — CONFIRMED BY TRACE** (crash from plugin.cpp:153 -> :207 -> :241) |
| Static-detectable | NO (GCC-API precondition; same category as cprintf) |

## Console trace
```
[*] Checking function: 'victim'
[-] Found Buffer: buf
[-] Found Buffer: shadow
[!] Instrumenting function: 'victim' at: test_secAddr_bug_found.cpp:18
during GIMPLE pass: instr_pass2
test_secAddr_bug_found.cpp:18:6: internal compiler error: Segmentation fault
0x...  single_pred_edge(basic_block_def const*)  basic-block.h:343
0x...  single_pred(basic_block_def const*)       basic-block.h:361
0x...  instrument_exit                           plugin.cpp:153
0x...  instrument_functions                      plugin.cpp:207
0x...  execute                                   plugin.cpp:241
```

## Root cause in source — plugin.cpp:153 (instrument_exit)
```cpp
static void instrument_exit(function *fun, tree var){
	basic_block bb;
	...
	bb = single_pred(EXIT_BLOCK_PTR_FOR_FN(fun));   // <-- :153 CRASH
	gsi_exit_bb = gsi_last_bb(bb);
	...
```
The plugin calls single_pred() on the function's EXIT block to get "the block
before exit". single_pred() has a HARD PRECONDITION: the block must have exactly
ONE predecessor (internally single_pred_edge dereferences assuming one incoming
edge). A function whose exit block has MULTIPLE predecessors (multiple return
paths / branches reaching the end) violates this -> single_pred_edge segfaults.
The test function victim() has multiple exit predecessors, so the plugin crashes.
Correct code would check single_pred_p(EXIT_BLOCK...) first, or iterate all
predecessor edges instead of assuming one.

## Classification
LOGIC DEFECT — GCC-API contract violation (single_pred precondition), same
CATEGORY as cprintf (unchecked gimple_call_arg), different API. Crashes on
ordinary C++ with multiple returns, plugin used with default args. Strong bug.

## Phase 2 — Static Backtrack
| Tool | Result |
|---|---|
| cppcheck | NOT flagged (only unrelated unusedStructMember note) |
| g++ -Wall -Wextra | NOT flagged |
GCC-API precondition (single_pred requires 1 predecessor) is not modeled by
static tools. 2x2 cell: CONFIRMED + STATICALLY-MISSED.
