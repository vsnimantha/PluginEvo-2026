// Test cases for all instrumentation scenarios
#include <stdio.h>

// 1. Basic attribute cases
__attribute__((instrument_function)) void attr_func1() {}
void __attribute__((instrument_function)) attr_func2() {}
__attribute__((instrument_function, noinline)) void attr_func_with_other_attrs() {}

// 2. Functions in different files (create separate files)
void file_match_func(); // Defined in file_match.c
void no_match_func();   // Defined in no_match.c

// 3. Function name variations
void exact_match_func() {}
void partial_match_func() {}
void EXACT_MATCH_FUNC() {} // Case sensitivity test
void prefix_match_function() {}
void suffix_match_function() {}

// 4. Edge cases
static void static_func() {} // Static functions
inline void inline_func() {} // Inline functions
void __attribute__((weak)) weak_func() {} // Weak symbols

// 5. Special characters in names
void func_with_underscores() {}
void FuncWithMixedCase() {}
void func_with_numbers123() {}

int main() {
    attr_func1();
    attr_func2();
    attr_func_with_other_attrs();
    file_match_func();
    no_match_func();
    exact_match_func();
    partial_match_func();
    EXACT_MATCH_FUNC();
    prefix_match_function();
    suffix_match_function();
    static_func();
    inline_func();
    weak_func();
    func_with_underscores();
    FuncWithMixedCase();
    func_with_numbers123();
    return 0;
}