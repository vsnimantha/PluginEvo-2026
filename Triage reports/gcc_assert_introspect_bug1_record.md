# Confirmed Bug Record: gcc_assert_introspect #1

## IMPORTANT: supersedes earlier EXCLUDED entry
The first run loaded the plugin into g++ (cc1plus) and failed with an undefined
symbol (toolchain mismatch, correctly excluded). This run uses gcc-10 (the C
compiler, cc1) — the plugin's intended front-end — where it LOADS, RUNS, and
produces a genuine ICE. This is a real, distinct plugin bug.

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | gcc_assert_introspect (compiled_plugin), gcc-10 10.5.0 (C compiler) |
| Crash site | get_format_for_expr, plugin.c:498 -> gcc_unreachable() at :521 |
| Plugin's own message | "unhandled integer type!" printed just before the ICE |
| Trigger | assert(...) over an integer type not matched by name or size {1,2,4,8} |
| Class | LOGIC DEFECT — incomplete type dispatch reaching gcc_unreachable() |
| Origin | **PLUGIN — CONFIRMED BY TRACE** (13 plugin frames, all in plugin.c) |
| Static-detectable | NO (needs knowledge of which integer types exist) |
| plugin args | none (default) |

## Console trace (abridged; full chain in log)
```
assert_introspect loaded, compiled for GCC 10.5.0
unhandled integer type!
test_bug_found_1.1.c: In function 'main':
internal compiler error: in get_format_for_expr, at plugin.c:498
0x... get_format_for_expr        plugin.c:498
0x... make_decl_subexpression_repr plugin.c:712
0x... make_subexpressions_repr   plugin.c:802
0x... make_conditional_expr_repr plugin.c:904 / :900
0x... make_assert_failed_body    plugin.c:992
0x... patch_assert               plugin.c:1041
0x... maybe_patch_statement      plugin.c:1062
0x... iterate_function_body      plugin.c:1099/:1086
0x... pre_genericize_callback    plugin.c:1113
```
Command: gcc-10 -c -O0 -fplugin=compiled_plugin.so -g test_bug_found_1.1.c

## Root cause in source — get_format_for_expr (plugin.c ~482-521)
```c
} else if (INTEGRAL_TYPE_P(type)) {
    if (NULL_TREE != TYPE_IDENTIFIER(type)) {
        const char *type_name = IDENTIFIER_POINTER(TYPE_IDENTIFIER(type));
        if      (!strcmp(type_name,"int"))               return "%d";
        else if (!strcmp(type_name,"unsigned int"))      return "%u";
        else if (!strcmp(type_name,"long int"))          return "%ld";
        else if (!strcmp(type_name,"long unsigned int")) return "%lu";
        else if (!strcmp(type_name,"short int"))         return "%hd";
        else if (!strcmp(type_name,"short unsigned int"))return "%hu";
    }
    // fallback by size:
    const int is_unsigned = TYPE_UNSIGNED(type);
    switch (TREE_INT_CST_LOW(TYPE_SIZE_UNIT(type))) {   // <-- :498
    case 1: return is_unsigned ? PRIu8  : PRId8;
    case 2: return is_unsigned ? PRIu16 : PRId16;
    case 4: return is_unsigned ? PRIu32 : PRId32;
    case 8: return is_unsigned ? PRIu64 : PRId64;
    }
    printf("unhandled integer type!\n");                // :505 — no return
} else if (SCALAR_FLOAT_TYPE_P(type)) { ... }
gcc_unreachable();                                       // :521 — ICE lands here
```
An integral type whose NAME isn't in the hardcoded list AND whose size isn't
1/2/4/8 bytes (e.g. __int128, _BitInt(N), or an enum with an unusual underlying
type) matches no case, prints "unhandled integer type!", and falls through to
gcc_unreachable() -> ICE. The plugin used correctly, on valid C, crashes.

## Classification
LOGIC DEFECT — incomplete type dispatch. A THIRD assert-family variant:
  - stackleak: gcc_assert on config (arch)
  - funcp:     gcc_assert on tree-code (C++ fields)
  - gai:       gcc_unreachable via incomplete integer-type coverage
All three are compiler-domain "this shouldn't happen" checks that DO happen.

## Phase 2 — Static Backtrack
| Tool | Result |
|---|---|
| cppcheck | NOT flagged |
| g++ -Wall -Wextra | NOT flagged |
Incomplete case coverage reaching gcc_unreachable() needs knowledge of the set
of possible C integer types; static tools don't model that. CONFIRMED + STATICALLY-MISSED.

## To finalize
The exact triggering integer type would be confirmed from test_bug_found_1.1.c
(likely __int128 / _BitInt / unusual enum). Worth noting in the paper which type.
