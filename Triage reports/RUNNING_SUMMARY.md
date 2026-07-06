# ICE Confirmation — FINAL SUMMARY (corpus complete: 7/7 plugins tested)

## CONFIRMED distinct bugs: 7 (all root-caused, origin PLUGIN, trace-confirmed)
| # | Plugin | Root cause | Class | Static? | Triggers |
|---|---|---|---|---|---|
| 1 | DFED | DFED_Plugin.cpp:127 missing return -> :167 strlen segfault | Missing return | YES | 1 |
| 2 | stack_leak | stackleak_plugin.c:131 gcc_assert(build_for_x86) | Reachable assert (config) | NO | 5 |
| 3 | cprintf | gcc_hell.cpp:309 gimple_call_arg OOB | GCC-API contract | NO | 2 |
| 4 | funcp_encrypt | funcp-encrypt.cc:288 gcc_assert(TREE_CODE==FIELD_DECL) | Reachable assert (C++ fields) | NO | 1 |
| 5 | gcc_assert_introspect | plugin.c:498->521 gcc_unreachable, incomplete int-type dispatch | Incomplete dispatch | NO | 1 |
| 6 | static_analyzer | unit.h:293 fprintf2 missing return -> SIGILL | Missing return | YES | 5 |
| 7 | SecRetAddress | plugin.cpp:153 single_pred(EXIT_BLOCK) no single-pred check | GCC-API contract | NO | 1 |

## Static-detectability split — 2 CAUGHT / 5 MISSED
- CAUGHT (2): DFED, static_analyzer — BOTH missing-return in non-void fn
  (-Wreturn-type, part of default -Wall; also cppcheck missingReturn).
- MISSED (5): stackleak, funcp, gcc_assert_introspect (reachable assert /
  gcc_unreachable), cprintf, SecRetAddress (GCC-API contract violations).

## Bug taxonomy (7 bugs, 4 classes)
A. Missing return (non-void) ......... DFED, static_analyzer ......... CAUGHT (2)
B. GCC-API contract violation ........ cprintf, SecRetAddress ......... MISSED (2)
C. Reachable gcc_assert (wrong assumption) . stackleak, funcp_encrypt .. MISSED (2)
D. gcc_unreachable / incomplete dispatch ... gcc_assert_introspect ..... MISSED (1)

## THE KEY FINDING (defensible, review-proof)
Of 7 confirmed GCC-plugin crashes, only 2 were catchable by standard static
analysis — and BOTH were the same generic C++ defect (missing return), flagged
by a default compiler warning. The other 5 are GCC-plugin-DOMAIN defects:
- API-contract violations (gimple_call_arg bounds; single_pred precondition)
- Reachable asserts / gcc_unreachable encoding assumptions that don't hold
  (target arch; C++ class field layout; unusual integer types)
These require compiler/GIMPLE-domain reasoning that generic static tools
(cppcheck, -Wall/-Wextra) do not perform. => Standard static analysis is
necessary-but-insufficient for GCC plugins; dynamic activation testing finds
the domain-specific crashes it misses.

## Deduplication — honest counting
| Plugin | Raw crash runs | Distinct bugs |
|---|---|---|
| DFED | 1 | 1 |
| stack_leak | 6 | 1 (all :131) |
| cprintf | 2 | 1 (all :309) |
| funcp_encrypt | 1 | 1 |
| gcc_assert_introspect | 2 | 1 (1 excluded g++ load-fail + 1 real ICE) |
| static_analyzer | 5 | 1 (all fprintf2:293) |
| SecRetAddress | 1 | 1 |
| **TOTAL** | **18** | **7** |

## Count vs PluginEvo headline
- PluginEvo headline: 10 bugs / 7 plugins.
- Honest, deduplicated: **7 distinct bugs / 7 plugins** (one genuine defect each).
- The gap: stackleak, cprintf, static_analyzer were each counted as 2, but each
  has only 1 distinct defect (multiple trigger programs -> same crash site).
  18 raw crash runs deduplicate to 7 distinct bugs.
- Every bug: plugin origin (trace), root cause in source, static-detectability
  determined. This is the number that survives a reviewer re-running the data.

## Excluded (correctly, not counted)
- gcc_assert_introspect first run: g++ load failure (C-frontend plugin into
  cc1plus) — toolchain mismatch, not a bug. The proper gcc run gave the real bug.

## Loose ends (optional strengthening, not required)
- DFED: exact arm-none-eabi-g++ version string + 3/3 reproducibility.
- funcp_encrypt: confirm :288 against original (uninstrumented) committed source.
- cprintf run 1 origin: already confirmed by run 2's full plugin frames.
