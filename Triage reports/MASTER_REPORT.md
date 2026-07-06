# GCC Plugin ICE Confirmation — Master Report

Confirmation and static-backtrack analysis of the crash/ICE bugs reported by the
activation (GP-based) testing stage. Each bug was (1) confirmed as a real,
reproducible, PLUGIN-origin crash from its stack trace, (2) root-caused in the
plugin source, and (3) checked against standard static analysis tools
(cppcheck, g++ -Wall/-Wextra) to determine whether static analysis could have
caught it.

---

## HEADLINE RESULT

**7 distinct confirmed bugs across 7 plugins** (18 raw crash runs deduplicated).
**Static-detectability: 2 caught / 5 missed.**

The 2 statically-caught bugs are BOTH the same generic C++ defect (missing
return in a non-void function), flagged by a default -Wall warning. The other 5
are GCC-plugin-DOMAIN defects — API-contract violations and reachable
asserts/gcc_unreachable — that generic static tools do not model. Standard
static analysis is therefore necessary-but-insufficient for GCC plugins;
dynamic activation testing finds the domain-specific crashes it misses.

---

## SUMMARY TABLE

| # | Plugin | Crash site | Root cause | Class | Static? | Triggers | GCC |
|---|--------|-----------|------------|-------|---------|----------|-----|
| 1 | DFED | DFED_Plugin.cpp:167 (via :127) | missing `return` -> garbage -> strlen segfault | Missing return | **CAUGHT** | 1 | arm-none-eabi GCC7 |
| 2 | stack_leak | stackleak_plugin.c:131 | `gcc_assert(build_for_x86)` fires (no arch=x86) | Reachable assert (config) | missed | 5 | g++-10 |
| 3 | cprintf | gcc_hell.cpp:309 | `gimple_call_arg` OOB (no num_args check) | GCC-API contract | missed | 2 | g++ 13 |
| 4 | funcp_encrypt | funcp-encrypt.cc:288 | `gcc_assert(TREE_CODE==FIELD_DECL)` on C++ fields | Reachable assert (tree code) | missed | 1 | g++-10 |
| 5 | gcc_assert_introspect | plugin.c:498->521 | `gcc_unreachable`, incomplete integer-type dispatch | Incomplete dispatch | missed | 1 | gcc-10 (C) |
| 6 | static_analyzer | unit.h:293 | `fprintf2` missing `return` -> SIGILL | Missing return | **CAUGHT** | 5 | g++ 13 |
| 7 | SecRetAddress | plugin.cpp:153 | `single_pred(EXIT_BLOCK)` w/o single-pred check | GCC-API contract | missed | 1 | g++ 13 |

## BUG TAXONOMY (4 classes)
- **A. Missing return (non-void):** DFED, static_analyzer -> static CATCHES (2)
- **B. GCC-API contract violation:** cprintf, SecRetAddress -> static MISSES (2)
- **C. Reachable gcc_assert (wrong assumption):** stack_leak, funcp_encrypt -> static MISSES (2)
- **D. gcc_unreachable / incomplete dispatch:** gcc_assert_introspect -> static MISSES (1)

## DEDUPLICATION (honest counting)
| Plugin | Raw crash runs | Distinct bugs |
|---|---|---|
| DFED | 1 | 1 |
| stack_leak | 6 | 1 (all crash at :131) |
| cprintf | 2 | 1 (both at build_spec_function:309) |
| funcp_encrypt | 1 | 1 |
| gcc_assert_introspect | 2 | 1 (1 excluded g++ load-fail + 1 real ICE under gcc) |
| static_analyzer | 5 | 1 (all fprintf2:293) |
| SecRetAddress | 1 | 1 |
| **TOTAL** | **18** | **7** |

PluginEvo headline was 10 bugs; deduplication (stack_leak 2->1, cprintf 2->1,
static_analyzer 2->1) yields 7 distinct defects — one genuine bug per plugin.

## EXCLUDED (correctly, not counted as a bug)
- gcc_assert_introspect first run: loaded into g++ (cc1plus) and failed with
  undefined symbol c_build_function_call_vec — a C-frontend plugin in the C++
  compiler = toolchain mismatch, not a crash. The proper gcc (C) run then
  produced the real ICE (bug #5).

===============================================================================
# BUG 1 — DFED
===============================================================================
- Plugin: DFED (myDFEDPlugin), arm-none-eabi-g++ (GCC 7, cortex-m3)
- Crash: `internal compiler error: Segmentation fault`
- Trace: DFED_PLUGIN::isAllowedToRun (DFED_Plugin.cpp:167) <- gate (:58)
- Class: LOGIC DEFECT (crashes when used correctly). Developer-confirmed.
- Static: CAUGHT (both sub-bugs)

Root cause — two stacked bugs:
Bug A (segfault) — DFED_Plugin.cpp:127-129:
```cpp
const char* DFED_PLUGIN::findArgumentValue(const char* key){
    DFED_PLUGIN::findArgumentValue(key, args, argc);   // MISSING 'return' -> garbage
}
```
Caller does `const char* f = findArgumentValue("function"); ... strlen(f)` at
:167 -> dereferences garbage -> SEGFAULT.

Bug B (latent) — DFED_Plugin.cpp:139-148: throws `(const char*)msg` where msg is
a local char[1024] -> dangling pointer / use-after-scope.

Static backtrack:
- Bug A: g++ -Wreturn-type (in -Wall) -> "no return statement in function
  returning non-void" — FLAGGED
- Bug B: cppcheck -> "Returning pointer to local variable 'msg'
  [returnDanglingLifetime]" — FLAGGED
2x2: CONFIRMED + STATICALLY-FLAGGED.

===============================================================================
# BUG 2 — stack_leak
===============================================================================
- Plugin: stack_leak (compiled_plugin), g++-10 x86_64
- Crash: `internal compiler error: in add_stack_tracking_gasm, at stackleak_plugin.c:131`
- Trace: :131 -> add_stack_tracking :172 -> stackleak_instrument_execute :265/:220
- Class: ROBUSTNESS (crashes on missing 'arch' argument — user config error)
- Static: MISSED (reachable assert)

Root cause — stackleak_plugin.c:124-131:
```c
static void add_stack_tracking_gasm(gimple_stmt_iterator *gsi, bool after)
{
    ...
    /* 'no_caller_saved_registers' is currently supported only for x86 */
    gcc_assert(build_for_x86);          // :131 fires when build_for_x86 == false
```
`build_for_x86` is false by default (:46), set true only if invoked with
`arch=x86` (:601). The run passed track-min-size but not arch=x86, so the
assert aborts. HONEST NUANCE: this is a robustness/error-handling issue — the
plugin uses gcc_assert (hard ICE) for a user-input condition that should be a
graceful error() (as it does for unknown options at :607). Weaker than the
logic defects: it crashes when used INCORRECTLY (missing required arg).

Triggers (ALL dedup to this one bug, crash line :131 in every case):
test.cpp/alpha; test_bug_found_1.1/frame_size_edge; 1.2/pure_leaf_1;
1.3/ctor_stress; 1.4/main. => 1 distinct bug, 5 triggers.

Static backtrack: cppcheck NOT flagged; g++ -Wall NOT flagged. Reachable-assert
reasoning is beyond static tools. 2x2: CONFIRMED + STATICALLY-MISSED.

===============================================================================
# BUG 3 — cprintf
===============================================================================
- Plugin: cprintf (compiled_plugin), g++ 13.3.0 x86_64
- Crash: `Segmentation fault` at build_spec_function, gcc_hell.cpp:309
- Trace (run 2, full plugin frames): build_spec_function:309 ->
  insert_spec_func:377 -> handle_printfunc:287 -> callback_stmt:163 -> execute:55
- Class: LOGIC DEFECT (format/argument-count mismatch)
- Static: MISSED (GCC-API contract)

Root cause — gcc_hell.cpp:306-310 (build_spec_function):
```cpp
if (token.second) {                              // token is a format specifier (%d)
    tree spec_param = gimple_call_arg(printf_stmt,
            pf.fmt_pos + cur_spec);              // reads arg at fmt_pos+cur_spec
    args.push_back(TREE_TYPE(spec_param));       // :309 TREE_TYPE(NULL/OOB) -> segfault
```
The plugin reads one call argument per format specifier via gimple_call_arg()
WITHOUT checking gimple_call_num_args(). When the format has more specifiers
than the call has arguments, the index is out of range -> segfault. GCC only
WARNS about the mismatch (-Wformat); the plugin turns it into a crash.

Triggers (both dedup to :309): printf("%d %d",1) [2 specs,1 arg];
printf("%d") [1 spec,0 args]. => 1 distinct bug, 2 triggers.

Static backtrack: cppcheck NOT flagged; g++ -Wall NOT flagged. Missing bounds
check against a GCC API contract (index must be < gimple_call_num_args).
2x2: CONFIRMED + STATICALLY-MISSED.

===============================================================================
# BUG 4 — funcp_encrypt
===============================================================================
- Plugin: funcp-encrypt (compiled_plugin), g++-10 x86_64
- Crash: `internal compiler error: in pointer_to_record_contains_funcp_p, at funcp-encrypt.cc:288`
- Trace: :288 -> prop_finalize :362 -> funcp_pass::execute :433
- Trigger: compiling std::allocator<char> (ordinary C++ stdlib type), no args
- Class: LOGIC DEFECT (wrong assumption about C++ TYPE_FIELDS contents)
- Static: MISSED (reachable assert)

Root cause — pointer_to_record_contains_funcp_p:
```cpp
for (tree fld = TYPE_FIELDS (TREE_TYPE (type)); fld; fld = DECL_CHAIN (fld)) {
    gcc_assert (TREE_CODE (fld) == FIELD_DECL);   // fires on non-FIELD_DECL
    ...
}
```
The loop asserts EVERY entry in a record's TYPE_FIELDS chain is a FIELD_DECL.
For C++ class types, TYPE_FIELDS also contains TYPE_DECL, FUNCTION_DECL (member
functions), USING_DECL, static VAR_DECL, etc. Compiling any such type reaches a
non-FIELD_DECL entry -> assert fires -> ICE. Correct code: skip non-fields
(`if (TREE_CODE(fld) != FIELD_DECL) continue;`). Crashes on ordinary C++ with
no special args.

Note: source copies on hand were INSTRUMENTED (line numbers shifted); the body
was verified by function name; :288 to be confirmed against original committed
source.

Static backtrack: cppcheck NOT flagged; g++ -Wall NOT flagged.
2x2: CONFIRMED + STATICALLY-MISSED.

===============================================================================
# BUG 5 — gcc_assert_introspect
===============================================================================
- Plugin: gcc_assert_introspect, gcc-10 10.5.0 (C compiler)
- Crash: `internal compiler error: in get_format_for_expr, at plugin.c:498` -> gcc_unreachable() at :521
- Trace: get_format_for_expr:498 -> make_decl_subexpression_repr:712 ->
  make_subexpressions_repr:802 -> make_conditional_expr_repr:904/900 ->
  make_assert_failed_body:992 -> patch_assert:1041 -> maybe_patch_statement:1062
  -> iterate_function_body:1099/1086 -> pre_genericize_callback:1113
- Plugin's own message before crash: "unhandled integer type!"
- Class: LOGIC DEFECT (incomplete type dispatch)
- Static: MISSED
- NOTE: first run into g++ was a load failure (toolchain mismatch, EXCLUDED);
  re-run under gcc (the plugin's intended C front-end) produced this real ICE.

Root cause — get_format_for_expr (integer branch): matches integer types by a
hardcoded name list (int, unsigned int, long int, ...) then by size {1,2,4,8}.
An integral type matching neither (e.g. __int128, _BitInt(N), unusual enum)
prints "unhandled integer type!" and falls through to gcc_unreachable() at
:521 -> ICE. Crashes on valid C, plugin used correctly.

Static backtrack: cppcheck NOT flagged; g++ -Wall NOT flagged. Incomplete case
coverage reaching gcc_unreachable needs knowledge of the set of C integer
types. 2x2: CONFIRMED + STATICALLY-MISSED.

===============================================================================
# BUG 6 — static_analyzer
===============================================================================
- Plugin: static_analyzer (Static-analyzer-in-gccplugin), g++ 13.3.0 x86_64
- Crash: `internal compiler error: Illegal instruction` (SIGILL)
- Trace: fprintf2 (unit.h:293) <- PointerConstraint (Algorithm.h:357) <-
  detect:191 <- execute_detect (gcc_plugin.c:95) <- execute:118
- Class: LOGIC DEFECT (missing return in non-void function)
- Static: CAUGHT

Root cause — unit.h, fprintf2:
```c
int fprintf2(FILE *stream, const char *format, ...)   // declared int (non-void)
{
    if (!debugoutput)
        return 0;                                       // the ONLY return
    va_list ap; va_start(ap, format);
    vfprintf(stream, format, ap);
    va_end(ap);
    fflush(fp);
}                                                       // FALLS OFF END, no return
```
When debugoutput is true (run passed debugmod=1), control takes the vfprintf
path and falls off the end of a non-void function -> UB. At -O0 this manifested
as SIGILL (corrupted return, hence the unusual "Illegal instruction" rather than
segfault). Same defect CLASS as DFED.

Triggers (ALL dedup to fprintf2:293): bug_found _1/_2/_4/_6 via
PointerConstraint:357; _5 via walk_function_path:767 -> dump_fucntion:989 ->
PointerConstraint:391 (different caller, same crashing function).
=> 1 distinct bug, 5 triggers.

Static backtrack: g++ -Wall -> "control reaches end of non-void function
[-Wreturn-type]" — FLAGGED; cppcheck -> "missing return statement
[missingReturn]" — FLAGGED. 2x2: CONFIRMED + STATICALLY-FLAGGED.

===============================================================================
# BUG 7 — SecRetAddress
===============================================================================
- Plugin: SecRetAddress (compiled_plugin), g++ 13.3.0 x86_64
- Crash: `Segmentation fault` in single_pred_edge (GCC header), called by plugin
- Trace: single_pred_edge (basic-block.h:343) <- single_pred (:361) <-
  instrument_exit (plugin.cpp:153) <- instrument_functions:207 <- execute:241
- Trigger: function victim() with multiple exit predecessors; default args
- Class: LOGIC DEFECT (GCC-API precondition violation)
- Static: MISSED

Root cause — plugin.cpp:153 (instrument_exit):
```cpp
bb = single_pred(EXIT_BLOCK_PTR_FOR_FN(fun));   // :153 CRASH
```
single_pred() has a HARD PRECONDITION: the block must have exactly ONE
predecessor. A function whose EXIT block has multiple predecessors (multiple
return paths) violates this -> single_pred_edge dereferences invalid data ->
segfault. Correct code: check single_pred_p() first or iterate predecessor
edges. Crashes on ordinary C++ with multiple returns, plugin used with defaults.

Static backtrack: cppcheck NOT flagged; g++ -Wall NOT flagged. GCC-API
precondition not modeled by static tools. Same CATEGORY as cprintf.
2x2: CONFIRMED + STATICALLY-MISSED.

===============================================================================
# OPTIONAL STRENGTHENING (not blocking)
===============================================================================
- DFED: capture exact `arm-none-eabi-g++ --version` and 3/3 reproducibility.
- funcp_encrypt: confirm :288 against original (uninstrumented) committed source.
- cprintf: run-1 origin already confirmed by run-2 full plugin frames.
- Check whether any "2-bug" plugin has a genuinely DIFFERENT second crash site
  (so far none do — all deduplicate to a single defect each).
