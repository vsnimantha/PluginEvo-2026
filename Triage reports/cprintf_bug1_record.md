# Confirmed Bug Record: cprintf #1  (triggers: too-few-args family)

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | cprintf (compiled_plugin), GCC 13 x86_64 |
| Root-cause function | build_spec_function, gcc_hell.cpp:309 |
| Class | LOGIC DEFECT — unchecked gimple_call_arg (format/arg-count mismatch) |
| Origin | **PLUGIN — CONFIRMED BY TRACE** (run 2 shows full plugin frames) |
| Static-detectable | NO (API-contract bounds check; cppcheck & -Wall miss it) |

### Triggers (both dedup to this one bug — same crash line 309)
| Run | Program / function | printf call | specs vs args |
|---|---|---|---|
| 1 | test_cprintf_bug_found_1.cpp / test_arg_mismatch_few | printf("few: x=%d y=%d\n", 1) | 2 specs, 1 arg |
| 2 | test_cprintf_bug_found_2.cpp / test_zero_args | printf("zero: x=%d\n") | 1 spec, 0 args |

Both read arg (fmt_pos + cur_spec) when the call lacks that argument.

## Console trace (run 2 — the one with full plugin frames)
```
during GIMPLE pass: cprintf_walk
test_cprintf_bug_found_2.cpp:45:27: warning: format '%d' expects a matching 'int' argument [-Wformat=]
   45 |     std::printf("zero: x=%d\n");
test_cprintf_bug_found_2.cpp:39:6: internal compiler error: Segmentation fault
   39 | void test_zero_args() {
0x...  build_spec_function        gcc_hell.cpp:309
0x...  insert_spec_func           gcc_hell.cpp:377
0x...  handle_printfunc           gcc_hell.cpp:287
0x...  cprintf_pass::callback_stmt gcc_hell.cpp:163
0x...  cprintf_pass::execute      gcc_hell.cpp:55
0x...  __libc_start_call_main
```
(Run 1 trace showed only libc frames; run 2 confirms plugin origin.)

## Root cause in source — gcc_hell.cpp:306-310 (build_spec_function)
```cpp
    if (token.second) {                              // token is a format specifier (e.g. %d)
        tree spec_param = gimple_call_arg(printf_stmt,
                pf.fmt_pos + cur_spec);              // <-- :307-308 reads arg at fmt_pos+cur_spec
        args.push_back(TREE_TYPE(spec_param));       // <-- :309 CRASH: TREE_TYPE(NULL/OOB) segfaults
        func_name = pf.spec_to_func.at(token.first);
    } else {
```
The plugin reads ONE call argument per format specifier via gimple_call_arg()
WITHOUT checking gimple_call_num_args(printf_stmt). When the format has more
specifiers than the call has arguments, the index (fmt_pos + cur_spec) is out
of range -> gimple_call_arg returns NULL / reads OOB -> TREE_TYPE() deref ->
segfault at line 309. GCC only WARNS about the mismatch (-Wformat); the plugin
turns that into a compiler crash.

## Phase 2 — Static Backtrack
| Tool | Result |
|---|---|
| cppcheck | NOT flagged (only unrelated unusedStructMember note) |
| g++ -Wall -Wextra | NOT flagged |
Reason: missing bounds check against a GCC API contract (gimple_call_arg index
must be < gimple_call_num_args). Static tools don't model that contract.
2x2 cell: CONFIRMED + STATICALLY-MISSED.

## Count note
cprintf claimed 2 bugs; both observed crashes are the SAME defect at
build_spec_function:309 (too-few-args, reached with 1 arg and with 0 args).
Honest count for cprintf = 1 distinct bug, 2 triggers.
A genuinely distinct 2nd cprintf bug would need a DIFFERENT crash site.
