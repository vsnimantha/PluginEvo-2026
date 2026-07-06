# gcc_assert_introspect — first run EXCLUDED, but SUPERSEDED

The FIRST run (into g++/cc1plus) failed to load with an undefined symbol
(c_build_function_call_vec) — a toolchain mismatch, not a bug.

HOWEVER: re-running under gcc-10 (the C compiler, the plugin's intended
front-end) produced a GENUINE ICE. See gcc_assert_introspect_bug1_record.md.
=> This plugin now has 1 CONFIRMED distinct bug.

Lesson for the paper: the g++ load failure was correctly NOT counted as a bug;
only the proper C-frontend run revealed the real defect. Good example of the
classification discipline avoiding both a false positive (the load failure) and
a false negative (missing the real bug).
