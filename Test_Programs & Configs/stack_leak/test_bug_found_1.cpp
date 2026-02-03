#include <stdio.h>
#include <stdlib.h>
#include <setjmp.h>

#define MAX_ALLOCA_DEPTH 30
#define LARGE_FRAME_SIZE 16384

jmp_buf stress_jb;

void deep_alloca(int depth) {
    if (depth > 0) {
        char *buf1 = (char*)alloca(1024);
        char *buf2 = (char*)alloca(2048);
        
        buf1[0] = buf2[0] = (char)depth;
        
        if (depth % 7 == 0) longjmp(stress_jb, 1);
        else deep_alloca(depth - 1);
    }
}

void huge_frame(void) {
    char massive[LARGE_FRAME_SIZE];
    
    for (int i = 0; i < LARGE_FRAME_SIZE; i += 128)
        massive[i] = (char)i;
    
    for (int j = 0; j < 32; j++)
        alloca(512);
}

static inline int inline_leaf(int x) {
    return x * 2;
}

__attribute__((noinline)) int noinline_leaf(int x) {
    return x + 1;
}

void _paravirt_stress_1(void) {
    alloca(256);
}

void _paravirt_stress_2(int x) {
    if (x > 0) _paravirt_stress_1();
}

void complex_cfg(int flag) {
    char *buf1 = NULL, *buf2 = NULL;
    
    if (flag & 1) {
        buf1 = (char*)alloca(1024);
        if (flag & 2) goto after2;
    }
    
    buf2 = (char*)alloca(2048);
    
after2:
    if (flag & 4) alloca(4096);
    
    if (flag & 8) goto end;
    alloca(512);
    
end:
    (void)buf1; (void)buf2;
}

void setjmp_alloca(void) {
    int val = setjmp(stress_jb);
    
    if (val == 0) {
        char *buf = (char*)alloca(4096);
        longjmp(stress_jb, 1);
    } else {
        alloca(2048);
    }
}

void fnptr_stress(void) {
    void (*fn_ptr)(void);
    
    fn_ptr = (void(*)(void))alloca(128);
    alloca(256);
    fn_ptr = (void(*)(void))alloca(512);
}

void ultimate_stress(int depth) {
    char huge[8192];
    char *buf1 = (char*)alloca(4096);
    
    if (depth > 0) {
        if (setjmp(stress_jb) == 0) {
            ultimate_stress(depth - 1);
            longjmp(stress_jb, 1);
        }
    }
    
    huge[0] = buf1[0] = (char)depth;
    
    __asm__ volatile ("" ::: "memory");
}

int main(void) {
    deep_alloca(MAX_ALLOCA_DEPTH);
    huge_frame();
    printf("Leaf test: %d\n", noinline_leaf(42));
    _paravirt_stress_2(1);
    complex_cfg(15);
    setjmp_alloca();
    fnptr_stress();
    ultimate_stress(5);
    
    printf("stackleak stress test complete\n");
    return 0;
}
