# Confirmed Bug Record: static_analyzer #1

## Phase 1 — ICE Confirmation
| Field | Value |
|---|---|
| Plugin | static_analyzer (Static-analyzer-in-gccplugin), g++ 13.3.0 x86_64 |
| Crash signal | internal compiler error: Illegal instruction (SIGILL) |
| Crash site | fprintf2, unit.h (missing return), called from PointerConstraint Algorithm.h:357 |
| Pass | IPA pass: static_analyzer |
| Trigger | test_static_analyser_bug_found.cpp (new/delete + arr[i]); args incl debugmod=1 |
| Class | LOGIC DEFECT — missing return in non-void function (same class as DFED) |
| Origin | **PLUGIN — CONFIRMED BY TRACE** (all frames in plugin files) |
| Static-detectable | YES (-Wreturn-type in -Wall; cppcheck missingReturn) |

## Console trace
```
during IPA pass: static_analyzer
test_static_analyser_bug_found.cpp:37:1: internal compiler error: Illegal instruction
0x...  fprintf2(_IO_FILE*, char const*, ...)   unit.h:293
0x...  PointerConstraint(ptb*, ptb*)           Algorithm.h:357
0x...  detect(plugin_argument*, int)           Algorithm.h:191
0x...  execute_detect                          gcc_plugin.c:95
0x...  execute                                 gcc_plugin.c:118
```

## Root cause in source — unit.h, fprintf2
```c
int fprintf2(FILE *stream, const char *format, ...)   // declared int (non-void)
{
	if (!debugoutput)
		return 0;                                       // the ONLY return
	va_list ap;
	va_start(ap, format);
	vfprintf(stream, format, ap);
	va_end(ap);
	fflush(fp);
}                                                       // <-- FALLS OFF END, no return
```
When debugoutput is true (the run passed debugmod=1), control takes the vfprintf
path and falls off the end of a non-void function -> undefined behaviour. At the
call site Algorithm.h:357 (the 3rd fprintf2, right after "program slicing stmt
count"), the UB manifested as SIGILL (corrupted return, not a null-deref — which
explains the unusual "Illegal instruction" signal).

## Correction to earlier hypothesis
The initial (source-less) note hypothesised a vararg/format mismatch because the
crash was inside a vararg function. That was WRONG. With source, the real cause
is a MISSING RETURN — same defect class as DFED, not a format bug. (Recorded here
to keep the reasoning honest: the hypothesis was flagged as such and is now corrected.)

## Classification
LOGIC DEFECT — missing return in non-void function. Manifests when debugmod=1
(a normal, documented plugin argument). Same root-cause CLASS as DFED bug A.

## Phase 2 — Static Backtrack
| Tool | Result |
|---|---|
| g++ -Wall -Wextra | FLAGGED: "control reaches end of non-void function [-Wreturn-type]" |
| cppcheck | FLAGGED: "missing return statement [missingReturn]" |
BOTH flag it. 2x2 cell: CONFIRMED + STATICALLY-FLAGGED (2nd such, with DFED).

## Count note
static_analyzer claimed 2 bugs; this is #1 (fprintf2 missing return, via
Algorithm.h:357). A distinct 2nd bug needs a DIFFERENT crash site. Note: fprintf2
is called in MANY places, so a "2nd bug" that is just another fprintf2 call
crashing is the SAME defect and deduplicates to this one.

## ADDITIONAL RUNS (_2, _4, _5, _6) — ALL SAME BUG (dedup)
| Run | Program | Leaf frame | Path | Verdict |
|---|---|---|---|---|
| _1 | test_static_analyser_bug_found.cpp | fprintf2 unit.h:293 | PointerConstraint Algorithm.h:357 | bug #1 |
| _2 | ..._2.cpp | fprintf2 unit.h:293 | PointerConstraint Algorithm.h:357 | SAME |
| _4 | ..._4.cpp | fprintf2 unit.h:293 | PointerConstraint Algorithm.h:357 | SAME |
| _5 | ..._5.cpp | fprintf2 unit.h:293 | walk_function_path trace.h:767 -> dump_fucntion:989 -> PointerConstraint:391 | SAME (diff caller) |
| _6 | ..._6.cpp | fprintf2 unit.h:293 | PointerConstraint Algorithm.h:357 | SAME |

ALL crash in the SAME leaf function: fprintf2 at unit.h:293 (missing return).
_5 reaches it via a different caller chain (walk_function_path/dump_fucntion,
PointerConstraint:391 instead of :357), but the CRASHING FUNCTION and DEFECT are
identical. fprintf2 is called in many places; any call crashes once debugmod=1
routes control to the fall-off-the-end path.

DEDUP VERDICT: static_analyzer = 1 distinct bug (fprintf2 missing return),
5+ trigger programs / call sites. NOT 2, NOT 5.
The PluginEvo "2 bugs for static_analyzer" is not supported by these traces —
every crash is the same fprintf2 defect.
