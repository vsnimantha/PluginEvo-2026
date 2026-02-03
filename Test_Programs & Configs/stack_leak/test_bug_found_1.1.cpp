#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <setjmp.h>

#define FRAME_SIZE_LIMIT 32768
#define ITERATIONS 1000

jmp_buf phase2_jb;

void frame_size_edge(size_t size) {
    char buf[size];
    for (size_t i = 0; i < size / 64; i++)
        buf[i * 64] = (char)i;
    
    alloca(size / 8);
}

static __attribute__((noinline, cold)) int leaf_confusion_1(int x) {
    return x * 3;
}

static inline int leaf_confusion_2(int x) {
    char *tmp = (char*)alloca(64);
    tmp[0] = 1;
    return leaf_confusion_1(x);
}

void __pv_some_op_stress(void) { 
    char *tmp = (char*)alloca(128);
    tmp[0] = 1;
}

void pv_ops_stress_foo(void) { 
    char *tmp = (char*)alloca(256);
    tmp[0] = 2;
}

void _pv_foo_bar_baz(void) { 
    char *tmp = (char*)alloca(512);
    tmp[0] = 3;
}

void cgraph_stress_helper(int level) {
    if (level > 0) {
        char *buf = (char*)alloca(1024);
        buf[0] = (char)level;
        cgraph_stress_helper(level - 1);
        cgraph_stress_helper(level - 2);
    }
}

void rtl_stress(void) {
    char huge[8192];
    __asm__ volatile ("" ::: "memory");
    
    char *tmp = (char*)alloca(1024);
    huge[0] = tmp[0] = 65;
}

void cleanup_stress(void) {
    char *buf1 = (char*)alloca(4096);
    char *buf2 = (char*)alloca(2048);
    
    if (setjmp(phase2_jb) == 0) {
        longjmp(phase2_jb, 1);
    }
}

void zero_size_stress(void) {
    char *zero = (char*)alloca(0);
    (void)zero;
}

void callgraph_massive(int depth) {
    if (depth < 25) {
        char *tmp = (char*)alloca(128);
        tmp[0] = (char)depth;
        callgraph_massive(depth + 1);
    }
}

int main(void) {
    printf("=== Stackleak Phase 2 Stress Test ===\n");
    
    frame_size_edge(FRAME_SIZE_LIMIT - 64);
    frame_size_edge(FRAME_SIZE_LIMIT + 64);
    
    printf("Leaf confusion: %d\n", leaf_confusion_2(100));
    
    __pv_some_op_stress();
    pv_ops_stress_foo();
    _pv_foo_bar_baz();
    
    cgraph_stress_helper(8);
    rtl_stress();
    cleanup_stress();
    zero_size_stress();
    callgraph_massive(0);
    
    printf("Phase 2 complete - check for new ICEs!\n");
    return 0;
}
