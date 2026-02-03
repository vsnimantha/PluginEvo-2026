#include <stdio.h>
#include <stdlib.h>

#define RECURSION_DEPTH 15
#define INLINE_CALLS 1000

static __attribute__((noinline, cold, noclone)) int pure_leaf_1(int x) {
    return x * 7 + 13;
}

static inline int pure_leaf_2(int x) {
    return pure_leaf_1(x + 1);
}

static __attribute__((noinline)) int fake_leaf_alloc(int x) {
    char *tmp = (char*)alloca(64);
    tmp[0] = 1;
    return x;
}

void callgraph_explosion(int level) {
    if (level > 0) {
        char *buf = (char*)alloca(128);
        buf[0] = (char)level;
        callgraph_explosion(level - 1);
        callgraph_explosion(level - 1);
    }
}

void __kvm_handle_stress(void) { alloca(128); }
void pvops_mm_stress(void) { alloca(256); }
void _pv_lazy_stress_ops(void) { alloca(512); }

static inline void inline_materialize(void) {
    alloca(256);
}

void force_inline_outlined(void) {
    inline_materialize();
}

static void static_addr_taken(void) {
    alloca(128);
}

void take_static_addr(void) {
    typeof(static_addr_taken) *fnptr = static_addr_taken;
    (void)fnptr;
}

__attribute__((constructor(101))) void ctor_stress_low(void) {
    alloca(512);
}

__attribute__((constructor(200))) void ctor_stress_high(void) {
    alloca(1024);
}

int main(void) {
    printf("=== Stress Test #3: cgraph/Leaf Detection ===\n");
    
    printf("Pure leaf: %d\n", pure_leaf_2(42));
    printf("Fake leaf: %d\n", fake_leaf_alloc(42));
    
    callgraph_explosion(RECURSION_DEPTH);
    
    __kvm_handle_stress();
    pvops_mm_stress();
    _pv_lazy_stress_ops();
    
    force_inline_outlined();
    
    take_static_addr();
    
    printf("Test #3 complete\n");
    return 0;
}
