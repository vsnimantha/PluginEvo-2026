# Confirmed Bug Record: funcp_encrypt #1

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | funcp-encrypt (compiled_plugin), g++-10 x86_64 |
| Crash site | pointer_to_record_contains_funcp_p, funcp-encrypt.cc:288 |
| Chain | :288 -> prop_finalize :362 -> funcp_pass::execute :433 |
| Trigger | compiling std::allocator<char>::allocator() (ordinary C++ stdlib type) |
| Class | LOGIC DEFECT — wrong assumption about C++ TYPE_FIELDS contents |
| Origin | **PLUGIN — CONFIRMED BY TRACE** (all frames in funcp-encrypt.cc) |
| Static-detectable | NO (reachable gcc_assert on tree-code; needs GCC domain knowledge) |
| plugin args | none (default) |

## Console trace
```
during GIMPLE pass: funcp_plugin
test_bug_found_1.cpp: In constructor 'std::allocator<...>::allocator() [with _Tp = char]':
test_bug_found_1.cpp:115:1: internal compiler error: in pointer_to_record_contains_funcp_p, at funcp-encrypt.cc:288
0x...  pointer_to_record_contains_funcp_p   funcp-encrypt.cc:288
0x...  prop_finalize                        funcp-encrypt.cc:362
0x...  funcp_pass::execute(function*)       funcp-encrypt.cc:433
```
Command: g++-10 -fplugin=compiled_plugin.so -g test_bug_found_1.cpp

## Root cause in source (function body; real line ~288 is the gcc_assert)
```cpp
static bool
pointer_to_record_contains_funcp_p (tree type)
{
  if (TREE_CODE (type) != POINTER_TYPE
      || TREE_CODE (TREE_TYPE (type)) != RECORD_TYPE)
    return false;

  bool has_funcp = false;
  for (tree fld = TYPE_FIELDS (TREE_TYPE (type)); fld; fld = DECL_CHAIN (fld))
    {
      gcc_assert (TREE_CODE (fld) == FIELD_DECL);   // <-- CRASH: fires on non-FIELD_DECL
      tree fld_type = TREE_TYPE (fld);
      if (TREE_CODE (fld_type) == POINTER_TYPE
          && TREE_CODE (TREE_TYPE (fld_type)) == FUNCTION_TYPE)
        { has_funcp = true; break; }
    }
  return has_funcp;
}
```
The loop walks a record's TYPE_FIELDS chain and asserts EVERY entry is a
FIELD_DECL. For C++ class/struct types, TYPE_FIELDS also contains TYPE_DECL,
FUNCTION_DECL (member functions), USING_DECL, static VAR_DECL, etc. Compiling
any such C++ type (here std::allocator<char>) reaches a non-FIELD_DECL entry ->
gcc_assert fires -> ICE. Correct code would skip non-fields:
`if (TREE_CODE(fld) != FIELD_DECL) continue;`

## Classification
LOGIC DEFECT (wrong assumption about the tree structure). Crashes on ORDINARY
C++ code with NO special plugin arguments — stronger than stackleak. The plugin
was likely written/tested against C records (where TYPE_FIELDS is all fields)
and never hardened for C++ class layouts.

## Phase 2 — Static Backtrack
| Tool | Result |
|---|---|
| cppcheck | NOT flagged |
| g++ -Wall -Wextra | NOT flagged |
Reachable gcc_assert on a tree-code assumption; static tools don't model which
TREE_CODEs can appear in a TYPE_FIELDS chain. 2x2 cell: CONFIRMED + STATICALLY-MISSED.

## Note on source line
Available funcp-encrypt.cc copies on hand are INSTRUMENTED (line numbers shifted
by injected logging). The function body above is verbatim (log calls elided);
the gcc_assert is the crash line reported as :288 in the uninstrumented plugin.
To lock the exact line, confirm against the original committed funcp-encrypt.cc.
